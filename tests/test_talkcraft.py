from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "adapters" / "shared" / "skills" / "talkcraft"
AUDIT_SCRIPT = SKILL_DIR / "scripts" / "audit_outline.py"
SYNC_SCRIPT = SKILL_DIR / "scripts" / "sync_mirror.py"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "quick_validate.py"


class TalkCraftTests(unittest.TestCase):
    def test_audit_outline_reports_fence_details(self) -> None:
        outline = """
# Demo Talk

## Mission
- Audience: engineers
- Objective: approve migration
- Duration: 15 minutes

## Core Message
- Promise: show why the migration matters
- Slogan: migrate once, simplify forever

## Fences

### Fence 1
- Time: 4 minutes
- Question answered: why act now
- Memory target: delay costs more
- Evidence: incident trend
- Board/demo move: draw current state
- Transition out: move from pain to design

### Fence 2
- Time: 5 minutes
- Question answered: what changes
- Memory target: simpler system
- Evidence: architecture comparison
- Board/demo move: side-by-side diagram
- Transition out: now prove rollout is safe

### Fence 3
- Time: 3 minutes
- Question answered: how rollout stays safe
- Memory target: controlled change
- Evidence: rollout checklist
- Board/demo move: show cutover steps
- Transition out: close with decision

## Opening
- First line: production complexity costs us every week
- Hook: recent incident
- Stakes: reliability and pace
- Promise line: by the end you will see why we should migrate now

## Closing
- Recap: pain, design, rollout
- Last line: approve the migration
- Final implication: faster delivery with lower operational risk

## Q&A
- Likely question 1: migration cost
"""
        with TemporaryDirectory() as tmp:
            outline_path = Path(tmp) / "outline.md"
            outline_path.write_text(outline.strip() + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(AUDIT_SCRIPT), str(outline_path), "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
        report = json.loads(result.stdout)
        self.assertEqual(report["fence_count"], 3)
        self.assertTrue(report["fence_structure_pass"])
        self.assertEqual(len(report["fence_details"]), 3)
        self.assertGreaterEqual(report["score"], 85)

    def test_sync_mirror_check_and_sync(self) -> None:
        with TemporaryDirectory() as tmp:
            mirror = Path(tmp) / "mirror"
            mirror.mkdir()
            (mirror / "SKILL.md").write_text("stale\n", encoding="utf-8")

            check_result = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), str(mirror), "--mode", "check"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(check_result.returncode, 0)

            sync_result = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), str(mirror), "--mode", "sync"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("synced:", sync_result.stdout)

            recheck_result = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), str(mirror), "--mode", "check"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("in sync", recheck_result.stdout)

    def test_sync_mirror_uses_env_override(self) -> None:
        with TemporaryDirectory() as tmp:
            mirror = Path(tmp) / "mirror"
            mirror.mkdir()
            env = dict(os.environ, TALKCRAFT_MIRROR=str(mirror))

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
                TALKCRAFT_QUICK_VALIDATE=str(validator),
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


if __name__ == "__main__":
    unittest.main()
