from __future__ import annotations

import json
from pathlib import Path

from chef import scaffold


def resolve_project(project_dir: str = ".") -> Path:
    return Path(project_dir).expanduser().resolve()


def manifest_warning(project_dir: str = ".") -> str | None:
    project = resolve_project(project_dir)
    path = scaffold.manifest_path(project)
    if not path.exists():
        return "Warning: missing .chef/chef.json; using default knowledge-vault path."
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        manifest = scaffold.validate_manifest(raw, source=path)
    except (json.JSONDecodeError, ValueError) as exc:
        return f"Warning: {exc}; using default knowledge-vault path."
    vault = scaffold.resolve_project_path(project, manifest["vault"])
    if vault != project / "knowledge-vault":
        return f"Warning: manifest points to external vault: {vault}"
    return None


def vault_dir(project_dir: str = ".") -> Path:
    project = resolve_project(project_dir)
    return scaffold.resolved_vault_dir(project)


def graph_dir(project_dir: str = ".") -> Path:
    return vault_dir(project_dir) / "Graphify" / "graphify-out"


def graph_index_path(project_dir: str = ".") -> Path:
    return graph_dir(project_dir) / "wiki" / "index.md"


def graph_report_path(project_dir: str = ".") -> Path:
    return graph_dir(project_dir) / "GRAPH_REPORT.md"


def read_text(path: Path) -> str:
    if not path.exists():
        return f"Missing file: {path}"
    return path.read_text(encoding="utf-8")
