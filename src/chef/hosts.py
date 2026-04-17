from __future__ import annotations

import datetime as dt
import re
import shutil
from pathlib import Path

from chef.paths import (
    ROOT,
    backups_dir,
    claude_commands_dir,
    claude_plugin_dir,
    claude_plugin_manifest_dir,
    claude_skill_dir,
    codex_mcp_file,
    codex_plugin_dir,
    codex_skill_dir,
)


def backup_root(project: Path) -> Path:
    return backups_dir(project)


def timestamp_label() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_existing_path(project: Path, target: Path, label: str) -> str | None:
    if not target.exists():
        return None
    backup_dir = backup_root(project)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{label}-{timestamp_label()}"
    shutil.move(str(target), str(backup_path))
    return str(backup_path)


def parse_backup_label(backup: Path) -> str:
    match = re.match(r"(?P<label>.+)-\d{8}T\d{6}Z$", backup.name)
    if not match:
        raise ValueError(f"Unrecognized backup name: {backup.name}")
    return match.group("label")


def restore_target(project: Path, label: str) -> Path:
    if label == "claude-commands-chef":
        return claude_commands_dir(project)
    if label == "claude-plugin-chef":
        return claude_plugin_manifest_dir(project, "chef")
    if label.startswith("claude-plugin-"):
        plugin_name = label.removeprefix("claude-plugin-")
        if not plugin_name:
            raise ValueError(f"Invalid claude plugin backup label: {label}")
        return claude_plugin_dir(project, plugin_name)
    if label.startswith("claude-skill-"):
        skill_name = label.removeprefix("claude-skill-")
        if not skill_name:
            raise ValueError(f"Invalid claude skill backup label: {label}")
        return claude_skill_dir(project, skill_name)
    if label == "project-codex-plugin":
        return codex_plugin_dir(project)
    if label == "project-codex-mcp":
        return codex_mcp_file(project)
    if label.startswith("codex-skill-"):
        skill_name = label.removeprefix("codex-skill-")
        if not skill_name:
            raise ValueError(f"Invalid codex skill backup label: {label}")
        return codex_skill_dir(project, skill_name)
    raise ValueError(f"Unsupported backup label: {label}")


def restore_backup(project: Path, backup_path: Path, force: bool = False) -> list[str]:
    backup = backup_path.expanduser().resolve()
    if not backup.exists():
        raise ValueError(f"Backup not found: {backup}")

    label = parse_backup_label(backup)
    target = restore_target(project, label)
    actions = [f"backup:{backup}"]
    if target.exists():
        if not force:
            raise ValueError(
                f"Restore target already exists: {target}. Re-run with --force to replace it."
            )
        replaced = backup_existing_path(project, target, f"restore-overwrite-{label}")
        if replaced:
            actions.append(f"backup:{replaced}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(backup), str(target))
    actions.append(str(target))
    return actions


def copy_asset(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
        return

    dest.mkdir(parents=True, exist_ok=True)
    target_file = dest / ("SKILL.md" if src.suffix.lower() == ".md" else src.name)
    shutil.copy2(src, target_file)


def install_bundled_skills(project: Path, host: str, items: list[dict[str, object]]) -> list[str]:
    installed: list[str] = []
    for item in items:
        item_id = str(item["id"])
        target = codex_skill_dir(project, item_id) if host == "codex" else claude_skill_dir(
            project, item_id
        )
        backup = backup_existing_path(project, target, f"{host}-skill-{item_id}")
        if backup:
            installed.append(f"backup:{backup}")
        source = ROOT / str(item["install"]["path"])
        copy_asset(source, target)
        installed.append(str(target))
    return installed


def install_claude(
    project: Path, bundled_items: list[dict[str, object]] | None = None
) -> list[str]:
    installed: list[str] = []
    command_target = claude_commands_dir(project)
    plugin_target = claude_plugin_manifest_dir(project, "chef")
    for target, label in (
        (command_target, "claude-commands-chef"),
        (plugin_target, "claude-plugin-chef"),
    ):
        backup = backup_existing_path(project, target, label)
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
    installed.extend(install_bundled_skills(project, "claude", bundled_items or []))
    return installed


def install_codex(project: Path, bundled_items: list[dict[str, object]] | None = None) -> list[str]:
    installed: list[str] = []
    installed.extend(install_bundled_skills(project, "codex", bundled_items or []))
    plugin_src = ROOT / "adapters" / "codex" / ".codex-plugin"
    plugin_dest = codex_plugin_dir(project)
    backup = backup_existing_path(project, plugin_dest, "project-codex-plugin")
    if backup:
        installed.append(f"backup:{backup}")
    shutil.copytree(plugin_src, plugin_dest)
    installed.append(str(plugin_dest))
    return installed
