from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"
PACKS_FILE = ROOT / "core" / "packs.json"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_template(*parts: str) -> str:
    return (TEMPLATES.joinpath(*parts)).read_text(encoding="utf-8")


def ensure_vault(vault_path: Path) -> None:
    write_file(vault_path / "Home" / "Home.md", read_template("vault", "Home", "Home.md"))
    write_file(vault_path / "Memory" / "Memory.md", read_template("vault", "Memory", "Memory.md"))
    write_file(vault_path / "Graphify" / "index.md", read_template("vault", "Graphify", "index.md"))
    (vault_path / "Graphify" / "graphify-out").mkdir(parents=True, exist_ok=True)
    ensure_graph_placeholders(vault_path)


def ensure_graph_placeholders(vault_path: Path) -> None:
    write_file(
        vault_path / "Graphify" / "graphify-out" / "wiki" / "index.md",
        "# Graph Wiki Index\n\nGraphify output appears here after refresh.\n",
    )
    write_file(
        vault_path / "Graphify" / "graphify-out" / "GRAPH_REPORT.md",
        "# Graph Report\n\nGraphify output appears here after refresh.\n",
    )


def merge_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        relative = path.relative_to(src)
        target = dest / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def ensure_graphify_compat(project: Path, vault_path: Path) -> None:
    target = vault_path / "Graphify" / "graphify-out"
    compat = project / "graphify-out"

    if compat.exists() and not compat.is_symlink():
        merge_tree(compat, target)
        shutil.rmtree(compat)

    if compat.is_symlink():
        try:
            if compat.resolve() == target.resolve():
                return
        except FileNotFoundError:
            compat.unlink()

    if compat.exists():
        return

    rel_target = os.path.relpath(target, start=project)
    compat.symlink_to(rel_target)


def ensure_project_files(project: Path, host: str) -> None:
    if host in {"claude", "both"}:
        write_file(project / "CLAUDE.md", read_template("project", "CLAUDE.md"))
    if host in {"codex", "both"}:
        write_file(project / "AGENTS.md", read_template("project", "AGENTS.md"))
        write_file(project / ".codex" / "config.toml", read_template("project", "codex.config.toml"))


def write_manifest(project: Path, host: str, vault_path: Path) -> None:
    manifest = {
        "project": "chef/",
        "host": host,
        "vault": "knowledge-vault",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "graph_index": "knowledge-vault/Graphify/graphify-out/wiki/index.md",
        "graph_report": "knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md",
    }
    write_file(project / ".chef" / "chef.json", json.dumps(manifest, indent=2) + "\n")


def resolve_project_path(project: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    if value == "knowledge-vault":
        return project / value
    return project / value


def read_pack_registry() -> dict[str, dict[str, object]]:
    return json.loads(PACKS_FILE.read_text(encoding="utf-8"))


def pack_state_path(project: Path) -> Path:
    return project / ".chef" / "enabled-packs.json"


def read_enabled_packs(project: Path) -> dict[str, object]:
    path = pack_state_path(project)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    registry = read_pack_registry()
    defaults = sorted(name for name, meta in registry.items() if meta.get("enabled_by_default") or meta.get("default"))
    return {"enabled": defaults}


def write_enabled_packs(project: Path, state: dict[str, object]) -> None:
    write_file(pack_state_path(project), json.dumps(state, indent=2) + "\n")


def detect_project(args: argparse.Namespace) -> Path:
    return Path(args.project).expanduser().resolve()


def cmd_init(args: argparse.Namespace) -> int:
    project = detect_project(args)
    project.mkdir(parents=True, exist_ok=True)
    if args.vault == "existing" and not args.vault_path:
        print("Existing vault mode requires --vault-path.", file=sys.stderr)
        return 1
    vault_path = Path(args.vault_path).expanduser().resolve() if args.vault_path else project / "knowledge-vault"
    ensure_vault(vault_path)
    ensure_graphify_compat(project, vault_path)
    ensure_project_files(project, args.host)
    write_manifest(project, args.host, vault_path)
    write_enabled_packs(project, read_enabled_packs(project))
    print(f"Initialized CHEF project at {project}")
    print(f"Vault path: {vault_path}")
    return 0


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


def cmd_install(args: argparse.Namespace) -> int:
    project = detect_project(args)
    installed: list[str] = []
    if args.host in {"claude", "both"}:
        installed.extend(install_claude(project))
    if args.host in {"codex", "both"}:
        installed.extend(install_codex(project))
    print("Installed CHEF assets:")
    for path in installed:
        print(f"- {path}")
    return 0


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


def cmd_graph_refresh(args: argparse.Namespace) -> int:
    project = detect_project(args)
    manifest_path = project / ".chef" / "chef.json"
    if not manifest_path.exists():
        print("Missing .chef/chef.json. Run `chef init` first.", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    vault_path = resolve_project_path(project, manifest["vault"])
    ensure_vault(vault_path)
    ensure_graphify_compat(project, vault_path)
    graphify_bin = resolve_graphify_binary(project)
    install_sequence = [[graphify_bin, args.host, "install"]]
    update_command = [graphify_bin, "update", "."]
    if args.execute:
        for command in install_sequence + [update_command]:
            code = run_graphify_command(command, project)
            if code == 127:
                print("Graphify not installed. CHEF kept scaffold only.", file=sys.stderr)
                return 1
            if code != 0:
                return code
        sync_graphify_outputs(project, vault_path)
        print("Graphify commands executed.")
        return 0
    print("Graph refresh scaffold ready.")
    print("Suggested commands:")
    for command in install_sequence + [update_command]:
        print(" ".join(command))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project = detect_project(args)
    manifest_path = project / ".chef" / "chef.json"
    if not manifest_path.exists():
        print("Missing .chef/chef.json", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = {
        "CLAUDE.md": (project / "CLAUDE.md").exists(),
        "AGENTS.md": (project / "AGENTS.md").exists(),
        ".codex/config.toml": (project / ".codex" / "config.toml").exists(),
        "vault_home": (resolve_project_path(project, manifest["vault"]) / "Home" / "Home.md").exists(),
        "vault_memory": (resolve_project_path(project, manifest["vault"]) / "Memory" / "Memory.md").exists(),
        "graph_index_page": (resolve_project_path(project, manifest["vault"]) / "Graphify" / "index.md").exists(),
        "graph_output_dir": (resolve_project_path(project, manifest["vault"]) / "Graphify" / "graphify-out").exists(),
    }
    print(json.dumps(checks, indent=2))
    return 0 if all(checks.values()) else 1


def cmd_publish_github(args: argparse.Namespace) -> int:
    project = detect_project(args)
    owner = args.owner
    repo = args.repo
    remote = f"git@github.com:{owner}/{repo}.git"
    print(f"Suggested remote: {remote}")
    print("Run these commands:")
    print(f"git -C {project} init")
    print(f"git -C {project} add .")
    print(f"git -C {project} commit -m 'Initial CHEF scaffold'")
    print(f"gh repo create {owner}/{repo} --public --source {project} --remote origin --push")
    return 0


def cmd_pack_enable(args: argparse.Namespace) -> int:
    project = detect_project(args)
    registry = read_pack_registry()
    state = read_enabled_packs(project)
    enabled = set(state.get("enabled", []))
    unknown = [pack for pack in args.pack if pack not in registry]
    if unknown:
        print(f"Unknown packs: {', '.join(unknown)}", file=sys.stderr)
        return 1
    enabled.update(args.pack)
    write_enabled_packs(project, {"enabled": sorted(enabled)})
    print(json.dumps({"enabled": sorted(enabled)}, indent=2))
    return 0


def cmd_pack_status(args: argparse.Namespace) -> int:
    project = detect_project(args)
    registry = read_pack_registry()
    state = read_enabled_packs(project)
    enabled = set(state.get("enabled", []))
    output = {
        "enabled": sorted(enabled),
        "available": sorted(registry.keys()),
    }
    print(json.dumps(output, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chef")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init")
    init_parser.add_argument("--project", required=True)
    init_parser.add_argument("--host", choices=["claude", "codex", "both"], default="both")
    init_parser.add_argument("--vault", choices=["new", "existing"], default="new")
    init_parser.add_argument("--vault-path")
    init_parser.set_defaults(func=cmd_init)

    install_parser = sub.add_parser("install")
    install_parser.add_argument("--project", required=True)
    install_parser.add_argument("--host", choices=["claude", "codex", "both"], default="both")
    install_parser.set_defaults(func=cmd_install)

    graph_parser = sub.add_parser("graph-refresh")
    graph_parser.add_argument("--project", required=True)
    graph_parser.add_argument("--host", choices=["claude", "codex"], default="claude")
    graph_parser.add_argument("--execute", action="store_true")
    graph_parser.set_defaults(func=cmd_graph_refresh)

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--project", required=True)
    verify_parser.set_defaults(func=cmd_verify)

    publish_parser = sub.add_parser("publish-github")
    publish_parser.add_argument("--project", required=True)
    publish_parser.add_argument("--owner", required=True)
    publish_parser.add_argument("--repo", default="chef")
    publish_parser.set_defaults(func=cmd_publish_github)

    enable_parser = sub.add_parser("pack-enable")
    enable_parser.add_argument("--project", required=True)
    enable_parser.add_argument("--pack", action="append", required=True)
    enable_parser.set_defaults(func=cmd_pack_enable)

    status_parser = sub.add_parser("pack-status")
    status_parser.add_argument("--project", required=True)
    status_parser.set_defaults(func=cmd_pack_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
