from __future__ import annotations

import json
import shutil
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import chef.cli as chef_cli
from chef import graphify as graphify_ops
from chef import hosts as host_install
from chef.mcp import common as mcp_common
from chef import packs as pack_ops


def run_command(func, **kwargs: object) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = func(SimpleNamespace(**kwargs))
    return code, stdout.getvalue(), stderr.getvalue()


class ChefCliTests(unittest.TestCase):
    def test_verify_respects_claude_only_projects(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(chef_cli.cmd_init, project=str(project), host="claude", vault="new", vault_path=None)
            self.assertEqual(code, 0)

            code, _, _ = run_command(chef_cli.cmd_verify, project=str(project))
            self.assertEqual(code, 0)

    def test_existing_vault_content_survives_init(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            vault = root / "shared-vault"
            (vault / "Home").mkdir(parents=True)
            (vault / "Memory").mkdir(parents=True)
            (vault / "Graphify" / "graphify-out" / "wiki").mkdir(parents=True)
            (vault / "Home" / "Home.md").write_text("CUSTOM HOME\n", encoding="utf-8")
            (vault / "Memory" / "Memory.md").write_text("CUSTOM MEMORY\n", encoding="utf-8")
            (vault / "Graphify" / "index.md").write_text("CUSTOM GRAPH\n", encoding="utf-8")

            code, _, _ = run_command(
                chef_cli.cmd_init,
                project=str(project),
                host="codex",
                vault="existing",
                vault_path=str(vault),
            )
            self.assertEqual(code, 0)
            self.assertEqual((vault / "Home" / "Home.md").read_text(encoding="utf-8"), "CUSTOM HOME\n")
            self.assertEqual((vault / "Memory" / "Memory.md").read_text(encoding="utf-8"), "CUSTOM MEMORY\n")
            self.assertEqual((vault / "Graphify" / "index.md").read_text(encoding="utf-8"), "CUSTOM GRAPH\n")

            manifest = json.loads((project / ".chef" / "chef.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["vault"], str(vault.resolve()))
            self.assertEqual(manifest["graph_index"], str((vault / "Graphify" / "graphify-out" / "wiki" / "index.md").resolve()))
            self.assertEqual(manifest["graph_report"], str((vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md").resolve()))

            code, _, _ = run_command(chef_cli.cmd_verify, project=str(project))
            self.assertEqual(code, 0)

    def test_existing_vault_requires_real_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            missing_vault = root / "missing-vault"

            code, _, stderr = run_command(
                chef_cli.cmd_init,
                project=str(project),
                host="codex",
                vault="existing",
                vault_path=str(missing_vault),
            )
            self.assertEqual(code, 1)
            self.assertIn("Existing vault path not found", stderr)

    def test_graph_refresh_dry_run_preserves_existing_graph_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None)
            self.assertEqual(code, 0)

            report = project / "knowledge-vault" / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"
            index = project / "knowledge-vault" / "Graphify" / "graphify-out" / "wiki" / "index.md"
            report.write_text("REAL REPORT\n", encoding="utf-8")
            index.write_text("REAL INDEX\n", encoding="utf-8")

            code, _, _ = run_command(chef_cli.cmd_graph_refresh, project=str(project), host="codex", execute=False)
            self.assertEqual(code, 0)
            self.assertEqual(report.read_text(encoding="utf-8"), "REAL REPORT\n")
            self.assertEqual(index.read_text(encoding="utf-8"), "REAL INDEX\n")

    def test_new_vault_manifest_uses_project_relative_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(chef_cli.cmd_init, project=str(project), host="both", vault="new", vault_path=None)
            self.assertEqual(code, 0)

            manifest = json.loads((project / ".chef" / "chef.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["vault"], "knowledge-vault")
            self.assertEqual(manifest["graph_index"], "knowledge-vault/Graphify/graphify-out/wiki/index.md")
            self.assertEqual(manifest["graph_report"], "knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md")

    def test_pack_registry_prefers_pack_directory_definitions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            packs_dir = root / "packs"
            legacy_file = root / "core" / "packs.json"
            (packs_dir / "alpha").mkdir(parents=True)
            (packs_dir / "beta").mkdir(parents=True)
            legacy_file.parent.mkdir(parents=True)
            (packs_dir / "alpha" / "pack.json").write_text(
                json.dumps({"name": "alpha", "default": True, "tools": ["graphify"]}),
                encoding="utf-8",
            )
            (packs_dir / "beta" / "pack.json").write_text(
                json.dumps({"name": "beta", "enabled_by_default": False, "items": ["secure-code-guardian"]}),
                encoding="utf-8",
            )
            legacy_file.write_text(json.dumps({"legacy": {"enabled_by_default": True, "items": ["old"]}}), encoding="utf-8")

            with patch.object(pack_ops, "PACKS_DIR", packs_dir), patch.object(pack_ops, "PACKS_FILE", legacy_file):
                registry = pack_ops.read_pack_registry()

            self.assertEqual(
                registry,
                {
                    "alpha": {"enabled_by_default": True, "items": ["graphify"]},
                    "beta": {"enabled_by_default": False, "items": ["secure-code-guardian"]},
                },
            )

    def test_install_codex_replaces_existing_skill_copy(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            home = Path(tmp) / "home"
            project = Path(tmp) / "project"
            skill_src = root / "adapters" / "codex" / "skills" / "skill-a"
            plugin_src = root / "adapters" / "codex" / ".codex-plugin"
            skill_src.mkdir(parents=True)
            plugin_src.mkdir(parents=True)
            project.mkdir(parents=True)
            (skill_src / "SKILL.md").write_text("# Skill A\n", encoding="utf-8")
            (plugin_src / "plugin.json").write_text('{"name":"chef"}\n', encoding="utf-8")

            existing = home / ".codex" / "skills" / "skill-a"
            existing.mkdir(parents=True)
            (existing / "OLD.md").write_text("old\n", encoding="utf-8")

            with patch.object(host_install, "ROOT", root), patch.object(host_install.Path, "home", return_value=home):
                installed = host_install.install_codex(project)

            self.assertIn(str(home / ".codex" / "skills" / "skill-a"), installed)
            self.assertIn(str(project / ".codex-plugin"), installed)
            self.assertTrue((home / ".codex" / "skills" / "skill-a" / "SKILL.md").exists())
            self.assertFalse((home / ".codex" / "skills" / "skill-a" / "OLD.md").exists())
            self.assertTrue((project / ".codex-plugin" / "plugin.json").exists())

    def test_install_claude_copies_commands_and_plugin(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            home = Path(tmp) / "home"
            project = Path(tmp) / "project"
            commands_src = root / "adapters" / "claude" / "commands"
            plugin_src = root / "adapters" / "claude" / ".claude-plugin"
            commands_src.mkdir(parents=True)
            plugin_src.mkdir(parents=True)
            project.mkdir(parents=True)
            (commands_src / "chef-pack-status.md").write_text("# status\n", encoding="utf-8")
            (plugin_src / "plugin.json").write_text('{"name":"chef"}\n', encoding="utf-8")

            with patch.object(host_install, "ROOT", root), patch.object(host_install.Path, "home", return_value=home):
                installed = host_install.install_claude(project)

            self.assertIn(str(home / ".claude" / "commands" / "chef"), installed)
            self.assertIn(str(home / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin"), installed)
            self.assertTrue((home / ".claude" / "commands" / "chef" / "chef-pack-status.md").exists())
            self.assertTrue((home / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin" / "plugin.json").exists())

    def test_resolve_graphify_binary_prefers_local_virtualenv(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            local_graphify = project / ".venv" / "bin" / "graphify"
            local_graphify.parent.mkdir(parents=True)
            local_graphify.write_text("", encoding="utf-8")

            with patch.object(shutil, "which", return_value="/usr/local/bin/graphify"):
                binary = graphify_ops.resolve_graphify_binary(project)

            self.assertEqual(binary, str(local_graphify))

    def test_run_graphify_command_returns_127_when_binary_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            code = graphify_ops.run_graphify_command(["definitely-missing-graphify-binary"], Path(tmp))
            self.assertEqual(code, 127)

    def test_mcp_common_uses_manifest_defined_external_vault(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            vault = root / "shared-vault"
            (vault / "Home").mkdir(parents=True)
            (vault / "Memory").mkdir(parents=True)
            (vault / "Graphify" / "graphify-out" / "wiki").mkdir(parents=True)
            (vault / "Home" / "Home.md").write_text("home\n", encoding="utf-8")
            (vault / "Memory" / "Memory.md").write_text("memory\n", encoding="utf-8")
            (vault / "Graphify" / "index.md").write_text("graph\n", encoding="utf-8")
            (vault / "Graphify" / "graphify-out" / "wiki" / "index.md").write_text("wiki\n", encoding="utf-8")
            (vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md").write_text("report\n", encoding="utf-8")

            code, _, _ = run_command(
                chef_cli.cmd_init,
                project=str(project),
                host="codex",
                vault="existing",
                vault_path=str(vault),
            )
            self.assertEqual(code, 0)
            self.assertEqual(mcp_common.vault_dir(str(project)), vault.resolve())
            self.assertEqual(mcp_common.graph_index_path(str(project)), (vault / "Graphify" / "graphify-out" / "wiki" / "index.md").resolve())
            self.assertEqual(mcp_common.graph_report_path(str(project)), (vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md").resolve())

    def test_verify_reports_invalid_manifest_cleanly(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            manifest_dir = project / ".chef"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "chef.json").write_text('{"host":"wrong"}\n', encoding="utf-8")

            code, _, stderr = run_command(chef_cli.cmd_verify, project=str(project))
            self.assertEqual(code, 1)
            self.assertIn("Invalid manifest", stderr)

    def test_pack_status_reports_invalid_pack_definition_cleanly(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            packs_dir = root / "packs"
            (packs_dir / "broken").mkdir(parents=True)
            (packs_dir / "broken" / "pack.json").write_text('{"name":"broken","tools":"not-a-list"}\n', encoding="utf-8")
            project.mkdir(parents=True)

            with patch.object(pack_ops, "PACKS_DIR", packs_dir):
                code, _, stderr = run_command(chef_cli.cmd_pack_status, project=str(project))

            self.assertEqual(code, 1)
            self.assertIn("Invalid pack definition", stderr)


if __name__ == "__main__":
    unittest.main()
