from __future__ import annotations

import importlib
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

external_ops = importlib.import_module("chef.external")


class ChefExternalTests(unittest.TestCase):
    def test_sync_external_installs_codex_wrapper_skill(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            home = root / "home"
            snapshot = external_ops.Snapshot(
                cache_dir=project / ".chef" / "vendor" / "sample-skill",
                material_kind="text",
                text="Imported skill text",
            )
            snapshot.cache_dir.mkdir(parents=True)
            item = {
                "id": "sample-skill",
                "name": "Sample Skill",
                "kind": "skill",
                "hosts": ["codex"],
                "install": {"method": "manual"},
                "source_url": "https://skills.example/sample-skill",
            }

            with (
                patch.object(external_ops, "fetch_snapshot", return_value=snapshot),
                patch.object(external_ops.Path, "home", return_value=home),
            ):
                result = external_ops.sync_external_items(project, "codex", [item])

            self.assertEqual(result.errors, [])
            target = home / ".codex" / "skills" / "sample-skill" / "SKILL.md"
            self.assertTrue(target.exists())
            self.assertIn("Imported skill text", target.read_text(encoding="utf-8"))

    def test_sync_external_installs_claude_plugin_when_detected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            home = root / "home"
            plugin_root = project / ".chef" / "vendor" / "sample-plugin" / "plugin-root"
            (plugin_root / ".claude-plugin").mkdir(parents=True)
            (plugin_root / ".claude-plugin" / "plugin.json").write_text(
                '{"name":"sample"}\n', encoding="utf-8"
            )
            snapshot = external_ops.Snapshot(
                cache_dir=project / ".chef" / "vendor" / "sample-plugin",
                material_kind="dir",
                material_path=plugin_root,
            )
            item = {
                "id": "sample-plugin",
                "name": "Sample Plugin",
                "kind": "plugin",
                "hosts": ["claude"],
                "install": {"method": "manual"},
                "source_url": "https://github.com/example/plugin/tree/main/plugins/sample",
            }

            with (
                patch.object(external_ops, "fetch_snapshot", return_value=snapshot),
                patch.object(external_ops.Path, "home", return_value=home),
            ):
                result = external_ops.sync_external_items(project, "claude", [item])

            self.assertEqual(result.errors, [])
            self.assertEqual(result.warnings, [])
            target = home / ".claude" / "plugins" / "local" / "sample-plugin"
            self.assertTrue((target / ".claude-plugin" / "plugin.json").exists())

    def test_sync_external_writes_codex_mcp_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            home = root / "home"
            (project / ".codex-plugin").mkdir(parents=True)
            (project / ".codex-plugin" / "plugin.json").write_text(
                '{"name":"chef","version":"0.1.0"}\n', encoding="utf-8"
            )
            snapshot = external_ops.Snapshot(
                cache_dir=project / ".chef" / "vendor" / "excel-mcp-server",
                material_kind="text",
                text="Excel MCP notes",
            )
            snapshot.cache_dir.mkdir(parents=True)
            item = {
                "id": "excel-mcp-server",
                "name": "Excel MCP Server",
                "kind": "mcp_server",
                "hosts": ["codex"],
                "install": {"method": "manual"},
                "source_url": "https://github.com/haris-musa/excel-mcp-server",
                "mcp": {"command": "uvx", "args": ["excel-mcp-server", "stdio"]},
            }

            with (
                patch.object(external_ops, "fetch_snapshot", return_value=snapshot),
                patch.object(external_ops.Path, "home", return_value=home),
            ):
                result = external_ops.sync_external_items(project, "codex", [item])

            self.assertEqual(result.errors, [])
            mcp_data = json.loads(
                (project / ".codex-plugin" / ".mcp.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                mcp_data["mcpServers"]["excel-mcp-server"],
                {"command": "uvx", "args": ["excel-mcp-server", "stdio"]},
            )
            plugin_data = json.loads(
                (project / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(plugin_data["mcpServers"], "./.mcp.json")

    def test_sync_external_falls_back_to_wrapper_on_fetch_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            home = root / "home"
            item = {
                "id": "fallback-skill",
                "name": "Fallback Skill",
                "kind": "skill",
                "hosts": ["codex"],
                "install": {"method": "manual"},
                "source_url": "https://example.com/fallback-skill",
            }

            with (
                patch.object(
                    external_ops, "fetch_snapshot", side_effect=external_ops.InstallError("boom")
                ),
                patch.object(external_ops.Path, "home", return_value=home),
            ):
                result = external_ops.sync_external_items(project, "codex", [item])

            self.assertEqual(result.errors, [])
            self.assertTrue(result.warnings)
            target = home / ".codex" / "skills" / "fallback-skill" / "SKILL.md"
            self.assertTrue(target.exists())
            self.assertIn("could not fetch upstream content", target.read_text(encoding="utf-8"))

    def test_fetch_snapshot_falls_back_from_blob_to_repo_path(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            repo_root = project / "repo-root"
            skill_dir = repo_root / "skills" / "using-git-worktrees"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Worktrees\n", encoding="utf-8")
            item = {
                "id": "using-git-worktrees",
                "name": "Using Git Worktrees",
                "kind": "skill",
                "hosts": ["codex"],
                "install": {"method": "manual"},
                "source_url": "https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees",
            }
            http_404 = urllib.error.HTTPError(
                url=item["source_url"], code=404, msg="Not Found", hdrs=None, fp=None
            )

            with (
                patch.object(external_ops, "request_bytes", side_effect=http_404),
                patch.object(external_ops, "download_repo_zip", return_value=repo_root),
            ):
                snapshot = external_ops.fetch_snapshot(project, item)

            self.assertEqual(snapshot.material_path, skill_dir)
            self.assertEqual(snapshot.material_kind, "dir")


if __name__ == "__main__":
    unittest.main()
