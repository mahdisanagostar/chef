from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import cast

from chef import scaffold

IGNORED_VAULT_DIRS = {".obsidian"}


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


def is_vault_note(relative: Path) -> bool:
    if relative.suffix.lower() != ".md":
        return False
    parts = relative.parts
    if any(part in IGNORED_VAULT_DIRS for part in parts):
        return False
    return tuple(parts[:2]) != ("Graphify", "graphify-out")


def vault_note_paths(project_dir: str = ".") -> list[Path]:
    vault = vault_dir(project_dir)
    if not vault.exists():
        return []
    paths = [path for path in vault.rglob("*.md") if is_vault_note(path.relative_to(vault))]
    return sorted(paths)


def note_rel_path(path: Path, vault: Path) -> str:
    return path.relative_to(vault).as_posix()


def note_identifier(path: Path, vault: Path) -> str:
    return cast(str, PurePosixPath(note_rel_path(path, vault)).with_suffix("").as_posix())


def resolve_note_path(
    project_dir: str = ".",
    note: str = "",
    create: bool = False,
) -> tuple[Path | None, str | None]:
    vault = vault_dir(project_dir)
    raw_note = note.strip()
    if not raw_note:
        return None, "Note path is required."

    preferred = Path(raw_note)
    if preferred.suffix.lower() != ".md":
        preferred = preferred.with_suffix(".md")
    target = (vault / preferred).resolve()
    if vault not in target.parents and target != vault:
        return None, "Note path escapes vault root."
    if target.exists():
        return target, None
    if create:
        return target, None

    normalized = PurePosixPath(raw_note).with_suffix("").as_posix()
    note_paths = vault_note_paths(project_dir)
    exact_matches = [path for path in note_paths if note_identifier(path, vault) == normalized]
    if len(exact_matches) == 1:
        return exact_matches[0], None
    stem_matches = [path for path in note_paths if path.stem == Path(raw_note).stem]
    if len(stem_matches) == 1:
        return stem_matches[0], None
    if len(stem_matches) > 1:
        matches = ", ".join(note_rel_path(path, vault) for path in stem_matches)
        return None, f"Ambiguous note path: {raw_note}. Matches: {matches}"
    return None, f"Missing note: {raw_note}"


def read_text(path: Path) -> str:
    if not path.exists():
        return f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


def resolve_repo_paths(project_dir: str = ".", raw_paths: str = "") -> list[Path]:
    project = resolve_project(project_dir)
    resolved: list[Path] = []
    for line in raw_paths.splitlines():
        raw = line.strip()
        if not raw:
            continue
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = project / candidate
        candidate = candidate.resolve()
        if project == candidate or project in candidate.parents:
            resolved.append(candidate)
    return resolved


def read_path_snippets(project_dir: str = ".", raw_paths: str = "", max_lines: int = 40) -> str:
    project = resolve_project(project_dir)
    sections: list[str] = []
    for path in resolve_repo_paths(project_dir, raw_paths):
        try:
            relative = path.relative_to(project)
        except ValueError:
            relative = path
        if not path.exists() or path.is_dir():
            sections.append(f"{relative}\nMissing file.")
            continue
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        preview = "\n".join(lines[:max_lines])
        sections.append(f"{relative}\n{preview}")
    return "\n\n".join(sections) if sections else "No matching files."


def report_excerpt(
    project_dir: str = ".",
    keywords: tuple[str, ...] = (),
    limit: int = 20,
) -> str:
    report = read_text(graph_report_path(project_dir))
    if report.startswith("Missing file:"):
        return report
    if not keywords:
        lines = [line for line in report.splitlines() if line.strip()]
        return "\n".join(lines[:limit])
    matches = [
        line
        for line in report.splitlines()
        if any(keyword.lower() in line.lower() for keyword in keywords)
    ]
    if not matches:
        return "No matching graph report lines."
    return "\n".join(matches[:limit])
