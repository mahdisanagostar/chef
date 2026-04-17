from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"
PACKS_DIR = ROOT / "packs"
PACKS_FILE = ROOT / "core" / "packs.json"
