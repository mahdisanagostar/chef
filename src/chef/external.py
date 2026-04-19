from __future__ import annotations

import datetime as dt
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

from chef.catalog import read_item_catalog
from chef.hosts import codex_builtin_mcp_servers, replace_path
from chef.install_state import record_for
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
    states: list[dict[str, object]]


@dataclass
class Snapshot:
    cache_dir: Path
    material_kind: str
    material_path: Path | None = None
    text: str | None = None
    source_mode: str = "unknown"
    resolved_ref: str | None = None


@dataclass
class GitHubSource:
    owner: str
    repo: str
    ref: str | None
    subpath: str | None
    mode: str


def item_source_ref(item: dict[str, object], source: GitHubSource | None) -> str | None:
    configured = item.get("source_ref")
    if isinstance(configured, str) and configured:
        return configured
    if source is None:
        return None
    return source.ref or "main"


def item_source_subpath(item: dict[str, object], source: GitHubSource | None) -> str | None:
    configured = item.get("source_subpath")
    if isinstance(configured, str) and configured.strip():
        return configured.strip().lstrip("/")
    if source is None or not source.subpath:
        return None
    return source.subpath


def item_source_kind(item: dict[str, object]) -> str:
    configured = item.get("source_kind")
    if isinstance(configured, str) and configured:
        return configured
    kind = str(item.get("kind", "skill"))
    if kind == "plugin":
        return "plugin"
    if kind == "mcp_server":
        return "mcp_server"
    if kind in {"repo", "tool"}:
        return kind
    return "skill"


class HtmlTextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "article",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "nav",
        "p",
        "pre",
        "section",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "summary",
        "ul",
        "ol",
    }
    IGNORED_TAGS = {
        "head",
        "script",
        "style",
        "noscript",
        "svg",
        "template",
    }

    def __init__(self) -> None:
        super().__init__()
        self.parts: dict[str, list[str]] = {"article": [], "main": [], "body": []}
        self.capture_depth = {"article": 0, "main": 0, "body": 0}
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.IGNORED_TAGS:
            self.ignored_depth += 1
            return
        if self.ignored_depth:
            return
        if tag in self.capture_depth:
            self.capture_depth[tag] += 1
        if tag in self.BLOCK_TAGS:
            self._append_break()

    def handle_endtag(self, tag: str) -> None:
        if tag in self.IGNORED_TAGS:
            if self.ignored_depth:
                self.ignored_depth -= 1
            return
        if self.ignored_depth:
            return
        if tag in self.BLOCK_TAGS:
            self._append_break()
        if tag in self.capture_depth and self.capture_depth[tag]:
            self.capture_depth[tag] -= 1

    def handle_data(self, data: str) -> None:
        if self.ignored_depth:
            return
        text = data.strip()
        if text:
            self._append_text(text)

    def text(self) -> str:
        for scope in ("article", "main", "body"):
            lines = [
                " ".join(chunk.split()) for chunk in "".join(self.parts[scope]).splitlines()
            ]
            collapsed = "\n".join(line for line in lines if line)
            if collapsed.strip():
                return collapsed.strip()
        return ""

    def _append_break(self) -> None:
        for scope, depth in self.capture_depth.items():
            if depth > 0:
                self.parts[scope].append("\n")

    def _append_text(self, text: str) -> None:
        for scope, depth in self.capture_depth.items():
            if depth > 0:
                self.parts[scope].append(text)


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

    source_url = item.get("source_url")
    github = parse_github_url(source_url) if isinstance(source_url, str) else None
    repo_roots = [path for path in cache_dir.iterdir() if path.is_dir()]
    if github and len(repo_roots) == 1:
        repo_root = repo_roots[0]
        try:
            if github.mode == "repo":
                mode, material = resolve_repo_material(repo_root, item)
                return Snapshot(
                    cache_dir=cache_dir,
                    material_kind="dir" if material.is_dir() else "file",
                    material_path=material,
                    source_mode=f"cache-{mode}",
                    resolved_ref=item_source_ref(item, github),
                )
            if github.mode == "tree":
                subpath = item_source_subpath(item, github)
                if subpath:
                    material = repo_root / subpath
                    if material.exists():
                        return Snapshot(
                            cache_dir=cache_dir,
                            material_kind="dir" if material.is_dir() else "file",
                            material_path=material,
                            source_mode="cache-github-tree",
                            resolved_ref=item_source_ref(item, github),
                        )
        except InstallError:
            pass

    skill_dir = detect_skill_dir(cache_dir, str(item["id"]))
    if skill_dir is not None:
        return Snapshot(
            cache_dir=cache_dir,
            material_kind="dir",
            material_path=skill_dir,
            source_mode="cache-skill-dir",
        )

    plugin_dir = detect_claude_plugin_dir(cache_dir)
    if plugin_dir is not None:
        return Snapshot(
            cache_dir=cache_dir,
            material_kind="dir",
            material_path=plugin_dir,
            source_mode="cache-plugin-dir",
        )

    for filename in ("SKILL.md", "README.md"):
        path = cache_dir / filename
        if path.exists():
            return Snapshot(
                cache_dir=cache_dir,
                material_kind="file",
                material_path=path,
                source_mode="cache-file",
            )

    for filename in ("page.txt", "fallback.txt"):
        path = cache_dir / filename
        if path.exists():
            return Snapshot(
                cache_dir=cache_dir,
                material_kind="text",
                text=path.read_text(encoding="utf-8", errors="ignore"),
                source_mode="cache-text",
            )

    directories = [path for path in cache_dir.iterdir() if path.is_dir()]
    if len(directories) == 1:
        return Snapshot(
            cache_dir=cache_dir,
            material_kind="dir",
            material_path=directories[0],
            source_mode="cache-dir",
        )

    return Snapshot(
        cache_dir=cache_dir,
        material_kind="dir",
        material_path=cache_dir,
        source_mode="cache-dir",
    )


def extract_html_text(payload: bytes) -> str:
    parser = HtmlTextExtractor()
    parser.feed(payload.decode("utf-8", errors="ignore"))
    parser.close()
    text = parser.text()
    if not text:
        raise InstallError("Downloaded page did not contain readable text.")
    return text


def adapter_notes_for_host(item: dict[str, object], host: str) -> list[str]:
    adapter_notes = item.get("adapter_notes")
    if not isinstance(adapter_notes, dict):
        return []
    notes = adapter_notes.get(host)
    if not isinstance(notes, list):
        return []
    return [note for note in notes if isinstance(note, str) and note]


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
    source_ref = item_source_ref(item, github)
    source_subpath = item_source_subpath(item, github)

    if github and github.mode == "blob":
        ref = source_ref or "main"
        try:
            payload, _ = request_bytes(
                raw_github_url(
                    GitHubSource(
                        owner=github.owner,
                        repo=github.repo,
                        ref=ref,
                        subpath=source_subpath,
                        mode="blob",
                    ),
                    ref,
                )
            )
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            repo_root = download_repo_zip(github, ref, cache_dir)
            if not source_subpath:
                raise InstallError("GitHub blob URL missing path.")
            material = repo_root / source_subpath
            if not material.exists():
                raise InstallError(f"Path not found in downloaded repo: {source_subpath}") from exc
            kind = "dir" if material.is_dir() else "file"
            return Snapshot(
                cache_dir=cache_dir,
                material_kind=kind,
                material_path=material,
                source_mode="github-blob-fallback",
                resolved_ref=ref,
            )
        material = cache_dir / Path(source_subpath or "SKILL.md").name
        material.write_bytes(payload)
        return Snapshot(
            cache_dir=cache_dir,
            material_kind="file",
            material_path=material,
            source_mode="github-blob",
            resolved_ref=ref,
        )

    if github and github.mode == "tree":
        ref = source_ref or "main"
        repo_root = download_repo_zip(github, ref, cache_dir)
        if not source_subpath:
            raise InstallError("GitHub tree URL missing path.")
        material = repo_root / source_subpath
        if not material.exists():
            raise InstallError(f"Path not found in downloaded repo: {source_subpath}")
        return Snapshot(
            cache_dir=cache_dir,
            material_kind="dir" if material.is_dir() else "file",
            material_path=material,
            source_mode="github-tree",
            resolved_ref=ref,
        )

    if github and github.mode == "repo":
        refs = [source_ref] if source_ref else ["main", "master"]
        last_error: Exception | None = None
        for ref in refs:
            if not ref:
                continue
            try:
                repo_root = download_repo_zip(github, ref, cache_dir)
            except (InstallError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                last_error = exc
                continue
            mode, material = resolve_repo_material(repo_root, item)
            return Snapshot(
                cache_dir=cache_dir,
                material_kind="dir" if material.is_dir() else "file",
                material_path=material,
                source_mode=mode,
                resolved_ref=ref,
            )
        if last_error is not None:
            raise InstallError(
                f"Could not download repo for {source_url}: {last_error}"
            ) from last_error
        raise InstallError(f"Could not resolve repo source for {source_url}")

    payload, content_type = request_bytes(source_url)
    if content_type in {"text/markdown", "text/plain"}:
        material = cache_dir / "SKILL.md"
        material.write_bytes(payload)
        return Snapshot(
            cache_dir=cache_dir,
            material_kind="file",
            material_path=material,
            source_mode="web-text",
        )

    text = extract_html_text(payload)
    (cache_dir / "page.txt").write_text(text, encoding="utf-8")
    return Snapshot(cache_dir=cache_dir, material_kind="text", text=text, source_mode="web-html")


def fallback_snapshot(project: Path, item: dict[str, object], exc: Exception) -> Snapshot:
    cache_dir = ensure_clean_cache(project, str(item["id"]))
    text = (
        f"Chef could not fetch upstream content during install.\n"
        f"Source URL: {item['source_url']}\n"
        f"Error: {exc}\n"
    )
    (cache_dir / "fallback.txt").write_text(text, encoding="utf-8")
    return Snapshot(cache_dir=cache_dir, material_kind="text", text=text, source_mode="fallback")


def find_readme(path: Path) -> str | None:
    for candidate in ("README.md", "readme.md", "README.txt"):
        file_path = path / candidate
        if file_path.exists():
            return file_path.read_text(encoding="utf-8", errors="ignore")
    return None


def repo_readme_path(path: Path) -> Path | None:
    for candidate in ("README.md", "readme.md", "README.txt"):
        file_path = path / candidate
        if file_path.exists():
            return file_path
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
    if path.is_dir() and (path / "plugin.json").exists():
        return path

    if not path.is_dir():
        return None
    matches = list(path.rglob("plugin.json"))
    plugin_matches = [
        match.parent.parent for match in matches if match.parent.name == ".claude-plugin"
    ]
    plugin_matches.extend(
        match.parent
        for match in matches
        if match.parent.name != ".claude-plugin" and (match.parent / "commands").exists()
    )
    if len(plugin_matches) == 1:
        return plugin_matches[0]
    return None


def repo_root_candidates(item_id: str) -> list[tuple[str, Path]]:
    normalized = item_id.replace("-", "_")
    return [
        ("skills", Path("skills") / item_id),
        ("skills-normalized", Path("skills") / normalized),
        ("agents-skill", Path(".agents") / "skills" / item_id),
        ("claude-skill", Path(".claude") / "skills" / item_id),
        ("codex-skill", Path(".codex") / "skills" / item_id),
    ]


def resolve_repo_material(repo_root: Path, item: dict[str, object]) -> tuple[str, Path]:
    explicit_subpath = item_source_subpath(item, None)
    if explicit_subpath:
        explicit_path = repo_root / explicit_subpath
        if not explicit_path.exists():
            raise InstallError(f"Path not found in downloaded repo: {explicit_subpath}")
        if explicit_path.is_dir() and detect_claude_plugin_dir(explicit_path):
            plugin_dir = detect_claude_plugin_dir(explicit_path) or explicit_path
            return "github-repo-plugin", plugin_dir
        if explicit_path.is_dir():
            skill_dir = detect_skill_dir(explicit_path, str(item["id"]))
            if skill_dir is not None:
                return "github-repo-skill", skill_dir
        return ("github-repo-dir" if explicit_path.is_dir() else "github-repo-file", explicit_path)

    item_id = str(item["id"])
    source_kind = item_source_kind(item)
    if source_kind == "plugin":
        plugin_dir = detect_claude_plugin_dir(repo_root)
        if plugin_dir is not None:
            return "github-repo-plugin", plugin_dir

    if source_kind in {"skill", "mcp_server"}:
        for mode, relative in repo_root_candidates(item_id):
            candidate = repo_root / relative
            if candidate.exists() and candidate.is_dir() and (candidate / "SKILL.md").exists():
                return f"github-repo-{mode}", candidate
        skill_dir = detect_skill_dir(repo_root, item_id)
        if skill_dir is not None:
            return "github-repo-skill", skill_dir

    if source_kind in {"collection", "framework", "repo", "tool", "mcp_server"}:
        readme_path = repo_readme_path(repo_root)
        if readme_path is not None:
            return "github-repo-readme", readme_path

    plugin_dir = detect_claude_plugin_dir(repo_root)
    if plugin_dir is not None:
        return "github-repo-plugin", plugin_dir
    skill_dir = detect_skill_dir(repo_root, item_id)
    if skill_dir is not None:
        return "github-repo-skill", skill_dir
    readme_path = repo_readme_path(repo_root)
    if readme_path is not None:
        return "github-repo-readme", readme_path
    return "github-repo-dir", repo_root


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
    adapter_notes: list[str] | None = None,
    extra_lines: list[str] | None = None,
) -> str:
    title = f"# {item['name']}\n\n"
    body = [
        f"Source URL: {item['source_url']}",
        f"Local cache: {snapshot.cache_dir}",
        "",
    ]
    if adapter_notes:
        body.append("## Chef Adapter Notes")
        body.append("")
        body.extend(f"- {note}" for note in adapter_notes)
        body.append("")
    if extra_lines:
        body.append("## Chef Runtime Notes")
        body.append("")
        body.extend(f"- {line}" for line in extra_lines)
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


def wrapper_expected(item: dict[str, object]) -> bool:
    source_kind = item_source_kind(item)
    return source_kind in {"collection", "framework", "repo", "tool", "mcp_server"} or str(
        item.get("kind")
    ) in {"repo", "tool", "mcp_server"}


def snapshot_fidelity(
    item: dict[str, object],
    snapshot: Snapshot,
    degraded_fetch: bool,
    plugin_fallback: bool,
) -> tuple[str, list[str], bool]:
    warnings: list[str] = []
    if degraded_fetch or plugin_fallback:
        return "fallback", warnings, True

    item_kind = str(item.get("kind"))
    direct_skill = (
        snapshot.material_path and detect_skill_dir(snapshot.material_path, str(item["id"]))
    )
    direct_plugin = snapshot.material_path and detect_claude_plugin_dir(snapshot.material_path)
    if direct_skill or direct_plugin:
        return "direct", warnings, False

    if wrapper_expected(item):
        if snapshot.source_mode in {"github-repo-readme", "web-html", "web-text", "cache-text"}:
            warnings.append(
                "Installed through wrapper content; runtime stays valid but "
                "upstream fidelity stays limited."
            )
        return "wrapped", warnings, False

    parsed = parse_github_url(str(item.get("source_url", "")))
    if parsed and parsed.mode == "repo":
        warnings.append(
            "Repo-root source resolved to wrapper content. "
            "Add source_subpath for higher-fidelity installs."
        )
        return "wrapped", warnings, False

    if snapshot.source_mode in {"web-html", "web-text", "cache-text"} and item_kind == "plugin":
        warnings.append("Plugin source did not resolve to a real plugin directory.")
        return "fallback", warnings, True
    return "wrapped", warnings, False


def build_install_record(
    project: Path,
    host: str,
    item: dict[str, object],
    snapshot: Snapshot | None,
    targets: list[str],
    warnings: list[str],
    errors: list[str],
    degraded: bool,
    fidelity: str,
) -> dict[str, object]:
    item_id = str(item["id"])
    source_url = item.get("source_url")
    return {
        "item_id": item_id,
        "host": host,
        "kind": str(item["kind"]),
        "install_method": str(item["install"]["method"]),
        "targets": targets,
        "installed": not errors and all(Path(target).exists() for target in targets),
        "degraded": degraded,
        "fidelity": fidelity,
        "source_url": source_url if isinstance(source_url, str) else None,
        "source_mode": snapshot.source_mode if snapshot is not None else "bundled",
        "resolved_ref": snapshot.resolved_ref if snapshot is not None else None,
        "warning_count": len(warnings),
        "warnings": warnings,
        "errors": errors,
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "cache_dir": str(snapshot.cache_dir) if snapshot is not None else None,
        "project": str(project),
    }


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
        if str(item["kind"]) == "plugin":
            replace_path(claude_plugin_dir(project, item_id))
    skill_dir = snapshot.material_path and detect_skill_dir(snapshot.material_path, item_id)
    skill_content = build_wrapper_skill(
        item,
        snapshot,
        adapter_notes=adapter_notes_for_host(item, host),
        extra_lines=extra_lines,
    )
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
    replace_path(claude_skill_dir(project, item_id))
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

    managed_mcp_ids = {
        item_id
        for item_id, item in read_item_catalog().items()
        if "codex" in item.get("hosts", []) and str(item.get("kind")) == "mcp_server"
    }
    enabled_mcp_ids = {str(item["id"]) for item in items}
    for item_id in managed_mcp_ids - enabled_mcp_ids:
        servers.pop(item_id, None)

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
    states: list[dict[str, object]] = []
    codex_mcp_items: list[dict[str, object]] = []
    offline_mode = offline_enabled(offline)

    for item in items:
        if item["install"]["method"] != "manual":
            continue
        snapshot: Snapshot
        degraded_fetch = False
        item_actions: list[str] = []
        item_warnings: list[str] = []
        item_errors: list[str] = []
        plugin_fallback = False
        try:
            snapshot = fetch_snapshot(project, item, offline=offline_mode)
        except (InstallError, urllib.error.URLError) as exc:
            snapshot = fallback_snapshot(project, item, exc)
            degraded_fetch = True
            item_warnings.append(
                f"{item['id']}: upstream fetch failed, installed wrapper fallback instead."
            )

        try:
            kind = str(item["kind"])
            if host == "claude" and kind == "plugin":
                plugin_actions, plugin_warnings = install_claude_plugin_item(
                    project, item, snapshot
                )
                item_actions.extend(plugin_actions)
                item_warnings.extend(plugin_warnings)
                if plugin_warnings:
                    plugin_fallback = True
                    item_actions.extend(
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
                item_actions.extend(
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
                extra_lines = ["Upstream fetch degraded."] if degraded_fetch else None
                item_actions.extend(
                    install_skill_like_item(project, host, item, snapshot, extra_lines=extra_lines)
                )
        except (InstallError, OSError, json.JSONDecodeError) as exc:
            item_errors.append(f"{item['id']}: {exc}")

        fidelity, fidelity_warnings, degraded = snapshot_fidelity(
            item,
            snapshot,
            degraded_fetch=degraded_fetch,
            plugin_fallback=plugin_fallback,
        )
        item_warnings.extend(fidelity_warnings)
        actions.extend(item_actions)
        warnings.extend(item_warnings)
        errors.extend(item_errors)
        states.append(
            build_install_record(
                project,
                host,
                item,
                snapshot,
                item_actions,
                item_warnings,
                item_errors,
                degraded=degraded or bool(item_errors),
                fidelity=fidelity,
            )
        )

    if host == "codex":
        try:
            actions.extend(merge_codex_mcp_entries(project, codex_mcp_items))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"codex-mcp-config: {exc}")

    return SyncResult(actions=actions, warnings=warnings, errors=errors, states=states)


def verify_external_items_report(
    project: Path, host: str, items: list[dict[str, object]]
) -> tuple[dict[str, bool], list[str]]:
    checks: dict[str, bool] = {}
    warnings: list[str] = []
    codex_servers: dict[str, object] = {}
    if host == "codex":
        try:
            mcp_data = json.loads(codex_mcp_path(project).read_text(encoding="utf-8"))
            loaded_servers = mcp_data.get("mcpServers", {}) if isinstance(mcp_data, dict) else {}
            if isinstance(loaded_servers, dict):
                codex_servers = loaded_servers
        except (FileNotFoundError, json.JSONDecodeError):
            codex_servers = {}
        for mcp_id in sorted(codex_builtin_mcp_servers(project)):
            checks[f"mcp:{mcp_id}"] = mcp_id in codex_servers

    for item in items:
        item_id = str(item["id"])
        kind = str(item["kind"])
        if item["install"]["method"] == "bundled":
            if host == "codex" and kind in {"codex_skill", "skill"}:
                checks[f"item:{item_id}"] = codex_skill_dir(project, item_id).exists()
            elif host == "claude" and kind == "skill":
                checks[f"item:{item_id}"] = claude_skill_dir(project, item_id).exists()
            continue

        state = record_for(project, host, item_id)
        checks[f"install-state:{item_id}"] = state is not None
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
        if not state:
            continue
        if bool(state.get("degraded")):
            checks[f"item:{item_id}"] = False
        record_warnings = state.get("warnings")
        if isinstance(record_warnings, list):
            warnings.extend(
                f"{item_id}: {warning}" for warning in record_warnings if isinstance(warning, str)
            )
        source_mode = str(state.get("source_mode", ""))
        parsed_source = parse_github_url(str(item.get("source_url", "")))
        if (
            state.get("fidelity") == "wrapped"
            and kind in {"skill", "plugin"}
            and not wrapper_expected(item)
            and (
                "github-repo" in source_mode
                or bool(parsed_source and parsed_source.mode == "repo")
            )
        ):
            warnings.append(
                f"{item_id}: wrapper install only. Add source_subpath or better source metadata."
            )
    return checks, warnings


def verify_external_items(
    project: Path, host: str, items: list[dict[str, object]]
) -> dict[str, bool]:
    checks, _ = verify_external_items_report(project, host, items)
    return checks
