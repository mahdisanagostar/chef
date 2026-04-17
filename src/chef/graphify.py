from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from chef.scaffold import ensure_graphify_compat, merge_tree


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


def sync_graphify_outputs(project: Path, vault_path: Path) -> None:
    compat = project / "graphify-out"
    target = vault_path / "Graphify" / "graphify-out"
    ensure_graphify_compat(project, vault_path)
    if compat.is_symlink():
        return
    merge_tree(compat, target)
