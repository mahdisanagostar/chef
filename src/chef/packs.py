from __future__ import annotations

import json
from pathlib import Path

from chef.paths import PACKS_DIR, PACKS_FILE
from chef.scaffold import write_file


def normalize_pack_definition(name: str, data: object, source: Path) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid pack definition at {source}: expected JSON object.")

    pack_name = data.get("name", name)
    if not isinstance(pack_name, str) or not pack_name:
        raise ValueError(f"Invalid pack definition at {source}: name must be a non-empty string.")

    items = data.get("items", data.get("tools", []))
    if not isinstance(items, list) or any(not isinstance(item, str) or not item for item in items):
        raise ValueError(
            f"Invalid pack definition at {source}: items/tools must be a list of non-empty strings."
        )

    enabled_by_default = data.get("enabled_by_default", data.get("default", False))
    if not isinstance(enabled_by_default, bool):
        raise ValueError(
            f"Invalid pack definition at {source}: enabled_by_default/default must be boolean."
        )

    return {
        "name": pack_name,
        "enabled_by_default": enabled_by_default,
        "items": list(items),
    }


def normalize_legacy_registry(data: object, source: Path) -> dict[str, dict[str, object]]:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid pack registry at {source}: expected JSON object.")

    registry: dict[str, dict[str, object]] = {}
    for name, raw in data.items():
        normalized = normalize_pack_definition(name, raw, source)
        registry[normalized["name"]] = {
            "enabled_by_default": normalized["enabled_by_default"],
            "items": normalized["items"],
        }
    return registry


def read_pack_registry() -> dict[str, dict[str, object]]:
    registry: dict[str, dict[str, object]] = {}
    for pack_file in sorted(PACKS_DIR.glob("*/pack.json")):
        data = json.loads(pack_file.read_text(encoding="utf-8"))
        normalized = normalize_pack_definition(pack_file.parent.name, data, pack_file)
        registry[normalized["name"]] = {
            "enabled_by_default": normalized["enabled_by_default"],
            "items": normalized["items"],
        }
    if registry:
        return registry
    return normalize_legacy_registry(json.loads(PACKS_FILE.read_text(encoding="utf-8")), PACKS_FILE)


def pack_state_path(project: Path) -> Path:
    return project / ".chef" / "enabled-packs.json"


def read_enabled_packs(project: Path) -> dict[str, object]:
    path = pack_state_path(project)
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
        enabled = state.get("enabled") if isinstance(state, dict) else None
        if not isinstance(enabled, list) or any(
            not isinstance(item, str) or not item for item in enabled
        ):
            raise ValueError(
                f"Invalid enabled pack state at {path}: "
                "enabled must be a list of non-empty strings."
            )
        return {"enabled": enabled}

    registry = read_pack_registry()
    defaults = sorted(
        name
        for name, meta in registry.items()
        if meta.get("enabled_by_default") or meta.get("default")
    )
    return {"enabled": defaults}


def write_enabled_packs(project: Path, state: dict[str, object]) -> None:
    write_file(pack_state_path(project), json.dumps(state, indent=2) + "\n")
