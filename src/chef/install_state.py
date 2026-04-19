from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from chef.paths import install_state_file
from chef.scaffold import write_file

STATE_VERSION = 1


def state_key(host: str, item_id: str) -> str:
    return f"{host}:{item_id}"


def read_install_state(project: Path) -> dict[str, object]:
    path = install_state_file(project)
    if not path.exists():
        return {"version": STATE_VERSION, "items": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {"version": STATE_VERSION, "items": {}}
    items = data.get("items")
    if not isinstance(items, dict):
        items = {}
    return {
        "version": int(data.get("version", STATE_VERSION)),
        "updated_at": data.get("updated_at"),
        "items": items,
    }


def write_install_state(project: Path, state: dict[str, object]) -> None:
    payload = {
        "version": STATE_VERSION,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "items": state.get("items", {}),
    }
    write_file(install_state_file(project), json.dumps(payload, indent=2) + "\n")


def merge_host_records(project: Path, host: str, records: list[dict[str, object]]) -> None:
    state = read_install_state(project)
    items = state.get("items")
    if not isinstance(items, dict):
        items = {}

    prefix = f"{host}:"
    next_keys = {state_key(host, str(record["item_id"])) for record in records}
    for key in list(items):
        if key.startswith(prefix) and key not in next_keys:
            items.pop(key, None)

    for record in records:
        items[state_key(host, str(record["item_id"]))] = record

    state["items"] = items
    write_install_state(project, state)


def record_for(project: Path, host: str, item_id: str) -> dict[str, object] | None:
    state = read_install_state(project)
    items = state.get("items")
    if not isinstance(items, dict):
        return None
    record = items.get(state_key(host, item_id))
    return record if isinstance(record, dict) else None
