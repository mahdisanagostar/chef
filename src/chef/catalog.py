from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from chef.paths import CATALOG_FILE, ROOT

ALLOWED_HOSTS = {"claude", "codex"}
ALLOWED_INSTALL_METHODS = {"bundled", "manual"}
ALLOWED_SOURCE_KINDS = {
    "collection",
    "framework",
    "mcp_server",
    "plugin",
    "repo",
    "skill",
    "tool",
}


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

    source_ref = data.get("source_ref")
    if source_ref is not None and (not isinstance(source_ref, str) or not source_ref):
        raise ValueError(f"Invalid item catalog entry at {source}: source_ref must be a string.")

    source_subpath = data.get("source_subpath")
    if source_subpath is not None and (
        not isinstance(source_subpath, str) or not source_subpath.strip()
    ):
        raise ValueError(
            f"Invalid item catalog entry at {source}: source_subpath must be a string."
        )

    source_kind = data.get("source_kind")
    if source_kind is not None and source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError(
            f"Invalid item catalog entry at {source}: source_kind must be one of "
            f"{', '.join(sorted(ALLOWED_SOURCE_KINDS))}."
        )

    checksum = data.get("checksum")
    if checksum is not None and (not isinstance(checksum, str) or not checksum):
        raise ValueError(f"Invalid item catalog entry at {source}: checksum must be a string.")

    if source_subpath and method != "manual":
        raise ValueError(
            f"Invalid item catalog entry at {source}: source_subpath only applies to manual items."
        )
    if source_ref and method != "manual":
        raise ValueError(
            f"Invalid item catalog entry at {source}: source_ref only applies to manual items."
        )
    if source_url and source_subpath:
        parsed = urlparse(source_url)
        if parsed.netloc != "github.com":
            raise ValueError(
                f"Invalid item catalog entry at {source}: source_subpath requires a GitHub source."
            )

    always_installed = data.get("always_installed", False)
    if not isinstance(always_installed, bool):
        raise ValueError(
            f"Invalid item catalog entry at {source}: always_installed must be boolean."
        )

    mcp = data.get("mcp")
    if mcp is not None:
        if not isinstance(mcp, dict):
            raise ValueError(f"Invalid item catalog entry at {source}: mcp must be an object.")
        command = mcp.get("command")
        args = mcp.get("args")
        if not isinstance(command, str) or not command:
            raise ValueError(
                f"Invalid item catalog entry at {source}: mcp.command must be a non-empty string."
            )
        if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
            raise ValueError(
                f"Invalid item catalog entry at {source}: mcp.args must be a list of strings."
            )

    adapter_notes = data.get("adapter_notes")
    normalized_adapter_notes: dict[str, list[str]] = {}
    if adapter_notes is not None:
        if not isinstance(adapter_notes, dict):
            raise ValueError(
                f"Invalid item catalog entry at {source}: adapter_notes must be an object."
            )
        for host, notes in adapter_notes.items():
            if host not in ALLOWED_HOSTS:
                raise ValueError(
                    f"Invalid item catalog entry at {source}: adapter_notes keys must be "
                    f"one of {', '.join(sorted(ALLOWED_HOSTS))}."
                )
            if not isinstance(notes, list) or any(
                not isinstance(note, str) or not note for note in notes
            ):
                raise ValueError(
                    f"Invalid item catalog entry at {source}: adapter_notes.{host} must be "
                    "a list of non-empty strings."
                )
            normalized_adapter_notes[host] = list(notes)

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
        **({"source_ref": source_ref} if isinstance(source_ref, str) else {}),
        **({"source_subpath": source_subpath} if isinstance(source_subpath, str) else {}),
        **({"source_kind": source_kind} if isinstance(source_kind, str) else {}),
        **({"checksum": checksum} if isinstance(checksum, str) else {}),
        **({"mcp": {"command": mcp["command"], "args": list(mcp["args"])}} if mcp else {}),
        **({"adapter_notes": normalized_adapter_notes} if normalized_adapter_notes else {}),
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
