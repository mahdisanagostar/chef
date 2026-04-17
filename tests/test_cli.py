from __future__ import annotations

import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chef.cli import cmd_graph_refresh, cmd_init, cmd_verify


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
            code, _, _ = run_command(cmd_init, project=str(project), host="claude", vault="new", vault_path=None)
            self.assertEqual(code, 0)

            code, _, _ = run_command(cmd_verify, project=str(project))
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
                cmd_init,
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

            code, _, _ = run_command(cmd_verify, project=str(project))
            self.assertEqual(code, 0)

    def test_existing_vault_requires_real_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            missing_vault = root / "missing-vault"

            code, _, stderr = run_command(
                cmd_init,
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
            code, _, _ = run_command(cmd_init, project=str(project), host="codex", vault="new", vault_path=None)
            self.assertEqual(code, 0)

            report = project / "knowledge-vault" / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"
            index = project / "knowledge-vault" / "Graphify" / "graphify-out" / "wiki" / "index.md"
            report.write_text("REAL REPORT\n", encoding="utf-8")
            index.write_text("REAL INDEX\n", encoding="utf-8")

            code, _, _ = run_command(cmd_graph_refresh, project=str(project), host="codex", execute=False)
            self.assertEqual(code, 0)
            self.assertEqual(report.read_text(encoding="utf-8"), "REAL REPORT\n")
            self.assertEqual(index.read_text(encoding="utf-8"), "REAL INDEX\n")


if __name__ == "__main__":
    unittest.main()
