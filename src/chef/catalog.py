from __future__ import annotations

import json
from pathlib import Path

from chef.paths import CATALOG_FILE, ROOT

ALLOWED_HOSTS = {"claude", "codex"}
ALLOWED_INSTALL_METHODS = {"bundled", "manual"}


def normalize_catalog_item(item_id: str, data: object, source: Path) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid item catalog entry at {source}: expected JSON object.")

    name = data.get("name", item_id)
    if not isinstance(name, str) or not name:
        raise ValueError(
            f"Invalid item catalog entry at {source}: name must be a non-empty string."
        )

    kind = data.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError(
            f"Invalid item catalog entry at {source}: kind must be a non-empty string."
        )

    hosts = data.get("hosts")
    if not isinstance(hosts, list) or not hosts or any(host not in ALLOWED_HOSTS for host in hosts):
        raise ValueError(
            f"Invalid item catalog entry at {source}: hosts must be a non-empty list of "
            f"{', '.join(sorted(ALLOWED_HOSTS))}."
        )

    install = data.get("install")
    if not isinstance(install, dict):
        raise ValueError(f"Invalid item catalog entry at {source}: install must be an object.")

    method = install.get("method")
    if method not in ALLOWED_INSTALL_METHODS:
        raise ValueError(
            f"Invalid item catalog entry at {source}: install.method must be one of "
            f"{', '.join(sorted(ALLOWED_INSTALL_METHODS))}."
        )

    path_value = install.get("path")
    if method == "bundled":
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(
                f"Invalid item catalog entry at {source}: bundled items require install.path."
            )
        bundled_path = ROOT / path_value
        if not bundled_path.exists():
            raise ValueError(
                f"Invalid item catalog entry at {source}: bundled path not found: {bundled_path}"
            )
    elif path_value is not None:
        raise ValueError(
            f"Invalid item catalog entry at {source}: install.path only applies to bundled items."
        )

    source_url = data.get("source_url")
    if method == "manual" and (not isinstance(source_url, str) or not source_url):
        raise ValueError(
            f"Invalid item catalog entry at {source}: manual items require source_url."
        )
    if source_url is not None and (not isinstance(source_url, str) or not source_url):
        raise ValueError(f"Invalid item catalog entry at {source}: source_url must be a string.")

    always_installed = data.get("always_installed", False)
    if not isinstance(always_installed, bool):
        raise ValueError(
            f"Invalid item catalog entry at {source}: always_installed must be boolean."
        )

    return {
        "id": item_id,
        "name": name,
        "kind": kind,
        "hosts": list(hosts),
        "install": {
            "method": method,
            **({"path": path_value} if isinstance(path_value, str) else {}),
        },
        **({"source_url": source_url} if isinstance(source_url, str) else {}),
        "always_installed": always_installed,
    }


def read_item_catalog() -> dict[str, dict[str, object]]:
    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid item catalog at {CATALOG_FILE}: {exc.msg}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Invalid item catalog at {CATALOG_FILE}: expected JSON object.")

    catalog: dict[str, dict[str, object]] = {}
    for item_id, raw in sorted(data.items()):
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"Invalid item catalog at {CATALOG_FILE}: item ids must be strings.")
        catalog[item_id] = normalize_catalog_item(item_id, raw, CATALOG_FILE)
    return catalog
