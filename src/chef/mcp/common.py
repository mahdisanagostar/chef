from __future__ import annotations

from pathlib import Path

from chef import scaffold


def resolve_project(project_dir: str = ".") -> Path:
    return Path(project_dir).expanduser().resolve()


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
