from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from chef import external, scaffold
from chef import graphify as graphify_ops
from chef import hosts as host_install
from chef import packs as pack_ops
from chef import policy as policy_ops


def detect_project(args: argparse.Namespace) -> Path:
    return Path(args.project).expanduser().resolve()


def install_host_assets(
    project: Path, host: str, items: list[dict[str, object]], offline: bool
) -> tuple[list[str], list[str], list[str]]:
    installed: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    bundled_items = [item for item in items if item["install"]["method"] == "bundled"]

    if host == "claude":
        installed.extend(host_install.install_claude(project, bundled_items))
    else:
        installed.extend(host_install.install_codex(project, bundled_items))

    result = external.sync_external_items(project, host, items, offline=offline)
    installed.extend(result.actions)
    warnings.extend(result.warnings)
    errors.extend(result.errors)
    return installed, warnings, errors


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
    scaffold.write_manifest(project, args.host, vault_path)
    try:
        pack_ops.write_enabled_packs(project, pack_ops.read_enabled_packs(project))
        pack_ops.resolve_enabled_items(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    scaffold.ensure_project_files(project, args.host)
    print(f"Initialized Chef project at {project}")
    print(f"Vault path: {vault_path}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    project = detect_project(args)
    codex_items: list[dict[str, object]] = []
    claude_items: list[dict[str, object]] = []
    try:
        if args.host in {"claude", "both"}:
            claude_items = pack_ops.resolve_enabled_items(project, host="claude")
        if args.host in {"codex", "both"}:
            codex_items = pack_ops.resolve_enabled_items(project, host="codex")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    installed: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    if args.host in {"claude", "both"}:
        host_installed, host_warnings, host_errors = install_host_assets(
            project, "claude", claude_items, offline=args.offline
        )
        installed.extend(host_installed)
        warnings.extend(host_warnings)
        errors.extend(host_errors)
    if args.host in {"codex", "both"}:
        host_installed, host_warnings, host_errors = install_host_assets(
            project, "codex", codex_items, offline=args.offline
        )
        installed.extend(host_installed)
        warnings.extend(host_warnings)
        errors.extend(host_errors)
    policy_ops.sync_project_policies(project, args.host)
    print("Installed Chef assets:")
    for path in installed:
        print(f"- {path}")
    warning_lines = sorted(set(warnings))
    error_lines = sorted(set(errors))
    if warning_lines:
        print("Warnings:")
        for warning in warning_lines:
            print(f"- {warning}")
    if error_lines:
        print("Errors:", file=sys.stderr)
        for error in error_lines:
            print(f"- {error}", file=sys.stderr)
        return 1
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
    resolved_host = graphify_ops.resolve_graphify_host(project, args.host, manifest["host"])
    graphify_bin = graphify_ops.resolve_graphify_binary(project)
    install_sequence = [[graphify_bin, resolved_host, "install"]]
    update_command = [graphify_bin, "update", "."]
    if args.execute:
        for command in install_sequence + [update_command]:
            code = graphify_ops.run_graphify_command(command, project)
            if code == 127:
                print("Graphify not installed. Chef kept scaffold only.", file=sys.stderr)
                return 1
            if code != 0:
                return code
        graphify_ops.sync_graphify_outputs(project, vault_path)
        print(f"Graphify host: {resolved_host}")
        print("Graphify commands executed.")
        return 0
    print("Graph refresh scaffold ready.")
    print(f"Graphify host: {resolved_host}")
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
    checks.update(policy_ops.build_policy_checks(project, manifest["host"]))
    try:
        if manifest["host"] in {"claude", "both"}:
            claude_items = pack_ops.resolve_enabled_items(project, "claude")
            checks.update(external.verify_external_items(project, "claude", claude_items))
        if manifest["host"] in {"codex", "both"}:
            codex_items = pack_ops.resolve_enabled_items(project, "codex")
            checks.update(external.verify_external_items(project, "codex", codex_items))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
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
    print(f"git -C {project} commit -m 'Initial Chef scaffold'")
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
    try:
        resolved = pack_ops.resolve_enabled_items(project, include_always_installed=False)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    installed: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    try:
        manifest = scaffold.load_manifest_if_present(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if manifest:
        if manifest["host"] in {"claude", "both"}:
            claude_items = pack_ops.resolve_enabled_items(project, host="claude")
            host_installed, host_warnings, host_errors = install_host_assets(
                project, "claude", claude_items, offline=args.offline
            )
            installed.extend(host_installed)
            warnings.extend(host_warnings)
            errors.extend(host_errors)
        if manifest["host"] in {"codex", "both"}:
            codex_items = pack_ops.resolve_enabled_items(project, host="codex")
            host_installed, host_warnings, host_errors = install_host_assets(
                project, "codex", codex_items, offline=args.offline
            )
            installed.extend(host_installed)
            warnings.extend(host_warnings)
            errors.extend(host_errors)
        policy_ops.sync_project_policies(project, manifest["host"])

    print(
        json.dumps(
            {
                "enabled": sorted(enabled),
                "enabled_items": sorted(str(item["id"]) for item in resolved),
                "installed": installed,
                "warnings": sorted(set(warnings)),
                "errors": sorted(set(errors)),
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


def cmd_pack_status(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        registry = pack_ops.read_pack_registry()
        state = pack_ops.read_enabled_packs(project)
        resolved = pack_ops.resolve_enabled_items(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    enabled = set(state.get("enabled", []))
    bundled = sorted(str(item["id"]) for item in resolved if item["install"]["method"] == "bundled")
    manual = sorted(str(item["id"]) for item in resolved if item["install"]["method"] == "manual")
    output = {
        "enabled": sorted(enabled),
        "available": sorted(registry.keys()),
        "enabled_items": sorted(str(item["id"]) for item in resolved),
        "bundled_items": bundled,
        "manual_items": manual,
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
    install_parser.add_argument("--offline", action="store_true")
    install_parser.set_defaults(func=cmd_install)

    graph_parser = sub.add_parser("graph-refresh")
    graph_parser.add_argument("--project", required=True)
    graph_parser.add_argument("--host", choices=["auto", "claude", "codex"], default="auto")
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
    enable_parser.add_argument("--offline", action="store_true")
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
