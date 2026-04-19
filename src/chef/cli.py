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
from chef.install_state import merge_host_records


def detect_project(args: argparse.Namespace) -> Path:
    return Path(args.project).expanduser().resolve()


def print_json(data: dict[str, object]) -> None:
    print(json.dumps(data, indent=2))


def print_section(title: str, values: list[str]) -> None:
    print(f"{title}:")
    if not values:
        print("- none")
        return
    for value in values:
        print(f"- {value}")


def build_bundled_records(
    project: Path, host: str, items: list[dict[str, object]]
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in items:
        targets = [
            str(path)
            for path in host_install.managed_item_paths(project, host, item)
            if path.exists()
        ]
        records.append(
            external.build_install_record(
                project,
                host,
                item,
                snapshot=None,
                targets=targets,
                warnings=[],
                errors=[],
                degraded=False,
                fidelity="direct",
            )
        )
    return records


def install_host_assets(
    project: Path, host: str, items: list[dict[str, object]], offline: bool
) -> tuple[list[str], list[str], list[str], list[dict[str, object]]]:
    installed: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    bundled_items = [item for item in items if item["install"]["method"] == "bundled"]

    host_install.prune_host_items(project, host, items)

    if host == "claude":
        installed.extend(host_install.install_claude(project, bundled_items))
    else:
        installed.extend(host_install.install_codex(project, bundled_items))

    result = external.sync_external_items(project, host, items, offline=offline)
    installed.extend(result.actions)
    warnings.extend(result.warnings)
    errors.extend(result.errors)
    records = build_bundled_records(project, host, bundled_items) + result.states
    merge_host_records(project, host, records)
    return installed, warnings, errors, records


def pack_status_payload(project: Path) -> dict[str, object]:
    registry = pack_ops.read_pack_registry()
    state = pack_ops.read_enabled_packs(project)
    resolved = pack_ops.resolve_enabled_items(project)
    enabled = set(state.get("enabled", []))
    bundled = sorted(str(item["id"]) for item in resolved if item["install"]["method"] == "bundled")
    manual = sorted(str(item["id"]) for item in resolved if item["install"]["method"] == "manual")
    return {
        "enabled": sorted(enabled),
        "available": sorted(registry.keys()),
        "enabled_items": sorted(str(item["id"]) for item in resolved),
        "bundled_items": bundled,
        "manual_items": manual,
        "profiles": ["lean", "default", "full"],
    }


def render_pack_status(payload: dict[str, object]) -> None:
    print_section("Enabled packs", list(payload.get("enabled", [])))
    print_section("Available packs", list(payload.get("available", [])))
    print_section("Enabled items", list(payload.get("enabled_items", [])))
    print_section("Bundled items", list(payload.get("bundled_items", [])))
    print_section("Manual items", list(payload.get("manual_items", [])))


def render_pack_mutation(payload: dict[str, object]) -> None:
    print_section("Enabled packs", list(payload.get("enabled", [])))
    print_section("Enabled items", list(payload.get("enabled_items", [])))
    print_section("Installed paths", list(payload.get("installed", [])))
    warnings = list(payload.get("warnings", []))
    if warnings:
        print_section("Warnings", warnings)
    errors = list(payload.get("errors", []))
    if errors:
        print_section("Errors", errors)


def render_install_plan(payload: dict[str, object]) -> None:
    print("Install plan:")
    print(f"- project: {payload['project']}")
    print(f"- host: {payload['host']}")
    print(f"- offline: {payload['offline']}")
    for host, host_plan in payload["hosts"].items():
        print(f"{host}:")
        print_section("  bundled items", list(host_plan.get("bundled_items", [])))
        print_section("  manual items", list(host_plan.get("manual_items", [])))
        print_section("  prune", list(host_plan.get("prune", [])))
        builtin_mcp = list(host_plan.get("builtin_mcp", []))
        if builtin_mcp:
            print_section("  builtin MCP", builtin_mcp)


def render_verify_report(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    print("Verify summary:")
    print(f"- passed: {summary['passed']}")
    print(f"- failed: {summary['failed']}")
    for key, value in payload["checks"].items():
        status = "OK" if value else "FAIL"
        print(f"{status} {key}")
    warnings = list(payload.get("warnings", []))
    if warnings:
        print_section("Warnings", warnings)


def build_install_plan(project: Path, host: str, offline: bool) -> dict[str, object]:
    hosts: dict[str, dict[str, object]] = {}
    for target_host in ("claude", "codex"):
        if host not in {target_host, "both"}:
            continue
        items = pack_ops.resolve_enabled_items(project, host=target_host)
        enabled_ids = {str(item["id"]) for item in items}
        prune = []
        for item in host_install.managed_host_items(target_host):
            if str(item["id"]) in enabled_ids:
                continue
            prune.extend(
                str(path)
                for path in host_install.managed_item_paths(project, target_host, item)
                if path.exists()
            )
        hosts[target_host] = {
            "bundled_items": sorted(
                str(item["id"]) for item in items if item["install"]["method"] == "bundled"
            ),
            "manual_items": sorted(
                str(item["id"]) for item in items if item["install"]["method"] == "manual"
            ),
            "prune": sorted(prune),
            "builtin_mcp": (
                sorted(host_install.codex_builtin_mcp_servers(project).keys())
                if target_host == "codex"
                else []
            ),
        }
    return {
        "project": str(project),
        "host": host,
        "offline": offline,
        "hosts": hosts,
    }


def build_verify_report(project: Path, manifest: dict[str, str]) -> dict[str, object]:
    checks = scaffold.build_verify_checks(project, manifest)
    checks.update(policy_ops.build_policy_checks(project, manifest["host"]))
    warnings: list[str] = []

    graph_state = graphify_ops.graph_status(project)
    if not graph_state["graph_exists"]:
        warnings.append(
            "Graphify graph.json missing. "
            "Run `chef graph-refresh --project . --execute`."
        )
    elif graph_state["stale"]:
        warnings.append(f"Graphify output stale: {graph_state['reason']}")

    if manifest["host"] in {"claude", "both"}:
        claude_items = pack_ops.resolve_enabled_items(project, "claude")
        ext_checks, ext_warnings = external.verify_external_items_report(
            project, "claude", claude_items
        )
        checks.update(ext_checks)
        warnings.extend(ext_warnings)
    if manifest["host"] in {"codex", "both"}:
        codex_items = pack_ops.resolve_enabled_items(project, "codex")
        ext_checks, ext_warnings = external.verify_external_items_report(
            project, "codex", codex_items
        )
        checks.update(ext_checks)
        warnings.extend(ext_warnings)

    failed = sorted(key for key, value in checks.items() if not value)
    return {
        "checks": checks,
        "warnings": sorted(set(warnings)),
        "summary": {
            "passed": len(checks) - len(failed),
            "failed": len(failed),
        },
    }


def resolve_pack_names(project: Path, profile: str) -> list[str]:
    registry = pack_ops.read_pack_registry()
    if profile == "lean":
        return []
    if profile == "default":
        return sorted(
            name for name, meta in registry.items() if bool(meta.get("enabled_by_default"))
        )
    if profile == "full":
        return sorted(registry)
    raise ValueError(f"Unknown pack profile: {profile}")


def apply_pack_state(
    project: Path,
    enabled: list[str],
    offline: bool,
    json_output: bool,
) -> int:
    pack_ops.write_enabled_packs(project, {"enabled": sorted(enabled)})
    resolved = pack_ops.resolve_enabled_items(project, include_always_installed=False)

    installed: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    manifest = scaffold.load_manifest_if_present(project)
    if manifest:
        if manifest["host"] in {"claude", "both"}:
            claude_items = pack_ops.resolve_enabled_items(project, host="claude")
            host_installed, host_warnings, host_errors, _ = install_host_assets(
                project, "claude", claude_items, offline=offline
            )
            installed.extend(host_installed)
            warnings.extend(host_warnings)
            errors.extend(host_errors)
        if manifest["host"] in {"codex", "both"}:
            codex_items = pack_ops.resolve_enabled_items(project, host="codex")
            host_installed, host_warnings, host_errors, _ = install_host_assets(
                project, "codex", codex_items, offline=offline
            )
            installed.extend(host_installed)
            warnings.extend(host_warnings)
            errors.extend(host_errors)
        policy_ops.sync_project_policies(project, manifest["host"])

    payload = {
        "enabled": sorted(enabled),
        "enabled_items": sorted(str(item["id"]) for item in resolved),
        "installed": installed,
        "warnings": sorted(set(warnings)),
        "errors": sorted(set(errors)),
    }
    if json_output:
        print_json(payload)
    else:
        render_pack_mutation(payload)
    return 0 if not errors else 1


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
    if args.plan:
        try:
            payload = build_install_plan(project, args.host, args.offline)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if args.json:
            print_json(payload)
        else:
            render_install_plan(payload)
        return 0

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
        host_installed, host_warnings, host_errors, _ = install_host_assets(
            project, "claude", claude_items, offline=args.offline
        )
        installed.extend(host_installed)
        warnings.extend(host_warnings)
        errors.extend(host_errors)
    if args.host in {"codex", "both"}:
        host_installed, host_warnings, host_errors, _ = install_host_assets(
            project, "codex", codex_items, offline=args.offline
        )
        installed.extend(host_installed)
        warnings.extend(host_warnings)
        errors.extend(host_errors)
    policy_ops.sync_project_policies(project, args.host)
    print("Installed Chef assets:")
    for path in installed:
        print(f"- {path}")
    if warnings:
        print_section("Warnings", sorted(set(warnings)))
    if errors:
        print_section("Errors", sorted(set(errors)))
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
        report = build_verify_report(project, manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print_json(report)
    else:
        render_verify_report(report)
    return 0 if report["summary"]["failed"] == 0 else 1


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
    unknown = [pack for pack in args.pack if pack not in registry]
    if unknown:
        print(f"Unknown packs: {', '.join(unknown)}", file=sys.stderr)
        return 1
    enabled = sorted(set(state.get("enabled", [])) | set(args.pack))
    return apply_pack_state(project, enabled, args.offline, args.json)


def cmd_pack_disable(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        registry = pack_ops.read_pack_registry()
        state = pack_ops.read_enabled_packs(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    unknown = [pack for pack in args.pack if pack not in registry]
    if unknown:
        print(f"Unknown packs: {', '.join(unknown)}", file=sys.stderr)
        return 1
    enabled = sorted(set(state.get("enabled", [])) - set(args.pack))
    return apply_pack_state(project, enabled, args.offline, args.json)


def cmd_pack_set(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        registry = pack_ops.read_pack_registry()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    unknown = [pack for pack in args.pack if pack not in registry]
    if unknown:
        print(f"Unknown packs: {', '.join(unknown)}", file=sys.stderr)
        return 1
    return apply_pack_state(project, sorted(set(args.pack)), args.offline, args.json)


def cmd_pack_profile(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        enabled = resolve_pack_names(project, args.profile)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return apply_pack_state(project, enabled, args.offline, args.json)


def cmd_pack_status(args: argparse.Namespace) -> int:
    project = detect_project(args)
    try:
        payload = pack_status_payload(project)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        render_pack_status(payload)
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
    install_parser.add_argument("--plan", action="store_true")
    install_parser.add_argument("--json", action="store_true")
    install_parser.set_defaults(func=cmd_install)

    graph_parser = sub.add_parser("graph-refresh")
    graph_parser.add_argument("--project", required=True)
    graph_parser.add_argument("--host", choices=["auto", "claude", "codex"], default="auto")
    graph_parser.add_argument("--execute", action="store_true")
    graph_parser.set_defaults(func=cmd_graph_refresh)

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--project", required=True)
    verify_parser.add_argument("--json", action="store_true")
    verify_parser.set_defaults(func=cmd_verify)

    publish_parser = sub.add_parser("publish-github")
    publish_parser.add_argument("--project", required=True)
    publish_parser.add_argument("--owner", required=True)
    publish_parser.add_argument("--repo", default="chef")
    publish_parser.set_defaults(func=cmd_publish_github)

    enable_parser = sub.add_parser("pack-enable")
    enable_parser.add_argument("--project", required=True)
    enable_parser.add_argument("--offline", action="store_true")
    enable_parser.add_argument("--json", action="store_true")
    enable_parser.add_argument("--pack", action="append", required=True)
    enable_parser.set_defaults(func=cmd_pack_enable)

    disable_parser = sub.add_parser("pack-disable")
    disable_parser.add_argument("--project", required=True)
    disable_parser.add_argument("--offline", action="store_true")
    disable_parser.add_argument("--json", action="store_true")
    disable_parser.add_argument("--pack", action="append", required=True)
    disable_parser.set_defaults(func=cmd_pack_disable)

    set_parser = sub.add_parser("pack-set")
    set_parser.add_argument("--project", required=True)
    set_parser.add_argument("--offline", action="store_true")
    set_parser.add_argument("--json", action="store_true")
    set_parser.add_argument("--pack", action="append", default=[])
    set_parser.set_defaults(func=cmd_pack_set)

    profile_parser = sub.add_parser("pack-profile")
    profile_parser.add_argument("--project", required=True)
    profile_parser.add_argument("--offline", action="store_true")
    profile_parser.add_argument("--json", action="store_true")
    profile_parser.add_argument("--profile", choices=["lean", "default", "full"], required=True)
    profile_parser.set_defaults(func=cmd_pack_profile)

    status_parser = sub.add_parser("pack-status")
    status_parser.add_argument("--project", required=True)
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(func=cmd_pack_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
