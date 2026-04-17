from __future__ import annotations

import json
from pathlib import Path

from chef.paths import PACKS_DIR, PACKS_FILE
from chef.scaffold import write_file


def read_pack_registry() -> dict[str, dict[str, object]]:
    registry: dict[str, dict[str, object]] = {}
    for pack_file in sorted(PACKS_DIR.glob("*/pack.json")):
        data = json.loads(pack_file.read_text(encoding="utf-8"))
        name = data.get("name", pack_file.parent.name)
        registry[name] = {
            "enabled_by_default": bool(data.get("enabled_by_default", data.get("default", False))),
            "items": list(data.get("items", data.get("tools", []))),
        }
    if registry:
        return registry
    return json.loads(PACKS_FILE.read_text(encoding="utf-8"))


def pack_state_path(project: Path) -> Path:
    return project / ".chef" / "enabled-packs.json"


def read_enabled_packs(project: Path) -> dict[str, object]:
    path = pack_state_path(project)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    registry = read_pack_registry()
    defaults = sorted(name for name, meta in registry.items() if meta.get("enabled_by_default") or meta.get("default"))
    return {"enabled": defaults}


def write_enabled_packs(project: Path, state: dict[str, object]) -> None:
    write_file(pack_state_path(project), json.dumps(state, indent=2) + "\n")
