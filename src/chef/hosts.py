from __future__ import annotations

import json
import shutil
from pathlib import Path

from chef.paths import (
    ROOT,
    claude_commands_dir,
    claude_plugin_manifest_dir,
    claude_skill_dir,
    codex_mcp_file,
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


def codex_builtin_mcp_servers(project: Path) -> dict[str, dict[str, object]]:
    return {
        "chef-knowledge-mcp": {
            "command": str(project.resolve() / ".venv" / "bin" / "chef-knowledge-mcp"),
            "args": [],
        }
    }


def ensure_codex_builtin_mcp(project: Path) -> Path:
    mcp_path = codex_mcp_file(project)
    existing: dict[str, object] = {"mcpServers": {}}
    if mcp_path.exists():
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            existing = data
    servers = existing.get("mcpServers")
    if not isinstance(servers, dict):
        servers = {}
    servers.update(codex_builtin_mcp_servers(project))
    desired = json.dumps({"mcpServers": servers}, indent=2) + "\n"
    if not mcp_path.exists() or mcp_path.read_text(encoding="utf-8") != desired:
        mcp_path.write_text(desired, encoding="utf-8")
    return mcp_path


def install_codex(project: Path, bundled_items: list[dict[str, object]] | None = None) -> list[str]:
    installed: list[str] = []
    installed.extend(install_bundled_skills(project, "codex", bundled_items or []))
    plugin_src = ROOT / "adapters" / "codex" / ".codex-plugin"
    plugin_dest = codex_plugin_dir(project)
    replace_path(plugin_dest)
    shutil.copytree(plugin_src, plugin_dest)
    installed.append(str(plugin_dest))
    installed.append(str(ensure_codex_builtin_mcp(project)))
    return installed
