from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

from chef import scaffold
from chef.scaffold import ensure_graphify_compat, merge_tree

IGNORED_GRAPH_DIRS = {
    ".chef",
    ".claude",
    ".codex",
    ".codex-plugin",
    ".git",
    ".mypy_cache",
    ".obsidian",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "graphify-out",
    "node_modules",
}


def run_graphify_command(command: list[str], cwd: Path) -> int:
    try:
        return subprocess.run(command, cwd=cwd, check=False).returncode
    except FileNotFoundError:
        return 127


def resolve_graphify_binary(project: Path) -> str:
    local = project / ".venv" / "bin" / "graphify"
    if local.exists():
        return str(local)
    global_path = shutil.which("graphify")
    if global_path:
        return global_path
    return "graphify"


def detect_agent_host(project: Path, env: Mapping[str, str] | None = None) -> str | None:
    runtime_env = os.environ if env is None else env
    if any(key.startswith("CODEX_") and runtime_env.get(key) for key in runtime_env):
        return "codex"
    for key in ("CLAUDECODE", "CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT"):
        if runtime_env.get(key):
            return "claude"
    has_codex = (project / ".codex").exists() or (project / ".codex-plugin").exists()
    has_claude = (project / ".claude").exists() or (project / "CLAUDE.md").exists()
    if has_codex and not has_claude:
        return "codex"
    if has_claude and not has_codex:
        return "claude"
    return None


def resolve_graphify_host(
    project: Path,
    requested_host: str,
    manifest_host: str,
    env: Mapping[str, str] | None = None,
) -> str:
    if requested_host != "auto":
        return requested_host
    detected = detect_agent_host(project, env)
    if detected:
        return detected
    if manifest_host in {"claude", "codex"}:
        return manifest_host
    if (project / ".codex").exists() or (project / ".codex-plugin").exists():
        return "codex"
    return "claude"


def graph_json_path(project: Path) -> Path:
    vault = scaffold.resolved_vault_dir(project)
    return vault / "Graphify" / "graphify-out" / "graph.json"


def graph_report_file(project: Path) -> Path:
    vault = scaffold.resolved_vault_dir(project)
    return vault / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"


def _ignored_graph_path(relative: Path) -> bool:
    parts = relative.parts
    if not parts:
        return False
    if any(part in IGNORED_GRAPH_DIRS for part in parts):
        return True
    return len(parts) >= 3 and tuple(parts[:3]) == ("knowledge-vault", "Graphify", "graphify-out")


def iter_graph_inputs(project: Path) -> list[Path]:
    inputs: list[Path] = []
    for root, dirs, files in os.walk(project):
        root_path = Path(root)
        rel_root = root_path.relative_to(project)
        dirs[:] = [name for name in dirs if not _ignored_graph_path(rel_root / name)]
        for name in files:
            relative = rel_root / name
            if _ignored_graph_path(relative):
                continue
            path = root_path / name
            if path.is_symlink():
                continue
            inputs.append(path)
    return sorted(inputs)


def graph_status(project: Path, max_age_seconds: int = 0) -> dict[str, object]:
    project = project.resolve()
    graph_json = graph_json_path(project)
    report = graph_report_file(project)
    inputs = iter_graph_inputs(project)
    newest_input = max(inputs, key=lambda path: path.stat().st_mtime, default=None)
    newest_input_mtime = newest_input.stat().st_mtime if newest_input else None
    graph_mtime = graph_json.stat().st_mtime if graph_json.exists() else None

    stale = False
    reason = ""
    if not graph_json.exists():
        stale = True
        reason = "graph.json missing"
    elif newest_input_mtime is not None and newest_input_mtime > graph_mtime:
        stale = True
        reason = f"newer input file: {newest_input.relative_to(project)}"
    elif max_age_seconds > 0 and graph_mtime is not None:
        age_seconds = dt.datetime.now(tz=dt.timezone.utc).timestamp() - graph_mtime
        if age_seconds > max_age_seconds:
            stale = True
            reason = f"graph older than {max_age_seconds} seconds"

    return {
        "graph_json": str(graph_json),
        "graph_report": str(report),
        "graph_exists": graph_json.exists(),
        "graph_report_exists": report.exists(),
        "graph_updated_at": (
            dt.datetime.fromtimestamp(graph_mtime, tz=dt.timezone.utc).isoformat()
            if graph_mtime is not None
            else None
        ),
        "newest_input": str(newest_input.relative_to(project)) if newest_input else None,
        "newest_input_at": (
            dt.datetime.fromtimestamp(newest_input_mtime, tz=dt.timezone.utc).isoformat()
            if newest_input_mtime is not None
            else None
        ),
        "checked_inputs": len(inputs),
        "stale": stale,
        "reason": reason,
    }


def refresh_graph_if_stale(project: Path, max_age_seconds: int = 0) -> dict[str, object]:
    project = project.resolve()
    status_before = graph_status(project, max_age_seconds=max_age_seconds)
    if not status_before["stale"]:
        return {
            "updated": False,
            "exit_code": 0,
            "status_before": status_before,
            "status_after": status_before,
        }

    graphify_bin = resolve_graphify_binary(project)
    command = [graphify_bin, "update", "."]
    code = run_graphify_command(command, project)
    status_after = graph_status(project, max_age_seconds=max_age_seconds)
    result: dict[str, object] = {
        "updated": code == 0,
        "exit_code": code,
        "command": command,
        "status_before": status_before,
        "status_after": status_after,
    }
    if code == 127:
        result["error"] = "Graphify binary missing."
    elif code != 0:
        result["error"] = f"Graphify update failed with exit code {code}."
    return result


def sync_graphify_outputs(project: Path, vault_path: Path) -> None:
    compat = project / "graphify-out"
    target = vault_path / "Graphify" / "graphify-out"
    ensure_graphify_compat(project, vault_path)
    if compat.is_symlink():
        return
    merge_tree(compat, target)
