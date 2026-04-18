# Chef

Chef provides one modular enhancement package for Claude and Codex.

## Goals

- One repository.
- Two host installs.
- Shared graph-first policy.
- Structured Obsidian knowledge base.
- Native host routing.
- Optional domain packs.
- Built-in MCP servers.
- One capability catalog for pack resolution.

## Quick Start

```bash
cd chef
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e '.[graph]'
chef init --project . --host both --vault new
chef install --host both --project . --offline
chef verify --project .
```

`graphifyy` installs the `graphify` CLI used by `chef graph-refresh`.

## Host Install

Claude:

```bash
chef install --host claude --project .
```

Codex:

```bash
chef install --host codex --project .
```

Both:

```bash
chef install --host both --project .
```

`chef install` now syncs enabled packs:

- bundled Chef assets install into project-local host runtime under `.claude/`, `.codex/`, and `.codex-plugin/`
- external skills and plugin sources cache under `.chef/vendor/` and sync into project-local targets
- `--offline` reuses cached snapshots or writes managed wrapper fallbacks without network access
- Codex MCP entries write into project-local `.codex-plugin/.mcp.json` when catalog metadata exists

Enable more packs after initial install:

```bash
chef pack-enable --project . --pack media --offline
```

`chef pack-enable` now updates enabled state and installs pack assets for the project host immediately.

Local development wrapper:

```bash
./bin/chef --help
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Core Rules

- Query graph before raw source.
- Treat `chef/knowledge-vault/Graphify/graphify-out/wiki/index.md` as authoritative codebase index.
- Keep repo-root `graphify-out/` as compatibility symlink into vault-owned graph output.
- Keep generated runtime state inside project boundaries.
- Allow raw file reads only when user explicitly asks.
- Use native host expert routing, not cross-vendor routing.

## Key Paths

- [docs/architecture.md](docs/architecture.md)
- [docs/catalog-schema.md](docs/catalog-schema.md)
- [docs/install.md](docs/install.md)
- [docs/manifest-schema.md](docs/manifest-schema.md)
- [docs/publish.md](docs/publish.md)
- [docs/tool-matrix.md](docs/tool-matrix.md)
- [catalog/items.json](catalog/items.json)
- [knowledge-vault/Home/Home.md](knowledge-vault/Home/Home.md)
- [knowledge-vault/Graphify/index.md](knowledge-vault/Graphify/index.md)
- [mcp/chef-knowledge-mcp/README.md](mcp/chef-knowledge-mcp/README.md)
