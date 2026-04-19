#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
from pathlib import Path

IGNORED_NAMES = {"__pycache__", ".DS_Store"}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    root = skill_root()
    if (
        root.parent.name == "skills"
        and root.parent.parent.name == "shared"
        and root.parent.parent.parent.name == "adapters"
    ):
        return root.parent.parent.parent.parent
    return root.parent


def default_mirror() -> Path | None:
    override = os.environ.get("TALKCRAFT_MIRROR")
    if override:
        return Path(override).expanduser().resolve()

    repository = repo_root()
    source = skill_root()

    standalone_candidate = repository.parent / "talkcraft" / "talkcraft"
    chef_candidate = repository.parent / "chef" / "adapters" / "shared" / "skills" / "talkcraft"

    if source.parent == repository and chef_candidate.exists():
        return chef_candidate.resolve()
    if standalone_candidate.exists():
        return standalone_candidate.resolve()
    return None


def iter_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in IGNORED_NAMES for part in path.parts)
    )


def relative_file_map(root: Path) -> dict[str, Path]:
    return {path.relative_to(root).as_posix(): path for path in iter_files(root)}


def compare_dirs(source: Path, target: Path) -> list[str]:
    source_map = relative_file_map(source)
    target_map = relative_file_map(target)
    issues: list[str] = []

    for relative in sorted(source_map):
        if relative not in target_map:
            issues.append(f"missing in target: {relative}")
            continue
        if not filecmp.cmp(source_map[relative], target_map[relative], shallow=False):
            issues.append(f"content differs: {relative}")

    for relative in sorted(target_map):
        if relative not in source_map:
            issues.append(f"extra in target: {relative}")

    return issues


def sync_dirs(source: Path, target: Path) -> None:
    if target.exists():
        for child in sorted(target.iterdir()):
            if child.name in IGNORED_NAMES:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    target.mkdir(parents=True, exist_ok=True)
    for path in iter_files(source):
        relative = path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check or sync a TalkCraft mirror directory.",
    )
    parser.add_argument(
        "mirror",
        nargs="?",
        help=(
            "Mirror skill directory path. Defaults to TALKCRAFT_MIRROR "
            "or a sibling Chef/TalkCraft checkout."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("check", "sync"),
        default="check",
        help="Check drift or sync the mirror from the current skill copy.",
    )
    args = parser.parse_args()

    source = skill_root()
    mirror = (
        Path(args.mirror).expanduser().resolve()
        if args.mirror
        else default_mirror()
    )
    if mirror is None:
        raise SystemExit(
            "mirror path required; pass one explicitly or set TALKCRAFT_MIRROR",
        )

    if args.mode == "sync":
        sync_dirs(source, mirror)
        print(f"synced: {source} -> {mirror}")
        return

    issues = compare_dirs(source, mirror)
    if not issues:
        print("in sync")
        return
    for issue in issues:
        print(issue)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
