from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

chef_cli = importlib.import_module("chef.cli")
graphify_ops = importlib.import_module("chef.graphify")
mcp_common = importlib.import_module("chef.mcp.common")
mcp_knowledge = importlib.import_module("chef.mcp.knowledge")
mcp_review = importlib.import_module("chef.mcp.review")
mcp_security = importlib.import_module("chef.mcp.security")


def run_command(func, **kwargs: object) -> int:
    return func(SimpleNamespace(**kwargs))


class ChefMcpTests(unittest.TestCase):
    def test_external_vault_resolution_and_warnings(self) -> None:
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
            (vault / "Graphify" / "graphify-out" / "wiki" / "index.md").write_text(
                "wiki\n", encoding="utf-8"
            )
            (vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md").write_text(
                "report\n", encoding="utf-8"
            )

            code = run_command(
                chef_cli.cmd_init,
                project=str(project),
                host="codex",
                vault="existing",
                vault_path=str(vault),
            )
            self.assertEqual(code, 0)
            self.assertEqual(mcp_common.vault_dir(str(project)), vault.resolve())
            self.assertEqual(
                mcp_common.graph_index_path(str(project)),
                (vault / "Graphify" / "graphify-out" / "wiki" / "index.md").resolve(),
            )
            self.assertEqual(
                mcp_common.graph_report_path(str(project)),
                (vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md").resolve(),
            )
            warning = mcp_common.manifest_warning(str(project))
            self.assertIn("external vault", warning or "")
            self.assertIn("Warning:", mcp_knowledge.vault_summary(str(project)))
            self.assertIn("Warning:", mcp_review.review_sources(str(project)))
            self.assertIn("Warning:", mcp_security.security_review_order(str(project)))

    def test_invalid_manifest_warning_falls_back_to_default_vault(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            manifest_dir = project / ".chef"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "chef.json").write_text('{"host":"wrong"}\n', encoding="utf-8")

            warning = mcp_common.manifest_warning(str(project))
            self.assertIn("Invalid manifest", warning or "")
            self.assertEqual(
                mcp_common.vault_dir(str(project)),
                (project / "knowledge-vault").resolve(),
            )
            self.assertIn("Warning:", mcp_knowledge.vault_summary(str(project)))

    def test_vault_note_tools_cover_search_read_write_and_backlinks(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            vault = project / "knowledge-vault"
            home = vault / "Home" / "Home.md"
            memory = vault / "Memory" / "Memory.md"
            home.write_text(
                "# Home\n\n[[Memory]]\n[Graph](../Graphify/index.md)\n",
                encoding="utf-8",
            )
            memory.write_text("Durable memory lives here.\n", encoding="utf-8")

            search = mcp_knowledge.search_vault_notes(str(project), query="durable", limit=5)
            self.assertEqual(search["count"], 1)
            self.assertEqual(search["results"][0]["path"], "Memory/Memory.md")

            read_text = mcp_knowledge.read_note(str(project), "Memory")
            self.assertIn("Durable memory lives here.", read_text)

            write_result = mcp_knowledge.write_note(
                str(project), "Notes/Ideas", "Fresh thought", append=False
            )
            self.assertEqual(write_result, "Wrote note: Notes/Ideas.md")
            append_result = mcp_knowledge.write_note(
                str(project), "Notes/Ideas", "Second line", append=True
            )
            self.assertEqual(append_result, "Appended note: Notes/Ideas.md")
            note_text = (vault / "Notes" / "Ideas.md").read_text(encoding="utf-8")
            self.assertEqual(note_text, "Fresh thought\nSecond line")

            memory_backlinks = mcp_knowledge.list_backlinks(str(project), "Memory")
            self.assertEqual(memory_backlinks["count"], 1)
            self.assertEqual(memory_backlinks["results"][0]["path"], "Home/Home.md")
            graph_backlinks = mcp_knowledge.list_backlinks(str(project), "Graphify/index.md")
            self.assertEqual(graph_backlinks["count"], 1)
            self.assertEqual(graph_backlinks["results"][0]["path"], "Home/Home.md")

    def test_graph_status_and_refresh_if_stale(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code = run_command(
                chef_cli.cmd_init, project=str(project), host="codex", vault="new", vault_path=None
            )
            self.assertEqual(code, 0)
            graph_json = project / "knowledge-vault" / "Graphify" / "graphify-out" / "graph.json"
            graph_json.write_text("{}\n", encoding="utf-8")
            os.utime(graph_json, (1, 1))
            source = project / "src" / "module.py"
            source.parent.mkdir(parents=True)
            source.write_text("print('hello')\n", encoding="utf-8")

            initial = mcp_knowledge.graph_status(str(project))
            self.assertTrue(initial["stale"])
            self.assertEqual(initial["newest_input"], "src/module.py")

            def fake_run(command: list[str], cwd: Path) -> int:
                graph_json.write_text('{"ok": true}\n', encoding="utf-8")
                return 0

            with (
                patch.object(graphify_ops, "resolve_graphify_binary", return_value="graphify"),
                patch.object(graphify_ops, "run_graphify_command", side_effect=fake_run),
            ):
                refreshed = mcp_knowledge.refresh_graph_if_stale(str(project))

            self.assertTrue(refreshed["updated"])
            self.assertEqual(refreshed["exit_code"], 0)
            self.assertFalse(refreshed["status_after"]["stale"])
            self.assertEqual(refreshed["status_after"]["newest_input"], "src/module.py")


if __name__ == "__main__":
    unittest.main()
