from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"
PACKS_DIR = ROOT / "packs"
PACKS_FILE = ROOT / "core" / "packs.json"
CATALOG_FILE = ROOT / "catalog" / "items.json"


def chef_dir(project: Path) -> Path:
    return project / ".chef"


def vendor_dir(project: Path) -> Path:
    return chef_dir(project) / "vendor"


def install_state_file(project: Path) -> Path:
    return chef_dir(project) / "install-state.json"


def claude_dir(project: Path) -> Path:
    return project / ".claude"


def claude_commands_dir(project: Path) -> Path:
    return claude_dir(project) / "commands" / "chef"


def claude_plugins_dir(project: Path) -> Path:
    return claude_dir(project) / "plugins" / "local"


def claude_plugin_dir(project: Path, item_id: str) -> Path:
    return claude_plugins_dir(project) / item_id


def claude_plugin_manifest_dir(project: Path, item_id: str) -> Path:
    return claude_plugin_dir(project, item_id) / ".claude-plugin"


def claude_skill_dir(project: Path, item_id: str) -> Path:
    return claude_dir(project) / "skills" / item_id


def codex_dir(project: Path) -> Path:
    return project / ".codex"


def codex_skill_dir(project: Path, item_id: str) -> Path:
    return codex_dir(project) / "skills" / item_id


def codex_plugin_dir(project: Path) -> Path:
    return project / ".codex-plugin"


def codex_plugin_file(project: Path) -> Path:
    return codex_plugin_dir(project) / "plugin.json"


def codex_mcp_file(project: Path) -> Path:
    return codex_plugin_dir(project) / ".mcp.json"
