from __future__ import annotations

import importlib
import json
import subprocess
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

chef_cli = importlib.import_module("chef.cli")
graphify_ops = importlib.import_module("chef.graphify")
external_ops = importlib.import_module("chef.external")
host_install = importlib.import_module("chef.hosts")
pack_ops = importlib.import_module("chef.packs")
policy_ops = importlib.import_module("chef.policy")


def run_command(func, **kwargs: object) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    defaults = {"json": False, "plan": False}
    defaults.update(kwargs)
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = func(SimpleNamespace(**defaults))
    return code, stdout.getvalue(), stderr.getvalue()


def init_git_repo(project: Path) -> None:
    subprocess.run(
        ["git", "init", str(project)],
        check=True,
        capture_output=True,
        text=True,
    )


class ChefCliTests(unittest.TestCase):
    def test_init_writes_managed_policy_indexes(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="both", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            agents = (project / "AGENTS.md").read_text(encoding="utf-8")
            claude = (project / "CLAUDE.md").read_text(encoding="utf-8")
            codex_config = (project / ".codex" / "config.toml").read_text(encoding="utf-8")
            claude_settings = json.loads(
                (project / ".claude" / "settings.json").read_text(encoding="utf-8")
            )

            self.assertIn("Chef manages this file as the project policy", agents)
            self.assertIn("## Readable Persian Text", agents)
            self.assertIn("## Tarzan Persona", agents)
            self.assertIn("## Graph-First Rule", agents)
            self.assertIn("## Skills And Commands", agents)
            self.assertNotIn("## Routing", agents)
            self.assertIn("## graphify", agents)
            self.assertIn("- `$chef-index`", agents)
            self.assertIn("Always use `$chef-index` first", agents)
            self.assertIn("Fast Path runs by default", agents)
            self.assertIn("never replies to the user directly", agents)

            self.assertIn("Chef manages this file as the project policy", claude)
            self.assertIn("## Skills And Commands", claude)
            self.assertIn("- `/chef-graph-refresh`", claude)
            self.assertNotIn("- `/chef-expert-plan`", claude)
            self.assertNotIn("## Readable Persian Text", claude)
            self.assertEqual(claude_settings["model"], "opusplan")
            self.assertIn('model = "gpt-5.4-mini"', codex_config)
            self.assertIn('model_reasoning_effort = "high"', codex_config)
            self.assertIn("[profiles.chef-fast]", codex_config)
            self.assertIn("[profiles.chef-expert]", codex_config)
            self.assertIn('model = "gpt-5.4"', codex_config)
            self.assertIn('model_reasoning_effort = "xhigh"', codex_config)

    def test_verify_respects_claude_only_projects(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="claude", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )
            policy_ops.sync_project_policies(project, "claude")
            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="claude", offline=False
                )
            self.assertEqual(code, 0)
            code, _, _ = run_command(chef_cli.cmd_verify, project=str(project), json=False)
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
                host="claude",
                vault="existing",
                vault_path=str(vault),
            )
            self.assertEqual(code, 0)
            self.assertEqual(
                (vault / "Home" / "Home.md").read_text(encoding="utf-8"), "CUSTOM HOME\n"
            )
            self.assertEqual(
                (vault / "Memory" / "Memory.md").read_text(encoding="utf-8"), "CUSTOM MEMORY\n"
            )
            self.assertEqual(
                (vault / "Graphify" / "index.md").read_text(encoding="utf-8"), "CUSTOM GRAPH\n"
            )

            manifest = json.loads((project / ".chef" / "chef.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["vault"], str(vault.resolve()))
            self.assertEqual(
                manifest["graph_index"],
                str((vault / "Graphify" / "graphify-out" / "wiki" / "index.md").resolve()),
            )
            self.assertEqual(
                manifest["graph_report"],
                str((vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md").resolve()),
            )

            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )
            policy_ops.sync_project_policies(project, "claude")
            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="claude", offline=False
                )
            self.assertEqual(code, 0)
            code, _, _ = run_command(chef_cli.cmd_verify, project=str(project), json=False)
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
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            report = project / "knowledge-vault" / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"
            index = project / "knowledge-vault" / "Graphify" / "graphify-out" / "wiki" / "index.md"
            report.write_text("REAL REPORT\n", encoding="utf-8")
            index.write_text("REAL INDEX\n", encoding="utf-8")

            code, stdout, _ = run_command(
                chef_cli.cmd_graph_refresh, project=str(project), host="auto", execute=False
            )
            self.assertEqual(code, 0)
            self.assertEqual(report.read_text(encoding="utf-8"), "REAL REPORT\n")
            self.assertEqual(index.read_text(encoding="utf-8"), "REAL INDEX\n")
            self.assertIn("Graphify host: codex", stdout)

    def test_new_vault_manifest_uses_project_relative_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="both", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            manifest = json.loads((project / ".chef" / "chef.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["vault"], "knowledge-vault")
            self.assertEqual(
                manifest["graph_index"], "knowledge-vault/Graphify/graphify-out/wiki/index.md"
            )
            self.assertEqual(
                manifest["graph_report"], "knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md"
            )

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
                json.dumps(
                    {"name": "beta", "enabled_by_default": False, "items": ["secure-code-guardian"]}
                ),
                encoding="utf-8",
            )
            legacy_file.write_text(
                json.dumps({"legacy": {"enabled_by_default": True, "items": ["old"]}}),
                encoding="utf-8",
            )

            with (
                patch.object(pack_ops, "PACKS_DIR", packs_dir),
                patch.object(pack_ops, "PACKS_FILE", legacy_file),
            ):
                registry = pack_ops.read_pack_registry()

            self.assertEqual(
                registry,
                {
                    "alpha": {"enabled_by_default": True, "items": ["graphify"]},
                    "beta": {"enabled_by_default": False, "items": ["secure-code-guardian"]},
                },
            )

    def test_pack_status_resolves_enabled_catalog_items(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            code, stdout, _ = run_command(chef_cli.cmd_pack_status, project=str(project), json=True)
            self.assertEqual(code, 0)
            status = json.loads(stdout)

            self.assertEqual(status["enabled"], ["core"])
            self.assertIn("chef-index", status["bundled_items"])
            self.assertIn("graph-first-retrieval", status["bundled_items"])
            self.assertIn("skill-finder", status["bundled_items"])
            self.assertIn("using-git-worktrees", status["bundled_items"])
            self.assertIn("feature-forge", status["manual_items"])
            self.assertIn("playwright-skill", status["manual_items"])
            self.assertNotIn("gstack", status["manual_items"])
            self.assertNotIn("ruflo", status["manual_items"])
            self.assertNotIn("superpowers", status["manual_items"])

    def test_cmd_install_codex_respects_enabled_bundled_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, stdout, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=False
                )

            self.assertEqual(code, 0)
            self.assertTrue((project / ".codex" / "skills" / "chef-index" / "SKILL.md").exists())
            self.assertTrue(
                (project / ".codex" / "skills" / "graph-first-retrieval" / "SKILL.md").exists()
            )
            self.assertTrue(
                (project / ".codex" / "skills" / "skill-finder" / "SKILL.md").exists()
            )
            self.assertTrue(
                (project / ".codex" / "skills" / "using-git-worktrees" / "SKILL.md").exists()
            )
            self.assertIn("Installed Chef assets:", stdout)
            mcp_data = json.loads(
                (project / ".codex-plugin" / ".mcp.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                mcp_data["mcpServers"]["chef-knowledge-mcp"],
                {
                    "command": str(project.resolve() / ".venv" / "bin" / "chef-knowledge-mcp"),
                    "args": [],
                },
            )

    def test_cmd_install_codex_skips_optional_skills_when_no_pack_enables_them(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=False
                )

            self.assertEqual(code, 0)
            self.assertTrue((project / ".codex" / "skills" / "chef-index" / "SKILL.md").exists())
            self.assertTrue(
                (project / ".codex" / "skills" / "graph-first-retrieval" / "SKILL.md").exists()
            )
            self.assertTrue((project / ".codex" / "skills" / "skill-finder" / "SKILL.md").exists())
            self.assertFalse((project / ".codex" / "skills" / "using-git-worktrees").exists())

    def test_cmd_install_codex_prunes_disabled_managed_skills_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )

            stale_skill = project / ".codex" / "skills" / "gstack"
            stale_skill.mkdir(parents=True)
            (stale_skill / "SKILL.md").write_text("# stale\n", encoding="utf-8")
            custom_skill = project / ".codex" / "skills" / "custom-skill"
            custom_skill.mkdir(parents=True)
            (custom_skill / "SKILL.md").write_text("# custom\n", encoding="utf-8")

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=True
                )

            self.assertEqual(code, 0)
            self.assertFalse(stale_skill.exists())
            self.assertTrue(custom_skill.exists())
            self.assertTrue((project / ".codex" / "skills" / "chef-index" / "SKILL.md").exists())

    def test_install_codex_replaces_existing_skill_copy(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            project = Path(tmp) / "project"
            skill_src = root / "adapters" / "codex" / "skills" / "skill-a"
            plugin_src = root / "adapters" / "codex" / ".codex-plugin"
            skill_src.mkdir(parents=True)
            plugin_src.mkdir(parents=True)
            project.mkdir(parents=True)
            (skill_src / "SKILL.md").write_text("# Skill A\n", encoding="utf-8")
            (plugin_src / "plugin.json").write_text('{"name":"chef"}\n', encoding="utf-8")

            existing = project / ".codex" / "skills" / "skill-a"
            existing.mkdir(parents=True)
            (existing / "OLD.md").write_text("old\n", encoding="utf-8")
            bundled_item = {
                "id": "skill-a",
                "install": {"path": "adapters/codex/skills/skill-a"},
            }

            with patch.object(host_install, "ROOT", root):
                installed = host_install.install_codex(project, [bundled_item])

            self.assertIn(str(project / ".codex" / "skills" / "skill-a"), installed)
            self.assertIn(str(project / ".codex-plugin"), installed)
            self.assertIn(str(project / ".codex-plugin" / ".mcp.json"), installed)
            self.assertTrue((project / ".codex" / "skills" / "skill-a" / "SKILL.md").exists())
            self.assertFalse((project / ".codex" / "skills" / "skill-a" / "OLD.md").exists())
            self.assertTrue((project / ".codex-plugin" / "plugin.json").exists())
            mcp_data = json.loads((project / ".codex-plugin" / ".mcp.json").read_text())
            self.assertEqual(
                mcp_data["mcpServers"]["chef-knowledge-mcp"],
                {
                    "command": str(project.resolve() / ".venv" / "bin" / "chef-knowledge-mcp"),
                    "args": [],
                },
            )

    def test_install_claude_copies_commands_and_plugin(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            project = Path(tmp) / "project"
            commands_src = root / "adapters" / "claude" / "commands"
            plugin_src = root / "adapters" / "claude" / ".claude-plugin"
            commands_src.mkdir(parents=True)
            plugin_src.mkdir(parents=True)
            project.mkdir(parents=True)
            (commands_src / "chef-pack-status.md").write_text("# status\n", encoding="utf-8")
            (plugin_src / "plugin.json").write_text('{"name":"chef"}\n', encoding="utf-8")
            existing_command_dir = project / ".claude" / "commands" / "chef"
            existing_plugin_dir = (
                project / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin"
            )
            existing_command_dir.mkdir(parents=True)
            existing_plugin_dir.mkdir(parents=True)
            (existing_command_dir / "OLD.md").write_text("old command\n", encoding="utf-8")
            (existing_plugin_dir / "plugin.json").write_text('{"name":"old"}\n', encoding="utf-8")

            with patch.object(host_install, "ROOT", root):
                installed = host_install.install_claude(project)

            self.assertIn(str(project / ".claude" / "commands" / "chef"), installed)
            self.assertIn(
                str(project / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin"),
                installed,
            )
            self.assertTrue(
                (project / ".claude" / "commands" / "chef" / "chef-pack-status.md").exists()
            )
            self.assertFalse((project / ".claude" / "commands" / "chef" / "OLD.md").exists())
            self.assertTrue(
                (
                    project
                    / ".claude"
                    / "plugins"
                    / "local"
                    / "chef"
                    / ".claude-plugin"
                    / "plugin.json"
                ).exists()
            )

    def test_install_claude_copies_bundled_shared_skill(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            project = Path(tmp) / "project"
            commands_src = root / "adapters" / "claude" / "commands"
            plugin_src = root / "adapters" / "claude" / ".claude-plugin"
            skill_src = root / "adapters" / "shared" / "skills" / "using-git-worktrees"
            commands_src.mkdir(parents=True)
            plugin_src.mkdir(parents=True)
            skill_src.mkdir(parents=True)
            project.mkdir(parents=True)
            (commands_src / "chef-pack-status.md").write_text("# status\n", encoding="utf-8")
            (plugin_src / "plugin.json").write_text('{"name":"chef"}\n', encoding="utf-8")
            (skill_src / "SKILL.md").write_text("# Worktrees\n", encoding="utf-8")
            bundled_item = {
                "id": "using-git-worktrees",
                "install": {"path": "adapters/shared/skills/using-git-worktrees"},
            }

            with patch.object(host_install, "ROOT", root):
                installed = host_install.install_claude(project, [bundled_item])

            self.assertIn(
                str(project / ".claude" / "skills" / "using-git-worktrees"),
                installed,
            )
            self.assertTrue(
                (project / ".claude" / "skills" / "using-git-worktrees" / "SKILL.md").exists()
            )

    def test_verify_codex_project_passes_after_local_install(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=True
                )

            self.assertEqual(code, 0)
            code, stdout, _ = run_command(chef_cli.cmd_verify, project=str(project), json=True)
            self.assertEqual(code, 0)
            checks = json.loads(stdout)["checks"]
            self.assertTrue(checks["mcp:chef-knowledge-mcp"])
            self.assertTrue(checks["item:chef-index"])
            self.assertTrue(checks["item:graph-first-retrieval"])

    def test_install_writes_install_state_for_bundled_items(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=True
                )

            self.assertEqual(code, 0)
            install_state = json.loads(
                (project / ".chef" / "install-state.json").read_text(encoding="utf-8")
            )
            self.assertIn("codex:chef-index", install_state["items"])
            self.assertIn("codex:graph-first-retrieval", install_state["items"])
            self.assertEqual(install_state["items"]["codex:chef-index"]["fidelity"], "direct")

    def test_review_and_security_packs_enable_builtin_mcp_servers(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":["review","security"]}\n', encoding="utf-8"
            )

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=True
                )

            self.assertEqual(code, 0)
            mcp_data = json.loads(
                (project / ".codex-plugin" / ".mcp.json").read_text(encoding="utf-8")
            )
            self.assertIn("chef-review-mcp", mcp_data["mcpServers"])
            self.assertIn("chef-security-mcp", mcp_data["mcpServers"])

    def test_git_privacy_enable_installs_hook_guard_and_git_config(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_git_repo(project)

            code, stdout, _ = run_command(
                chef_cli.cmd_git_privacy_enable,
                project=str(project),
                author_name="Mahdi Sanagostar",
                author_email="mahdi@example.com",
            )
            self.assertEqual(code, 0, stdout)

            state = json.loads((project / ".chef" / "git-privacy.json").read_text(encoding="utf-8"))
            self.assertTrue(state["enabled"])
            self.assertEqual(state["author_name"], "Mahdi Sanagostar")
            self.assertEqual(state["author_email"], "mahdi@example.com")

            hooks_path = subprocess.run(
                ["git", "-C", str(project), "config", "--local", "--get", "core.hooksPath"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(hooks_path, str((project / ".chef" / "git-hooks").resolve()))
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(project), "config", "--local", "--get", "user.name"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
                "Mahdi Sanagostar",
            )
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(project), "config", "--local", "--get", "user.email"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
                "mahdi@example.com",
            )
            self.assertIn("Git privacy guard enabled.", stdout)
            self.assertTrue((project / ".chef" / "git-hooks" / "commit-msg").exists())
            self.assertTrue((project / ".chef" / "git-hooks" / "pre-commit").exists())

            code, stdout, _ = run_command(
                chef_cli.cmd_git_privacy_status, project=str(project)
            )
            self.assertEqual(code, 0)
            self.assertIn("- enabled: True", stdout)
            self.assertIn("Mahdi Sanagostar", stdout)

            (project / "notes.txt").write_text("safe\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(project), "add", "notes.txt"], check=True)
            commit_result = subprocess.run(
                ["git", "-C", str(project), "commit", "-m", "Use Codex for fix"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(commit_result.returncode, 0)
            self.assertIn("blocked commit message", commit_result.stderr)

    def test_git_privacy_enable_rejects_blocked_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_git_repo(project)

            code, _, stderr = run_command(
                chef_cli.cmd_git_privacy_enable,
                project=str(project),
                author_name="Codex Agent",
                author_email="codex@example.com",
            )
            self.assertEqual(code, 1)
            self.assertIn("blocked term", stderr)

    def test_install_plan_reports_hosts_and_prune(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            stale_skill = project / ".codex" / "skills" / "gstack"
            stale_skill.mkdir(parents=True)
            (stale_skill / "SKILL.md").write_text("# stale\n", encoding="utf-8")

            code, stdout, _ = run_command(
                chef_cli.cmd_install,
                project=str(project),
                host="codex",
                offline=True,
                plan=True,
                json=True,
            )
            self.assertEqual(code, 0)
            plan = json.loads(stdout)
            self.assertIn("codex", plan["hosts"])
            self.assertIn(str(stale_skill.resolve()), plan["hosts"]["codex"]["prune"])

    def test_pack_enable_installs_new_pack_assets_for_project_host(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, stdout, _ = run_command(
                    chef_cli.cmd_pack_enable,
                    project=str(project),
                    offline=True,
                    json=True,
                    pack=["media"],
                )

            self.assertEqual(code, 0)
            status = json.loads(stdout)
            self.assertIn("media", status["enabled"])
            self.assertIn("talkcraft", status["enabled_items"])
            self.assertIn("remotion-best-practices", status["enabled_items"])
            self.assertTrue(
                (
                    project
                    / ".codex"
                    / "skills"
                    / "talkcraft"
                    / "SKILL.md"
                ).exists()
            )
            self.assertTrue(
                (project / ".codex" / "skills" / "remotion-best-practices" / "SKILL.md").exists()
            )
            self.assertIn(
                "$talkcraft",
                (project / "AGENTS.md").read_text(),
            )
            self.assertIn("$remotion-best-practices", (project / "AGENTS.md").read_text())
            self.assertTrue(status["installed"])

    def test_verify_reports_policy_index_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)

            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=True
                )

            self.assertEqual(code, 0)
            (project / "AGENTS.md").write_text("# drift\n", encoding="utf-8")

            code, stdout, _ = run_command(chef_cli.cmd_verify, project=str(project), json=True)
            self.assertEqual(code, 1)
            checks = json.loads(stdout)["checks"]
            self.assertFalse(checks["codex_policy_index"])

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
            code = graphify_ops.run_graphify_command(
                ["definitely-missing-graphify-binary"], Path(tmp)
            )
            self.assertEqual(code, 127)

    def test_resolve_graphify_host_prefers_codex_runtime_env(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            host = graphify_ops.resolve_graphify_host(
                project,
                "auto",
                "both",
                env={"CODEX_THREAD_ID": "thread"},
            )
            self.assertEqual(host, "codex")

    def test_resolve_graphify_host_falls_back_to_manifest_host(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            host = graphify_ops.resolve_graphify_host(project, "auto", "claude", env={})
            self.assertEqual(host, "claude")

    def test_verify_reports_invalid_manifest_cleanly(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            manifest_dir = project / ".chef"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "chef.json").write_text('{"host":"wrong"}\n', encoding="utf-8")

            code, _, stderr = run_command(chef_cli.cmd_verify, project=str(project))
            self.assertEqual(code, 1)
            self.assertIn("Invalid manifest", stderr)

    def test_verify_reports_git_privacy_guard_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_git_repo(project)
            code, _, _ = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n', encoding="utf-8"
            )
            with patch.object(
                external_ops,
                "sync_external_items",
                return_value=external_ops.SyncResult([], [], [], []),
            ):
                code, _, _ = run_command(
                    chef_cli.cmd_install, project=str(project), host="codex", offline=True
                )
            self.assertEqual(code, 0)
            code, _, _ = run_command(
                chef_cli.cmd_git_privacy_enable,
                project=str(project),
                author_name="Mahdi Sanagostar",
                author_email="mahdi@example.com",
            )
            self.assertEqual(code, 0)

            code, stdout, _ = run_command(chef_cli.cmd_verify, project=str(project), json=True)
            self.assertEqual(code, 0)
            checks = json.loads(stdout)["checks"]
            self.assertTrue(checks["git_privacy_state"])
            self.assertTrue(checks["git_privacy_commit_msg_hook"])
            self.assertTrue(checks["git_privacy_pre_commit_hook"])

    def test_pack_status_reports_invalid_pack_definition_cleanly(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            packs_dir = root / "packs"
            (packs_dir / "broken").mkdir(parents=True)
            (packs_dir / "broken" / "pack.json").write_text(
                '{"name":"broken","tools":"not-a-list"}\n', encoding="utf-8"
            )
            project.mkdir(parents=True)

            with patch.object(pack_ops, "PACKS_DIR", packs_dir):
                code, _, stderr = run_command(chef_cli.cmd_pack_status, project=str(project))

            self.assertEqual(code, 1)
            self.assertIn("Invalid pack definition", stderr)

    def test_pack_status_reports_unknown_catalog_items_cleanly(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            packs_dir = root / "packs"
            (packs_dir / "broken").mkdir(parents=True)
            (packs_dir / "broken" / "pack.json").write_text(
                '{"name":"broken","items":["missing-item"]}\n', encoding="utf-8"
            )
            project.mkdir(parents=True)

            with patch.object(pack_ops, "PACKS_DIR", packs_dir):
                code, _, stderr = run_command(chef_cli.cmd_pack_status, project=str(project))

            self.assertEqual(code, 1)
            self.assertIn("unknown catalog items", stderr)


if __name__ == "__main__":
    unittest.main()
