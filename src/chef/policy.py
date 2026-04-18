from __future__ import annotations

import json
from pathlib import Path

from chef import packs as pack_ops
from chef.paths import ROOT


def _project_path_value(project: Path, target: Path) -> str:
    project = project.resolve()
    target = target.expanduser().resolve()
    try:
        return str(target.relative_to(project))
    except ValueError:
        return str(target)


def _load_manifest(project: Path) -> dict[str, str] | None:
    path = project / ".chef" / "chef.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("vault"), str):
        return None
    if not isinstance(data.get("host"), str):
        return None
    return {"vault": data["vault"], "host": data["host"]}


def _resolve_vault_path(project: Path) -> Path:
    manifest = _load_manifest(project)
    if not manifest:
        return project / "knowledge-vault"
    raw = Path(manifest["vault"]).expanduser()
    if raw.is_absolute():
        return raw.resolve()
    return (project / raw).resolve()


def _claude_commands(project: Path) -> list[str]:
    runtime = project / ".claude" / "commands" / "chef"
    source = runtime if runtime.exists() else ROOT / "adapters" / "claude" / "commands"
    return [f"/{path.stem}" for path in sorted(source.glob("*.md"))]


def _enabled_skill_items(project: Path, host: str) -> list[str]:
    items = pack_ops.resolve_enabled_items(project, host=host)
    return [str(item["id"]) for item in items]


def _format_list(items: list[str], prefix: str = "") -> str:
    if not items:
        return "- none\n"
    return "\n".join(f"- `{prefix}{item}`" for item in items) + "\n"


def render_codex_policy(project: Path) -> str:
    vault_path = _resolve_vault_path(project)
    graph_index = _project_path_value(
        project, vault_path / "Graphify" / "graphify-out" / "wiki" / "index.md"
    )
    graph_report = _project_path_value(
        project, vault_path / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"
    )
    skills = _enabled_skill_items(project, "codex")
    skill_lines = _format_list(skills, prefix="$")
    return (
        "# Chef Codex Policy\n\n"
        "Chef manages this file as the project policy and central runtime index for Codex.\n\n"
        "## Readable Persian Text\n\n"
        "- When you reply in Persian, write the Persian text normally.\n"
        "- Put each English section, number, code snippet, version name, or any "
        "left-to-right phrase on a separate line.\n"
        "- Then continue the Persian text again on the next line.\n"
        "- For English text, use normal left-to-right writing.\n\n"
        "## Tarzan Persona\n\n"
        "- Style: 3-6 word sentences. No articles (the), no linking verbs (is, "
        "am, are), no filler, no \"then\". No preamble or pleasantries. No "
        "narration; just act.\n"
        "- Example: \"Me fix code\" (not \"I will fix the code\").\n"
        "- Workflow: Interpret, Permission, Act, Conclude.\n\n"
        "## Graph-First Rule\n\n"
        f"- Read `{graph_index}` first.\n"
        f"- Read `{graph_report}` next.\n"
        "- Read raw source only when the graph output does not answer the task "
        "or the user explicitly asks.\n"
        "- Treat repo-root `graphify-out/` as a compatibility alias only.\n"
        "- After modifying code files in this session, run `graphify update .`.\n\n"
        "## Skills And Commands\n\n"
        "- Project runtime root: `.codex/skills`\n"
        "- Project plugin root: `.codex-plugin`\n"
        "- Enabled Chef skills for this project:\n"
        f"{skill_lines}"
    )


def render_claude_policy(project: Path) -> str:
    vault_path = _resolve_vault_path(project)
    graph_index = _project_path_value(
        project, vault_path / "Graphify" / "graphify-out" / "wiki" / "index.md"
    )
    graph_report = _project_path_value(
        project, vault_path / "Graphify" / "graphify-out" / "GRAPH_REPORT.md"
    )
    commands = _claude_commands(project)
    command_lines = _format_list(commands)
    skills = _enabled_skill_items(project, "claude")
    skill_lines = _format_list(skills)
    return (
        "# Chef Claude Policy\n\n"
        "Chef manages this file as the project policy and central runtime index for Claude.\n\n"
        "## Readable Persian Text\n\n"
        "- When you reply in Persian, write the Persian text normally.\n"
        "- Put each English section, number, code snippet, version name, or any "
        "left-to-right phrase on a separate line.\n"
        "- Then continue the Persian text again on the next line.\n"
        "- For English text, use normal left-to-right writing.\n\n"
        "## Tarzan Persona\n\n"
        "- Style: 3-6 word sentences. No articles (the), no linking verbs (is, "
        "am, are), no filler, no \"then\". No preamble or pleasantries. No "
        "narration; just act.\n"
        "- Example: \"Me fix code\" (not \"I will fix the code\").\n"
        "- Workflow: Interpret, Permission, Act, Conclude.\n\n"
        "## Graph-First Rule\n\n"
        f"- Read `{graph_index}` first.\n"
        f"- Read `{graph_report}` next.\n"
        "- Read raw source only when the graph output does not answer the task "
        "or the user explicitly asks.\n"
        "- Treat repo-root `graphify-out/` as a compatibility alias only.\n"
        "- After modifying code files in this session, run `graphify update .`.\n\n"
        "## Skills And Commands\n\n"
        "- Project runtime root: `.claude/commands/chef`\n"
        "- Project skill root: `.claude/skills`\n"
        "- Project plugin root: `.claude/plugins/local`\n"
        "- Chef commands for this project:\n"
        f"{command_lines}"
        "- Enabled Chef skills for this project:\n"
        f"{skill_lines}"
    )


def sync_project_policies(project: Path, host: str) -> None:
    if host in {"claude", "both"}:
        (project / "CLAUDE.md").write_text(render_claude_policy(project), encoding="utf-8")
    if host in {"codex", "both"}:
        (project / "AGENTS.md").write_text(render_codex_policy(project), encoding="utf-8")


def build_policy_checks(project: Path, host: str) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    if host in {"claude", "both"}:
        path = project / "CLAUDE.md"
        checks["claude_policy_index"] = path.exists() and path.read_text(
            encoding="utf-8"
        ) == render_claude_policy(project)
    if host in {"codex", "both"}:
        path = project / "AGENTS.md"
        checks["codex_policy_index"] = path.exists() and path.read_text(
            encoding="utf-8"
        ) == render_codex_policy(project)
    return checks
