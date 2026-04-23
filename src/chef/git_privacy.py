from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from chef.paths import git_privacy_hooks_dir, git_privacy_state_file
from chef.scaffold import write_file

DEFAULT_BLOCKED_TERMS = [
    "Claude",
    "Codex",
    "ChatGPT",
    "OpenAI",
    "Copilot",
    "Gemini",
    "Bard",
    "Anthropic",
]


def _run_git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def _require_git_repo(project: Path) -> None:
    result = _run_git(project, "rev-parse", "--git-dir")
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Not a git repository."
        raise ValueError(message)


def _contains_blocked_term(text: str, blocked_terms: list[str]) -> str | None:
    lowered = text.casefold()
    for term in blocked_terms:
        if term.casefold() in lowered:
            return term
    return None


def _write_executable(path: Path, content: str) -> None:
    write_file(path, content)
    path.chmod(0o755)


def _hook_script(blocked_terms: list[str]) -> str:
    terms = json.dumps(blocked_terms, indent=2)
    return f"""#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BLOCKED_TERMS = {terms}


def contains_blocked_term(text: str) -> str | None:
    lowered = text.casefold()
    for term in BLOCKED_TERMS:
        if term.casefold() in lowered:
            return term
    return None


def git_ident(name: str) -> str:
    result = subprocess.run(
        ["git", "var", name],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Git identity lookup failed."
        raise SystemExit(message)
    return result.stdout.strip()


def check_git_identity() -> None:
    for key, label in (("GIT_AUTHOR_IDENT", "author"), ("GIT_COMMITTER_IDENT", "committer")):
        ident = git_ident(key)
        blocked = contains_blocked_term(ident)
        if blocked:
            print(
                f"Chef git privacy guard blocked {{label}} identity containing {{blocked!r}}.",
                file=sys.stderr,
            )
            raise SystemExit(1)


def main() -> int:
    check_git_identity()
    if len(sys.argv) > 1:
        message_path = Path(sys.argv[1])
        message = message_path.read_text(encoding="utf-8", errors="ignore")
        blocked = contains_blocked_term(message)
        if blocked:
            print(
                f"Chef git privacy guard blocked commit message containing {{blocked!r}}.",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _state_path(project: Path) -> Path:
    return git_privacy_state_file(project)


def read_git_privacy_state(project: Path) -> dict[str, object] | None:
    path = _state_path(project)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not bool(data.get("enabled")):
        return None
    return data


def _write_state(project: Path, state: dict[str, object]) -> None:
    write_file(_state_path(project), json.dumps(state, indent=2) + "\n")


def _write_hook_files(project: Path, blocked_terms: list[str]) -> list[str]:
    hooks_dir = git_privacy_hooks_dir(project)
    hooks_dir.mkdir(parents=True, exist_ok=True)
    script = _hook_script(blocked_terms)
    actions: list[str] = []
    for name in ("pre-commit", "commit-msg"):
        hook_path = hooks_dir / name
        _write_executable(hook_path, script)
        actions.append(str(hook_path))
    return actions


def _configure_git(project: Path, author_name: str, author_email: str, hooks_dir: Path) -> None:
    for key, value in (
        ("user.name", author_name),
        ("user.email", author_email),
        ("user.useConfigOnly", "true"),
        ("core.hooksPath", str(hooks_dir.resolve())),
    ):
        result = _run_git(project, "config", "--local", key, value)
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or f"Could not set {key}."
            raise ValueError(message)


def enable_git_privacy(
    project: Path,
    author_name: str,
    author_email: str,
    blocked_terms: list[str] | None = None,
) -> list[str]:
    _require_git_repo(project)
    terms = blocked_terms or list(DEFAULT_BLOCKED_TERMS)
    if not author_name.strip():
        raise ValueError("Author name must be a non-empty string.")
    if not author_email.strip():
        raise ValueError("Author email must be a non-empty string.")

    for value, label in ((author_name, "author name"), (author_email, "author email")):
        blocked = _contains_blocked_term(value, terms)
        if blocked:
            raise ValueError(f"{label} contains blocked term {blocked!r}.")

    hooks_dir = git_privacy_hooks_dir(project)
    actions = _write_hook_files(project, terms)
    _configure_git(project, author_name, author_email, hooks_dir)

    state = {
        "enabled": True,
        "author_name": author_name,
        "author_email": author_email,
        "blocked_terms": terms,
        "hooks_path": str(hooks_dir.resolve()),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_state(project, state)
    actions.append(str(_state_path(project)))
    return actions


def disable_git_privacy(project: Path) -> list[str]:
    _require_git_repo(project)
    hooks_dir = git_privacy_hooks_dir(project)
    actions: list[str] = []
    for key in ("core.hooksPath", "user.useConfigOnly", "user.name", "user.email"):
        _run_git(project, "config", "--local", "--unset-all", key)
    if hooks_dir.exists():
        shutil.rmtree(hooks_dir)
        actions.append(str(hooks_dir))
    state = _state_path(project)
    if state.exists():
        state.unlink()
        actions.append(str(state))
    return actions


def status_git_privacy(project: Path) -> dict[str, object]:
    state = read_git_privacy_state(project)
    hooks_dir = git_privacy_hooks_dir(project)
    commit_msg = hooks_dir / "commit-msg"
    pre_commit = hooks_dir / "pre-commit"
    return {
        "enabled": state is not None,
        "state_path": str(_state_path(project)),
        "hooks_path": str(hooks_dir),
        "hooks_path_exists": hooks_dir.exists(),
        "commit_msg_hook_exists": commit_msg.exists(),
        "pre_commit_hook_exists": pre_commit.exists(),
        "author_name": state.get("author_name") if state else None,
        "author_email": state.get("author_email") if state else None,
        "blocked_terms": state.get("blocked_terms") if state else [],
        "configured_hooks_path": _git_config_get(project, "core.hooksPath"),
        "configured_author_name": _git_config_get(project, "user.name"),
        "configured_author_email": _git_config_get(project, "user.email"),
        "configured_use_config_only": _git_config_get(project, "user.useConfigOnly"),
    }


def _git_config_get(project: Path, key: str) -> str | None:
    result = _run_git(project, "config", "--local", "--get", key)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def build_git_privacy_checks(project: Path) -> dict[str, bool]:
    state = read_git_privacy_state(project)
    if state is None:
        return {}

    hooks_dir = git_privacy_hooks_dir(project)
    expected = _hook_script(list(state.get("blocked_terms", DEFAULT_BLOCKED_TERMS)))
    checks = {
        "git_privacy_state": _state_path(project).exists(),
        "git_privacy_hooks_path": _git_config_get(project, "core.hooksPath") == str(
            hooks_dir.resolve()
        ),
        "git_privacy_author_name": _git_config_get(project, "user.name")
        == state.get("author_name"),
        "git_privacy_author_email": _git_config_get(project, "user.email")
        == state.get("author_email"),
        "git_privacy_use_config_only": _git_config_get(project, "user.useConfigOnly") == "true",
        "git_privacy_pre_commit_hook": (hooks_dir / "pre-commit").exists()
        and (hooks_dir / "pre-commit").read_text(encoding="utf-8") == expected,
        "git_privacy_commit_msg_hook": (hooks_dir / "commit-msg").exists()
        and (hooks_dir / "commit-msg").read_text(encoding="utf-8") == expected,
    }
    return checks
