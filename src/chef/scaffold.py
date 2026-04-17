from __future__ import annotations

import datetime as dt
import json
import os
import shutil
from pathlib import Path

from chef.paths import TEMPLATES

ALLOWED_HOSTS = {"claude", "codex", "both"}
REQUIRED_MANIFEST_KEYS = {"project", "host", "vault", "generated_at", "graph_index", "graph_report"}


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_file_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def read_template(*parts: str) -> str:
    return (TEMPLATES.joinpath(*parts)).read_text(encoding="utf-8")


def ensure_graph_placeholders(vault_path: Path) -> None:
    write_file_if_missing(
        vault_path / "Graphify" / "graphify-out" / "wiki" / "index.md",
        "# Graph Wiki Index\n\nGraphify output appears here after refresh.\n",
    )
    write_file_if_missing(
        vault_path / "Graphify" / "graphify-out" / "GRAPH_REPORT.md",
        "# Graph Report\n\nGraphify output appears here after refresh.\n",
    )


def ensure_vault(vault_path: Path) -> None:
    write_file_if_missing(vault_path / "Home" / "Home.md", read_template("vault", "Home", "Home.md"))
    write_file_if_missing(vault_path / "Memory" / "Memory.md", read_template("vault", "Memory", "Memory.md"))
    write_file_if_missing(vault_path / "Graphify" / "index.md", read_template("vault", "Graphify", "index.md"))
    (vault_path / "Graphify" / "graphify-out").mkdir(parents=True, exist_ok=True)
    ensure_graph_placeholders(vault_path)


def merge_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        relative = path.relative_to(src)
        target = dest / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def ensure_graphify_compat(project: Path, vault_path: Path) -> None:
    target = vault_path / "Graphify" / "graphify-out"
    compat = project / "graphify-out"

    if compat.exists() and not compat.is_symlink():
        merge_tree(compat, target)
        shutil.rmtree(compat)

    if compat.is_symlink():
        try:
            if compat.resolve() == target.resolve():
                return
        except FileNotFoundError:
            compat.unlink()

    if compat.exists():
        return

    rel_target = os.path.relpath(target, start=project)
    compat.symlink_to(rel_target)


def ensure_project_files(project: Path, host: str) -> None:
    if host in {"claude", "both"}:
        write_file_if_missing(project / "CLAUDE.md", read_template("project", "CLAUDE.md"))
    if host in {"codex", "both"}:
        write_file_if_missing(project / "AGENTS.md", read_template("project", "AGENTS.md"))
        write_file_if_missing(project / ".codex" / "config.toml", read_template("project", "codex.config.toml"))


def manifest_path_value(project: Path, target: Path) -> str:
    project = project.resolve()
    target = target.expanduser().resolve()
    try:
        return str(target.relative_to(project))
    except ValueError:
        return str(target)


def build_manifest(project: Path, host: str, vault_path: Path) -> dict[str, str]:
    return {
        "project": "chef/",
        "host": host,
        "vault": manifest_path_value(project, vault_path),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "graph_index": manifest_path_value(project, vault_path / "Graphify" / "graphify-out" / "wiki" / "index.md"),
        "graph_report": manifest_path_value(project, vault_path / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"),
    }


def write_manifest(project: Path, host: str, vault_path: Path) -> None:
    write_file(project / ".chef" / "chef.json", json.dumps(build_manifest(project, host, vault_path), indent=2) + "\n")


def manifest_path(project: Path) -> Path:
    return project / ".chef" / "chef.json"


def resolve_project_path(project: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (project / path).resolve()


def validate_manifest(data: object, source: Path | None = None) -> dict[str, str]:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid manifest at {source}: expected JSON object.")

    missing = sorted(REQUIRED_MANIFEST_KEYS.difference(data))
    if missing:
        raise ValueError(f"Invalid manifest at {source}: missing keys: {', '.join(missing)}")

    host = data.get("host")
    if not isinstance(host, str) or host not in ALLOWED_HOSTS:
        raise ValueError(f"Invalid manifest at {source}: unsupported host {host!r}")

    manifest: dict[str, str] = {}
    for key in REQUIRED_MANIFEST_KEYS:
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Invalid manifest at {source}: {key} must be a non-empty string.")
        manifest[key] = value
    return manifest


def load_manifest(project: Path) -> dict[str, str]:
    path = manifest_path(project)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid manifest at {path}: {exc.msg}") from exc
    return validate_manifest(data, source=path)


def load_manifest_if_present(project: Path) -> dict[str, str] | None:
    path = manifest_path(project)
    if not path.exists():
        return None
    return load_manifest(project)


def resolved_vault_dir(project: Path) -> Path:
    manifest = load_manifest_if_present(project)
    if manifest:
        return resolve_project_path(project, manifest["vault"])
    return project / "knowledge-vault"


def build_verify_checks(project: Path, manifest: dict[str, str]) -> dict[str, bool]:
    host = manifest.get("host", "both")
    vault_path = resolve_project_path(project, manifest["vault"])
    return {
        "CLAUDE.md": host not in {"claude", "both"} or (project / "CLAUDE.md").exists(),
        "AGENTS.md": host not in {"codex", "both"} or (project / "AGENTS.md").exists(),
        ".codex/config.toml": host not in {"codex", "both"} or (project / ".codex" / "config.toml").exists(),
        "vault_home": (vault_path / "Home" / "Home.md").exists(),
        "vault_memory": (vault_path / "Memory" / "Memory.md").exists(),
        "graph_index_page": (vault_path / "Graphify" / "index.md").exists(),
        "graph_output_dir": (vault_path / "Graphify" / "graphify-out").exists(),
    }
