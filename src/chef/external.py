from __future__ import annotations

import json
import os
import shutil
import ssl
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from chef.hosts import replace_path
from chef.paths import (
    claude_plugin_dir,
    claude_skill_dir,
    codex_mcp_file,
    codex_plugin_file,
    codex_skill_dir,
    vendor_dir,
)

try:
    import certifi
except ImportError:  # pragma: no cover - optional dependency in runtime only
    certifi = None


class InstallError(Exception):
    pass


@dataclass
class SyncResult:
    actions: list[str]
    warnings: list[str]
    errors: list[str]


@dataclass
class Snapshot:
    cache_dir: Path
    material_kind: str
    material_path: Path | None = None
    text: str | None = None


@dataclass
class GitHubSource:
    owner: str
    repo: str
    ref: str | None
    subpath: str | None
    mode: str


class HtmlTextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "article",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "p",
        "pre",
        "section",
        "summary",
        "ul",
        "ol",
    }

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def text(self) -> str:
        lines = [" ".join(chunk.split()) for chunk in "".join(self.parts).splitlines()]
        collapsed = "\n".join(line for line in lines if line)
        return collapsed.strip()


def vendor_root(project: Path) -> Path:
    return vendor_dir(project)


def codex_mcp_path(project: Path) -> Path:
    return codex_mcp_file(project)


def codex_plugin_path(project: Path) -> Path:
    return codex_plugin_file(project)


def offline_enabled(explicit: bool | None = None) -> bool:
    if explicit is not None:
        return explicit
    value = os.environ.get("CHEF_OFFLINE", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_github_url(source_url: str) -> GitHubSource | None:
    parsed = urllib.parse.urlparse(source_url)
    if parsed.netloc != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None

    owner, repo = parts[0], parts[1]
    if len(parts) == 2:
        return GitHubSource(owner=owner, repo=repo, ref=None, subpath=None, mode="repo")

    mode = parts[2]
    if mode not in {"blob", "tree"} or len(parts) < 4:
        return GitHubSource(owner=owner, repo=repo, ref=None, subpath=None, mode="repo")

    ref = parts[3]
    subpath = "/".join(parts[4:]) if len(parts) > 4 else None
    return GitHubSource(owner=owner, repo=repo, ref=ref, subpath=subpath, mode=mode)


def request_bytes(url: str) -> tuple[bytes, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "chef/0.1"})
    if certifi is not None:
        context = ssl.create_default_context(cafile=certifi.where())
    else:
        context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=60, context=context) as response:
        payload = response.read()
        return payload, response.headers.get_content_type()


def safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: Path) -> None:
    dest_root = dest_dir.resolve()
    for info in zip_file.infolist():
        extracted = (dest_dir / info.filename).resolve()
        if extracted == dest_root or str(extracted).startswith(str(dest_root) + os.sep):
            continue
        raise InstallError("Archive contains files outside the destination.")
    zip_file.extractall(dest_dir)


def raw_github_url(source: GitHubSource, ref: str) -> str:
    if not source.subpath:
        raise InstallError("GitHub source missing path for raw download.")
    return (
        f"https://raw.githubusercontent.com/{source.owner}/{source.repo}/"
        f"{ref}/{source.subpath}"
    )


def repo_readme_url(source: GitHubSource, ref: str) -> str:
    return f"https://raw.githubusercontent.com/{source.owner}/{source.repo}/{ref}/README.md"


def download_repo_zip(source: GitHubSource, ref: str, dest_dir: Path) -> Path:
    zip_url = f"https://codeload.github.com/{source.owner}/{source.repo}/zip/{ref}"
    payload, _ = request_bytes(zip_url)
    zip_path = dest_dir / "repo.zip"
    zip_path.write_bytes(payload)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        safe_extract_zip(zip_file, dest_dir)
        top_levels = {name.split("/")[0] for name in zip_file.namelist() if name}
    if len(top_levels) != 1:
        raise InstallError("Unexpected archive layout.")
    return dest_dir / next(iter(top_levels))


def ensure_clean_cache(project: Path, item_id: str) -> Path:
    cache_dir = vendor_root(project) / item_id
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def snapshot_from_cache(project: Path, item: dict[str, object]) -> Snapshot | None:
    cache_dir = vendor_root(project) / str(item["id"])
    if not cache_dir.exists():
        return None

    skill_dir = detect_skill_dir(cache_dir, str(item["id"]))
    if skill_dir is not None:
        return Snapshot(cache_dir=cache_dir, material_kind="dir", material_path=skill_dir)

    plugin_dir = detect_claude_plugin_dir(cache_dir)
    if plugin_dir is not None:
        return Snapshot(cache_dir=cache_dir, material_kind="dir", material_path=plugin_dir)

    for filename in ("SKILL.md", "README.md"):
        path = cache_dir / filename
        if path.exists():
            return Snapshot(cache_dir=cache_dir, material_kind="file", material_path=path)

    for filename in ("page.txt", "fallback.txt"):
        path = cache_dir / filename
        if path.exists():
            return Snapshot(
                cache_dir=cache_dir,
                material_kind="text",
                text=path.read_text(encoding="utf-8", errors="ignore"),
            )

    directories = [path for path in cache_dir.iterdir() if path.is_dir()]
    if len(directories) == 1:
        return Snapshot(cache_dir=cache_dir, material_kind="dir", material_path=directories[0])

    return Snapshot(cache_dir=cache_dir, material_kind="dir", material_path=cache_dir)


def extract_html_text(payload: bytes) -> str:
    parser = HtmlTextExtractor()
    parser.feed(payload.decode("utf-8", errors="ignore"))
    text = parser.text()
    if not text:
        raise InstallError("Downloaded page did not contain readable text.")
    return text


def fetch_snapshot(project: Path, item: dict[str, object], offline: bool = False) -> Snapshot:
    item_id = str(item["id"])
    source_url = str(item["source_url"])
    cached = snapshot_from_cache(project, item)
    if offline:
        if cached is not None:
            return cached
        raise InstallError(f"Offline mode enabled and no cached snapshot exists for {item_id}.")

    cache_dir = ensure_clean_cache(project, item_id)
    github = parse_github_url(source_url)

    if github and github.mode == "blob":
        ref = github.ref or "main"
        try:
            payload, _ = request_bytes(raw_github_url(github, ref))
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            repo_root = download_repo_zip(github, ref, cache_dir)
            if not github.subpath:
                raise InstallError("GitHub blob URL missing path.")
            material = repo_root / github.subpath
            if not material.exists():
                raise InstallError(f"Path not found in downloaded repo: {github.subpath}") from exc
            kind = "dir" if material.is_dir() else "file"
            return Snapshot(cache_dir=cache_dir, material_kind=kind, material_path=material)
        material = cache_dir / Path(github.subpath or "SKILL.md").name
        material.write_bytes(payload)
        return Snapshot(cache_dir=cache_dir, material_kind="file", material_path=material)

    if github and github.mode == "tree":
        repo_root = download_repo_zip(github, github.ref or "main", cache_dir)
        if not github.subpath:
            raise InstallError("GitHub tree URL missing path.")
        material = repo_root / github.subpath
        if not material.exists():
            raise InstallError(f"Path not found in downloaded repo: {github.subpath}")
        return Snapshot(cache_dir=cache_dir, material_kind="dir", material_path=material)

    if github and github.mode == "repo":
        for ref in ("main", "master"):
            try:
                payload, _ = request_bytes(repo_readme_url(github, ref))
            except urllib.error.HTTPError:
                continue
            material = cache_dir / "README.md"
            material.write_bytes(payload)
            return Snapshot(cache_dir=cache_dir, material_kind="file", material_path=material)
        raise InstallError(f"Could not fetch README for {source_url}")

    payload, content_type = request_bytes(source_url)
    if content_type in {"text/markdown", "text/plain"}:
        material = cache_dir / "SKILL.md"
        material.write_bytes(payload)
        return Snapshot(cache_dir=cache_dir, material_kind="file", material_path=material)

    text = extract_html_text(payload)
    (cache_dir / "page.txt").write_text(text, encoding="utf-8")
    return Snapshot(cache_dir=cache_dir, material_kind="text", text=text)


def fallback_snapshot(project: Path, item: dict[str, object], exc: Exception) -> Snapshot:
    cache_dir = ensure_clean_cache(project, str(item["id"]))
    text = (
        f"Chef could not fetch upstream content during install.\n"
        f"Source URL: {item['source_url']}\n"
        f"Error: {exc}\n"
    )
    (cache_dir / "fallback.txt").write_text(text, encoding="utf-8")
    return Snapshot(cache_dir=cache_dir, material_kind="text", text=text)


def find_readme(path: Path) -> str | None:
    for candidate in ("README.md", "readme.md", "README.txt"):
        file_path = path / candidate
        if file_path.exists():
            return file_path.read_text(encoding="utf-8", errors="ignore")
    return None


def detect_skill_dir(path: Path, item_id: str) -> Path | None:
    if path.is_dir() and (path / "SKILL.md").exists():
        return path

    matches = list(path.rglob("SKILL.md")) if path.is_dir() else []
    if not matches:
        return None
    preferred = [match.parent for match in matches if match.parent.name == item_id]
    if len(preferred) == 1:
        return preferred[0]
    if len(matches) == 1:
        return matches[0].parent
    return None


def detect_claude_plugin_dir(path: Path) -> Path | None:
    if path.is_dir() and (path / ".claude-plugin" / "plugin.json").exists():
        return path

    if not path.is_dir():
        return None
    matches = list(path.rglob("plugin.json"))
    plugin_matches = [
        match.parent.parent for match in matches if match.parent.name == ".claude-plugin"
    ]
    if len(plugin_matches) == 1:
        return plugin_matches[0]
    return None


def copy_directory(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest)


def wrapper_frontmatter(item: dict[str, object]) -> str:
    description = f"Installed by Chef from {item['source_url']}"
    return (
        "---\n"
        f"name: {item['id']}\n"
        f"description: {description}\n"
        "---\n\n"
    )


def build_wrapper_skill(
    item: dict[str, object],
    snapshot: Snapshot,
    extra_lines: list[str] | None = None,
) -> str:
    title = f"# {item['name']}\n\n"
    body = [
        f"Source URL: {item['source_url']}",
        f"Local cache: {snapshot.cache_dir}",
        "",
    ]
    if extra_lines:
        body.extend(extra_lines)
        body.append("")

    imported_text: str | None = None
    if snapshot.text:
        imported_text = snapshot.text
    elif snapshot.material_path and snapshot.material_path.is_file():
        imported_text = snapshot.material_path.read_text(encoding="utf-8", errors="ignore")
    elif snapshot.material_path and snapshot.material_path.is_dir():
        imported_text = find_readme(snapshot.material_path)

    if imported_text:
        body.append("## Imported Notes")
        body.append("")
        body.append(imported_text.strip())
        body.append("")

    return wrapper_frontmatter(item) + title + "\n".join(body).strip() + "\n"


def replace_and_copy_skill(target: Path, skill_dir: Path | None, skill_content: str) -> list[str]:
    actions: list[str] = []
    replace_path(target)
    if skill_dir is not None:
        copy_directory(skill_dir, target)
    else:
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(skill_content, encoding="utf-8")
    actions.append(str(target))
    return actions


def install_skill_like_item(
    project: Path,
    host: str,
    item: dict[str, object],
    snapshot: Snapshot,
    extra_lines: list[str] | None = None,
) -> list[str]:
    item_id = str(item["id"])
    if host == "codex":
        target = codex_skill_dir(project, item_id)
    else:
        target = claude_skill_dir(project, item_id)
    skill_dir = snapshot.material_path and detect_skill_dir(snapshot.material_path, item_id)
    skill_content = build_wrapper_skill(item, snapshot, extra_lines=extra_lines)
    return replace_and_copy_skill(target, skill_dir, skill_content)


def install_claude_plugin_item(
    project: Path, item: dict[str, object], snapshot: Snapshot
) -> tuple[list[str], list[str]]:
    item_id = str(item["id"])
    plugin_dir = snapshot.material_path and detect_claude_plugin_dir(snapshot.material_path)
    if plugin_dir is None:
        warning = (
            f"{item_id}: plugin source not detected, "
            "installed as Claude skill wrapper instead."
        )
        return [], [warning]

    target = claude_plugin_dir(project, item_id)
    actions: list[str] = []
    replace_path(target)
    copy_directory(plugin_dir, target)
    actions.append(str(target))
    return actions, []


def ensure_codex_plugin_declares_mcp(project: Path) -> None:
    plugin_path = codex_plugin_path(project)
    if not plugin_path.exists():
        return
    data = json.loads(plugin_path.read_text(encoding="utf-8"))
    if data.get("mcpServers") == "./.mcp.json":
        return
    data["mcpServers"] = "./.mcp.json"
    plugin_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def merge_codex_mcp_entries(project: Path, items: list[dict[str, object]]) -> list[str]:
    if not items:
        return []

    ensure_codex_plugin_declares_mcp(project)
    mcp_path = codex_mcp_path(project)
    existing: dict[str, object] = {"mcpServers": {}}
    if mcp_path.exists():
        existing = json.loads(mcp_path.read_text(encoding="utf-8"))
        if not isinstance(existing, dict):
            existing = {"mcpServers": {}}
    servers = existing.get("mcpServers")
    if not isinstance(servers, dict):
        servers = {}

    for item in items:
        mcp = item.get("mcp")
        if not isinstance(mcp, dict):
            continue
        servers[str(item["id"])] = {
            "command": mcp["command"],
            "args": list(mcp["args"]),
        }

    desired = json.dumps({"mcpServers": servers}, indent=2) + "\n"
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    if mcp_path.exists():
        current = mcp_path.read_text(encoding="utf-8")
        if current == desired:
            return [str(mcp_path)]
    mcp_path.write_text(desired, encoding="utf-8")
    return [str(mcp_path)]


def sync_external_items(
    project: Path, host: str, items: list[dict[str, object]], offline: bool = False
) -> SyncResult:
    actions: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    codex_mcp_items: list[dict[str, object]] = []
    offline_mode = offline_enabled(offline)

    for item in items:
        if item["install"]["method"] != "manual":
            continue
        snapshot: Snapshot
        degraded = False
        try:
            snapshot = fetch_snapshot(project, item, offline=offline_mode)
        except (InstallError, urllib.error.URLError) as exc:
            snapshot = fallback_snapshot(project, item, exc)
            degraded = True
            warnings.append(
                f"{item['id']}: upstream fetch failed, installed wrapper fallback instead."
            )

        try:
            kind = str(item["kind"])
            if host == "claude" and kind == "plugin":
                plugin_actions, plugin_warnings = install_claude_plugin_item(
                    project, item, snapshot
                )
                actions.extend(plugin_actions)
                warnings.extend(plugin_warnings)
                if plugin_warnings:
                    actions.extend(
                        install_skill_like_item(
                            project,
                            host,
                            item,
                            snapshot,
                            extra_lines=[
                                "Plugin wrapper installed.",
                                "Upstream plugin fetch degraded.",
                            ],
                        )
                    )
            elif host == "codex" and kind == "mcp_server" and item.get("mcp"):
                codex_mcp_items.append(item)
                actions.extend(
                    install_skill_like_item(
                        project,
                        host,
                        item,
                        snapshot,
                        extra_lines=[
                            "This item is also configured as a Codex MCP server "
                            "in .codex-plugin/.mcp.json."
                        ],
                    )
                )
            else:
                extra_lines = ["Upstream fetch degraded."] if degraded else None
                actions.extend(
                    install_skill_like_item(project, host, item, snapshot, extra_lines=extra_lines)
                )
        except (InstallError, OSError, json.JSONDecodeError) as exc:
            errors.append(f"{item['id']}: {exc}")

    if host == "codex":
        try:
            actions.extend(merge_codex_mcp_entries(project, codex_mcp_items))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"codex-mcp-config: {exc}")

    return SyncResult(actions=actions, warnings=warnings, errors=errors)


def verify_external_items(
    project: Path, host: str, items: list[dict[str, object]]
) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    codex_servers: dict[str, object] = {}
    if host == "codex":
        try:
            mcp_data = json.loads(codex_mcp_path(project).read_text(encoding="utf-8"))
            loaded_servers = mcp_data.get("mcpServers", {}) if isinstance(mcp_data, dict) else {}
            if isinstance(loaded_servers, dict):
                codex_servers = loaded_servers
        except (FileNotFoundError, json.JSONDecodeError):
            codex_servers = {}
        checks["mcp:chef-knowledge-mcp"] = "chef-knowledge-mcp" in codex_servers

    for item in items:
        item_id = str(item["id"])
        kind = str(item["kind"])
        if item["install"]["method"] == "bundled":
            if host == "codex" and kind in {"codex_skill", "skill"}:
                checks[f"item:{item_id}"] = codex_skill_dir(project, item_id).exists()
            elif host == "claude" and kind == "skill":
                checks[f"item:{item_id}"] = claude_skill_dir(project, item_id).exists()
            continue

        if host == "codex":
            checks[f"item:{item_id}"] = codex_skill_dir(project, item_id).exists()
            if kind == "mcp_server" and item.get("mcp"):
                checks[f"mcp:{item_id}"] = item_id in codex_servers
        else:
            if kind == "plugin":
                checks[f"item:{item_id}"] = (
                    claude_plugin_dir(project, item_id).exists()
                    or claude_skill_dir(project, item_id).exists()
                )
            else:
                checks[f"item:{item_id}"] = claude_skill_dir(project, item_id).exists()
    return checks
