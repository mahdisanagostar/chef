#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


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


def validator_candidates() -> list[Path]:
    candidates: list[Path] = []
    override = os.environ.get("TALKCRAFT_QUICK_VALIDATE")
    if override:
        candidates.append(Path(override).expanduser())

    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(
            Path(codex_home)
            / "skills"
            / ".system"
            / "skill-creator"
            / "scripts"
            / "quick_validate.py",
        )

    candidates.append(
        Path.home()
        / ".codex"
        / "skills"
        / ".system"
        / "skill-creator"
        / "scripts"
        / "quick_validate.py",
    )
    return candidates


def find_validator() -> Path:
    for candidate in validator_candidates():
        if candidate.is_file():
            return candidate.resolve()
    searched = "\n".join(f"- {path}" for path in validator_candidates())
    raise SystemExit(
        "quick_validate.py not found. Checked:\n"
        f"{searched}\n"
        "Set TALKCRAFT_QUICK_VALIDATE or CODEX_HOME if needed.",
    )


def runtime_candidates() -> list[Path]:
    candidates: list[Path] = []
    override = os.environ.get("TALKCRAFT_VALIDATOR_PYTHON")
    if override:
        candidates.append(Path(override).expanduser())

    candidates.append(Path(sys.executable))

    repository = repo_root()
    candidates.append(repository / ".venv" / "bin" / "python")
    candidates.append(repository.parent / "chef" / ".venv" / "bin" / "python")

    ordered: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(candidate)
    return ordered


def supports_yaml(runtime: Path) -> bool:
    if not runtime.is_file():
        return False
    result = subprocess.run(
        [str(runtime), "-c", "import yaml"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def choose_runtime(validator: Path) -> Path:
    needs_yaml = validator.name == "quick_validate.py"
    for candidate in runtime_candidates():
        if not candidate.is_file():
            continue
        if needs_yaml and not supports_yaml(candidate):
            continue
        return candidate

    searched = "\n".join(f"- {path}" for path in runtime_candidates())
    raise SystemExit(
        "No compatible Python runtime found for validator.\n"
        f"Searched:\n{searched}\n"
        "Install PyYAML or set TALKCRAFT_VALIDATOR_PYTHON.",
    )


def main() -> None:
    target = skill_root()
    extra_args = sys.argv[1:]
    validator = find_validator()
    runtime = choose_runtime(validator)
    command = [str(runtime), str(validator), str(target), *extra_args]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
