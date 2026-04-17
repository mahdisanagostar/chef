from __future__ import annotations

import datetime as dt
import re
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


def parse_backup_label(backup: Path) -> str:
    match = re.match(r"(?P<label>.+)-\d{8}T\d{6}Z$", backup.name)
    if not match:
        raise ValueError(f"Unrecognized backup name: {backup.name}")
    return match.group("label")


def restore_target(project: Path, home: Path, label: str) -> Path:
    if label == "claude-commands-chef":
        return home / ".claude" / "commands" / "chef"
    if label == "claude-plugin-chef":
        return home / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin"
    if label.startswith("claude-plugin-"):
        plugin_name = label.removeprefix("claude-plugin-")
        if not plugin_name:
            raise ValueError(f"Invalid claude plugin backup label: {label}")
        return home / ".claude" / "plugins" / "local" / plugin_name
    if label.startswith("claude-skill-"):
        skill_name = label.removeprefix("claude-skill-")
        if not skill_name:
            raise ValueError(f"Invalid claude skill backup label: {label}")
        return home / ".claude" / "skills" / skill_name
    if label == "project-codex-plugin":
        return project / ".codex-plugin"
    if label == "project-codex-mcp":
        return project / ".codex-plugin" / ".mcp.json"
    if label.startswith("codex-skill-"):
        skill_name = label.removeprefix("codex-skill-")
        if not skill_name:
            raise ValueError(f"Invalid codex skill backup label: {label}")
        return home / ".codex" / "skills" / skill_name
    raise ValueError(f"Unsupported backup label: {label}")


def restore_backup(project: Path, backup_path: Path, force: bool = False) -> list[str]:
    home = Path.home()
    backup = backup_path.expanduser().resolve()
    if not backup.exists():
        raise ValueError(f"Backup not found: {backup}")

    label = parse_backup_label(backup)
    target = restore_target(project, home, label)
    actions = [f"backup:{backup}"]
    if target.exists():
        if not force:
            raise ValueError(
                f"Restore target already exists: {target}. Re-run with --force to replace it."
            )
        replaced = backup_existing_path(target, home, f"restore-overwrite-{label}")
        if replaced:
            actions.append(f"backup:{replaced}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(backup), str(target))
    actions.append(str(target))
    return actions


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


def install_codex(project: Path, skill_names: set[str] | None = None) -> list[str]:
    home = Path.home()
    target = home / ".codex" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    src = ROOT / "adapters" / "codex" / "skills"
    installed: list[str] = []
    selected = None if skill_names is None else set(skill_names)
    for skill_dir in src.iterdir():
        if not skill_dir.is_dir():
            continue
        if selected is not None and skill_dir.name not in selected:
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
