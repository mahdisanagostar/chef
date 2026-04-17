from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

chef_cli = importlib.import_module("chef.cli")
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


if __name__ == "__main__":
    unittest.main()
