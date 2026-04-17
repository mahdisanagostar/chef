from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

from chef.paths import ROOT


def backup_root(home: Path) -> Path:
    return home / ".chef" / "backups"


def timestamp_label() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_existing_path(target: Path, home: Path, label: str) -> str | None:
    if not target.exists():
        return None
    backup_dir = backup_root(home)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{label}-{timestamp_label()}"
    shutil.move(str(target), str(backup_path))
    return str(backup_path)


def install_claude(project: Path) -> list[str]:
    home = Path.home()
    installed: list[str] = []
    command_target = home / ".claude" / "commands" / "chef"
    plugin_target = home / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin"
    for target, label in (
        (command_target, "claude-commands-chef"),
        (plugin_target, "claude-plugin-chef"),
    ):
        backup = backup_existing_path(target, home, label)
        if backup:
            installed.append(f"backup:{backup}")
    command_target.mkdir(parents=True, exist_ok=True)
    plugin_target.mkdir(parents=True, exist_ok=True)
    src = ROOT / "adapters" / "claude" / "commands"
    for path in src.glob("*.md"):
        shutil.copy2(path, command_target / path.name)
    shutil.copy2(
        ROOT / "adapters" / "claude" / ".claude-plugin" / "plugin.json",
        plugin_target / "plugin.json",
    )
    installed.extend([str(command_target), str(plugin_target)])
    return installed


def install_codex(project: Path) -> list[str]:
    home = Path.home()
    target = home / ".codex" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    src = ROOT / "adapters" / "codex" / "skills"
    installed: list[str] = []
    for skill_dir in src.iterdir():
        if not skill_dir.is_dir():
            continue
        dest = target / skill_dir.name
        backup = backup_existing_path(dest, home, f"codex-skill-{skill_dir.name}")
        if backup:
            installed.append(f"backup:{backup}")
        shutil.copytree(skill_dir, dest)
        installed.append(str(dest))

    plugin_src = ROOT / "adapters" / "codex" / ".codex-plugin"
    plugin_dest = project / ".codex-plugin"
    backup = backup_existing_path(plugin_dest, home, "project-codex-plugin")
    if backup:
        installed.append(f"backup:{backup}")
    shutil.copytree(plugin_src, plugin_dest)
    installed.append(str(plugin_dest))
    return installed
