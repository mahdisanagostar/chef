from __future__ import annotations

import shutil
from pathlib import Path

from chef.paths import (
    ROOT,
    claude_commands_dir,
    claude_plugin_manifest_dir,
    claude_skill_dir,
    codex_plugin_dir,
    codex_skill_dir,
)


def replace_path(target: Path) -> None:
    if not target.exists():
        return
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
        return
    target.unlink()


def copy_asset(src: Path, dest: Path) -> None:
    replace_path(dest)
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
    replace_path(command_target)
    replace_path(plugin_target)
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
    replace_path(plugin_dest)
    shutil.copytree(plugin_src, plugin_dest)
    installed.append(str(plugin_dest))
    return installed
