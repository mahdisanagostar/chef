from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from chef import graphify as graphify_ops
from chef import hosts as host_install
from chef import packs as pack_ops
from chef import scaffold


def detect_project(args: argparse.Namespace) -> Path:
    return Path(args.project).expanduser().resolve()


def cmd_init(args: argparse.Namespace) -> int:
    project = detect_project(args)
    project.mkdir(parents=True, exist_ok=True)
    if args.vault == "existing" and not args.vault_path:
        print("Existing vault mode requires --vault-path.", file=sys.stderr)
        return 1
    vault_path = (
        Path(args.vault_path).expanduser().resolve()
        if args.vault_path
        else project / "knowledge-vault"
    )
    if args.vault == "existing" and not vault_path.exists():
        print(f"Existing vault path not found: {vault_path}", file=sys.stderr)
        return 1
    scaffold.ensure_vault(vault_path)
    scaffold.ensure_graphify_compat(project, vault_path)
    scaffold.ensure_project_files(project, args.host)
    scaffold.write_manifest(project, args.host, vault_path)
    try:
        pack_ops.write_enabled_packs(project, pack_ops.read_enabled_packs(project))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Initialized CHEF project at {project}")
    print(f"Vault path: {vault_path}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    project = detect_project(args)
    installed: list[str] = []
    if args.host in {"claude", "both"}:
        installed.extend(host_install.install_claude(project))
    if args.host in {"codex", "both"}:
        installed.extend(host_install.install_codex(project))
    print("Installed CHEF assets:")
    for path in installed:
        print(f"- {path}")
    return 0


def cmd_restore_backup(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        restored = host_install.restore_backup(project, Path(args.backup), force=args.force)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Restore actions:")
    for path in restored:
        print(f"- {path}")
    return 0


def cmd_graph_refresh(args: argparse.Namespace) -> int:
    project = detect_project(args)
    if not scaffold.manifest_path(project).exists():
        print("Missing .chef/chef.json. Run `chef init` first.", file=sys.stderr)
        return 1
    try:
        manifest = scaffold.load_manifest(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    vault_path = scaffold.resolve_project_path(project, manifest["vault"])
    scaffold.ensure_vault(vault_path)
    scaffold.ensure_graphify_compat(project, vault_path)
    graphify_bin = graphify_ops.resolve_graphify_binary(project)
    install_sequence = [[graphify_bin, args.host, "install"]]
    update_command = [graphify_bin, "update", "."]
    if args.execute:
        for command in install_sequence + [update_command]:
            code = graphify_ops.run_graphify_command(command, project)
            if code == 127:
                print("Graphify not installed. CHEF kept scaffold only.", file=sys.stderr)
                return 1
            if code != 0:
                return code
        graphify_ops.sync_graphify_outputs(project, vault_path)
        print("Graphify commands executed.")
        return 0
    print("Graph refresh scaffold ready.")
    print("Suggested commands:")
    for command in install_sequence + [update_command]:
        print(" ".join(command))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project = detect_project(args)
    if not scaffold.manifest_path(project).exists():
        print("Missing .chef/chef.json", file=sys.stderr)
        return 1
    try:
        manifest = scaffold.load_manifest(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    checks = scaffold.build_verify_checks(project, manifest)
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
    try:
        registry = pack_ops.read_pack_registry()
        state = pack_ops.read_enabled_packs(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    enabled = set(state.get("enabled", []))
    unknown = [pack for pack in args.pack if pack not in registry]
    if unknown:
        print(f"Unknown packs: {', '.join(unknown)}", file=sys.stderr)
        return 1
    enabled.update(args.pack)
    pack_ops.write_enabled_packs(project, {"enabled": sorted(enabled)})
    print(json.dumps({"enabled": sorted(enabled)}, indent=2))
    return 0


def cmd_pack_status(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        registry = pack_ops.read_pack_registry()
        state = pack_ops.read_enabled_packs(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
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

    restore_parser = sub.add_parser("restore-backup")
    restore_parser.add_argument("--project", required=True)
    restore_parser.add_argument("--backup", required=True)
    restore_parser.add_argument("--force", action="store_true")
    restore_parser.set_defaults(func=cmd_restore_backup)

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
