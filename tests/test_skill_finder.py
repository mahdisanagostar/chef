from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from chef import cli as chef_cli
from chef import packs as pack_ops
from chef import policy as policy_ops

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "adapters" / "shared" / "skills" / "skill-finder"
SYNC_SCRIPT = SKILL_DIR / "scripts" / "sync_mirror.py"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "quick_validate.py"


def run_command(func, **kwargs) -> tuple[int, str, str]:
    from argparse import Namespace
    from contextlib import redirect_stderr, redirect_stdout
    from io import StringIO

    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        code = func(Namespace(**kwargs))
    return code, stdout_buffer.getvalue(), stderr_buffer.getvalue()


class SkillFinderTests(unittest.TestCase):
    def test_skill_finder_is_always_installed_for_both_hosts(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init,
                project=str(project),
                host="both",
                vault="new",
                vault_path=None,
            )
            self.assertEqual(code, 0)
            (project / ".chef" / "enabled-packs.json").write_text(
                '{"enabled":[]}\n',
                encoding="utf-8",
            )

            codex_items = {
                str(item["id"]) for item in pack_ops.resolve_enabled_items(project, "codex")
            }
            claude_items = {
                str(item["id"]) for item in pack_ops.resolve_enabled_items(project, "claude")
            }

            self.assertIn("skill-finder", codex_items)
            self.assertIn("skill-finder", claude_items)

    def test_policy_mentions_skill_finder_as_default_router(self) -> None:
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            code, _, _ = run_command(
                chef_cli.cmd_init,
                project=str(project),
                host="both",
                vault="new",
                vault_path=None,
            )
            self.assertEqual(code, 0)

            codex_policy = policy_ops.render_codex_policy(project)
            claude_policy = policy_ops.render_claude_policy(project)

            self.assertIn("Always run `$skill-finder` after `$chef-index`", codex_policy)
            self.assertIn(
                "Always use `skill-finder` before choosing specialist skills",
                claude_policy,
            )

    def test_skill_finder_docs_cover_host_native_routes_and_fast_path(self) -> None:
        skill_doc = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        matrix = (SKILL_DIR / "references" / "selection-matrix.md").read_text(
            encoding="utf-8"
        )
        rules = (SKILL_DIR / "references" / "routing-rules.md").read_text(
            encoding="utf-8"
        )
        agent_prompt = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn(
            "Do not force routing when the task is already small and obvious.",
            skill_doc,
        )
        self.assertIn(
            "Prefer host-native specialists before generic overlap",
            skill_doc,
        )
        self.assertIn("editable `.pptx` deck -> `slides`", matrix)
        self.assertIn("OpenAI product or API guidance -> `openai-docs`", matrix)
        self.assertIn("GitHub Actions CI failure -> `github:gh-fix-ci`", matrix)
        self.assertIn(
            "Slack outbound message or draft -> `slack:slack-outgoing-message`",
            matrix,
        )
        self.assertIn("iOS simulator run or debug -> `build-ios-apps:ios-debugger-agent`", matrix)
        self.assertIn("Do not pick both items from same overlap pair", rules)
        self.assertIn("skip routing for trivial tasks", rules)
        self.assertIn("preferring host-native specialists", agent_prompt)

    def test_sync_mirror_uses_env_override(self) -> None:
        with TemporaryDirectory() as tmp:
            mirror = Path(tmp) / "mirror"
            mirror.mkdir()
            env = dict(os.environ, SKILL_FINDER_MIRROR=str(mirror))

            sync_result = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--mode", "sync"],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            self.assertIn("synced:", sync_result.stdout)

            check_result = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--mode", "check"],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            self.assertIn("in sync", check_result.stdout)

    def test_quick_validate_uses_override_validator(self) -> None:
        with TemporaryDirectory() as tmp:
            validator = Path(tmp) / "validator.py"
            output = Path(tmp) / "args.json"
            validator.write_text(
                "import json\n"
                "import pathlib\n"
                "import sys\n"
                "pathlib.Path(sys.argv[2]).write_text(json.dumps(sys.argv[1:]))\n",
                encoding="utf-8",
            )
            env = dict(
                os.environ,
                SKILL_FINDER_QUICK_VALIDATE=str(validator),
                PYTHONDONTWRITEBYTECODE="1",
            )

            subprocess.run(
                [sys.executable, str(VALIDATE_SCRIPT), str(output)],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )

            argv = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(argv[0], str(SKILL_DIR))
            self.assertEqual(argv[1], str(output))

    def test_sync_mirror_matches_sibling_repo_when_present(self) -> None:
        sibling = ROOT.parent / "skill-finder" / "skill-finder"
        if not sibling.exists():
            self.skipTest("sibling skill-finder repo not present")

        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), str(sibling), "--mode", "check"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("in sync", result.stdout)


if __name__ == "__main__":
    unittest.main()
