from __future__ import annotations

import shutil
from pathlib import Path

from chef.paths import ROOT


def install_claude(project: Path) -> list[str]:
    home = Path.home()
    command_target = home / ".claude" / "commands" / "chef"
    command_target.mkdir(parents=True, exist_ok=True)
    plugin_target = home / ".claude" / "plugins" / "local" / "chef" / ".claude-plugin"
    plugin_target.mkdir(parents=True, exist_ok=True)
    src = ROOT / "adapters" / "claude" / "commands"
    for path in src.glob("*.md"):
        shutil.copy2(path, command_target / path.name)
    shutil.copy2(ROOT / "adapters" / "claude" / ".claude-plugin" / "plugin.json", plugin_target / "plugin.json")
    return [str(command_target), str(plugin_target)]


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
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(skill_dir, dest)
        installed.append(str(dest))

    plugin_src = ROOT / "adapters" / "codex" / ".codex-plugin"
    plugin_dest = project / ".codex-plugin"
    if plugin_dest.exists():
        shutil.rmtree(plugin_dest)
    shutil.copytree(plugin_src, plugin_dest)
    installed.append(str(plugin_dest))
    return installed
