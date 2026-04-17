# CHEF

CHEF provides one modular enhancement package for Claude and Codex.

## Goals

- One repository.
- Two host installs.
- Shared graph-first policy.
- Structured Obsidian knowledge base.
- Native host routing.
- Optional domain packs.
- Built-in MCP servers.

## Quick Start

```bash
cd chef
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install graphifyy
chef init --project . --host both --vault new
chef verify --project .
```

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

## Core Rules

- Query graph before raw source.
- Treat `chef/knowledge-vault/Graphify/graphify-out/wiki/index.md` as authoritative codebase index.
- Keep repo-root `graphify-out/` as compatibility symlink into vault-owned graph output.
- Allow raw file reads only when user explicitly asks.
- Use native host expert routing, not cross-vendor routing.

## Key Paths

- [docs/architecture.md](docs/architecture.md)
- [docs/install.md](docs/install.md)
- [docs/publish.md](docs/publish.md)
- [docs/tool-matrix.md](docs/tool-matrix.md)
- [knowledge-vault/Home/Home.md](knowledge-vault/Home/Home.md)
- [knowledge-vault/Graphify/index.md](knowledge-vault/Graphify/index.md)
- [mcp/chef-knowledge-mcp/README.md](mcp/chef-knowledge-mcp/README.md)
