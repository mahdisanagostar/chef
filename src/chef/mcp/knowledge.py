from __future__ import annotations

import re
from pathlib import PurePosixPath

from mcp.server.fastmcp import FastMCP

from chef import graphify as graphify_ops
from chef.mcp.common import (
    graph_dir,
    graph_index_path,
    graph_report_path,
    manifest_warning,
    note_identifier,
    note_rel_path,
    read_text,
    resolve_note_path,
    resolve_project,
    vault_dir,
    vault_note_paths,
)

mcp = FastMCP("chef-knowledge-mcp")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _result_warning(project_dir: str = ".") -> dict[str, str]:
    warning = manifest_warning(project_dir)
    return {"warning": warning} if warning else {}


def _first_matching_snippet(text: str, query: str) -> str:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if not compact:
        return ""
    if not query:
        return compact[:180]
    lowered = query.lower()
    for line in text.splitlines():
        if lowered in line.lower():
            return line.strip()[:180]
    index = compact.lower().find(lowered)
    if index < 0:
        return compact[:180]
    start = max(0, index - 60)
    end = min(len(compact), index + len(query) + 60)
    return compact[start:end].strip()


def _normalize_wiki_target(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0].split("#", 1)[0].strip().replace("\\", "/")
    return PurePosixPath(target).with_suffix("").as_posix()


def _note_aliases(path, vault) -> set[str]:
    relative = PurePosixPath(note_rel_path(path, vault))
    return {
        note_identifier(path, vault),
        relative.stem,
    }


@mcp.tool()
def vault_summary(project_dir: str = ".") -> str:
    vault = vault_dir(project_dir)
    lines: list[str] = []
    warning = manifest_warning(project_dir)
    if warning:
        lines.append(warning)
    lines.extend(
        [
            f"Vault: {vault}",
            f"Home: {(vault / 'Home' / 'Home.md').exists()}",
            f"Memory: {(vault / 'Memory' / 'Memory.md').exists()}",
            f"Graphify: {(vault / 'Graphify' / 'index.md').exists()}",
        ]
    )
    return "\n".join(lines)


@mcp.tool()
def read_graph_index(project_dir: str = ".") -> str:
    return read_text(graph_index_path(project_dir))


@mcp.tool()
def read_graph_report(project_dir: str = ".") -> str:
    return read_text(graph_report_path(project_dir))


@mcp.tool()
def list_graph_pages(project_dir: str = ".") -> list[str]:
    wiki_dir = graph_dir(project_dir) / "wiki"
    if not wiki_dir.exists():
        return []
    return sorted(str(path.relative_to(wiki_dir)) for path in wiki_dir.rglob("*.md"))


@mcp.tool()
def read_graph_page(project_dir: str = ".", page: str = "index.md") -> str:
    wiki_dir = graph_dir(project_dir) / "wiki"
    target = (wiki_dir / page).resolve()
    if wiki_dir not in target.parents and target != wiki_dir:
        return "Page path escapes graph wiki root."
    return read_text(target)


@mcp.tool()
def search_vault_notes(project_dir: str = ".", query: str = "", limit: int = 10) -> dict[str, object]:
    vault = vault_dir(project_dir)
    normalized = query.strip().lower()
    matches: list[dict[str, object]] = []
    for path in vault_note_paths(project_dir):
        relative = note_rel_path(path, vault)
        title = note_identifier(path, vault)
        text = path.read_text(encoding="utf-8")
        score = 0
        if normalized:
            if normalized in title.lower():
                score += 3
            if normalized in relative.lower():
                score += 2
            if normalized in text.lower():
                score += 1
            if score == 0:
                continue
        matches.append(
            {
                "path": relative,
                "title": title,
                "snippet": _first_matching_snippet(text, normalized),
                "score": score,
            }
        )
    matches.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    safe_limit = max(1, limit)
    return {
        **_result_warning(project_dir),
        "query": query,
        "count": len(matches),
        "results": matches[:safe_limit],
    }


@mcp.tool()
def read_note(project_dir: str = ".", note: str = "") -> str:
    path, error = resolve_note_path(project_dir, note)
    if error:
        return error
    assert path is not None
    vault = vault_dir(project_dir)
    sections: list[str] = []
    warning = manifest_warning(project_dir)
    if warning:
        sections.append(warning)
    sections.extend([f"Note: {note_rel_path(path, vault)}", path.read_text(encoding="utf-8")])
    return "\n\n".join(sections)


@mcp.tool()
def write_note(project_dir: str = ".", note: str = "", content: str = "", append: bool = False) -> str:
    path, error = resolve_note_path(project_dir, note, create=True)
    if error:
        return error
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if append and existing:
        separator = "" if existing.endswith("\n") or not content else "\n"
        new_text = existing + separator + content
    elif append:
        new_text = content
    else:
        new_text = content
    path.write_text(new_text, encoding="utf-8")
    vault = vault_dir(project_dir)
    action = "Appended" if append and existing else "Wrote"
    return f"{action} note: {note_rel_path(path, vault)}"


@mcp.tool()
def list_backlinks(project_dir: str = ".", note: str = "") -> dict[str, object]:
    target, error = resolve_note_path(project_dir, note)
    if error:
        return {"error": error}
    assert target is not None
    vault = vault_dir(project_dir)
    aliases = _note_aliases(target, vault)
    results: list[dict[str, str]] = []
    for path in vault_note_paths(project_dir):
        if path == target:
            continue
        text = path.read_text(encoding="utf-8")
        relative = note_rel_path(path, vault)
        match_line = ""

        for raw_target in WIKI_LINK_RE.findall(text):
            if _normalize_wiki_target(raw_target) in aliases:
                match_line = _first_matching_snippet(text, raw_target)
                break

        if not match_line:
            for link_target in MARKDOWN_LINK_RE.findall(text):
                normalized = link_target.split("#", 1)[0].strip()
                if not normalized or "://" in normalized or normalized.startswith("mailto:"):
                    continue
                resolved = (path.parent / normalized).resolve()
                if resolved == target.resolve():
                    match_line = _first_matching_snippet(text, normalized)
                    break

        if match_line:
            results.append({"path": relative, "snippet": match_line})

    results.sort(key=lambda item: item["path"])
    return {
        **_result_warning(project_dir),
        "note": note_identifier(target, vault),
        "count": len(results),
        "results": results,
    }


@mcp.tool()
def graph_status(project_dir: str = ".", max_age_seconds: int = 0) -> dict[str, object]:
    return {
        **_result_warning(project_dir),
        **graphify_ops.graph_status(
            resolve_project(project_dir), max_age_seconds=max_age_seconds
        ),
    }


@mcp.tool()
def refresh_graph_if_stale(project_dir: str = ".", max_age_seconds: int = 0) -> dict[str, object]:
    return {
        **_result_warning(project_dir),
        **graphify_ops.refresh_graph_if_stale(
            resolve_project(project_dir), max_age_seconds=max_age_seconds
        ),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
