# Install Guide

## Prerequisites

- `python3`
- `pip`
- `git`
- `gh` for GitHub publish flow
- `uv` optional for Graphify ecosystem
- `node` and `npx` for MCP and browser tooling

## Local Package Setup

```bash
cd chef
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e '.[graph]'
```

`graphifyy` provides the `graphify` binary used by `chef graph-refresh`.

## Project Bootstrap

New structured vault:

```bash
chef init --project . --host both --vault new
```

Existing vault:

```bash
chef init --project . --host both --vault existing --vault-path /path/to/vault
```

## Host Install

Claude only:

```bash
chef install --host claude --project .
```

Codex only:

```bash
chef install --host codex --project .
```

Dual install:

```bash
chef install --host both --project .
```

Pack-aware install behavior:

- bundled Chef skills install into project-local host runtime under `.claude/`, `.codex/`, and `.codex-plugin/`
- external skill pages and GitHub sources cache under `.chef/vendor/` and sync into project-local targets
- Codex registers built-in `chef-knowledge-mcp` and also merges MCP-capable catalog items into project-local `.codex-plugin/.mcp.json`
- `chef install --offline` avoids network access and reuses cache or writes wrapper fallbacks

Enable and install more packs later:

```bash
chef pack-enable --project . --pack ux --pack media --offline
```

`chef pack-enable` now writes enabled-pack state and installs pack assets for the project host in one step.

Local wrapper without editable install:

```bash
./bin/chef --help
```

## Verification

`chef graph-refresh` auto-detects the current agent host when `--host` is omitted.

```bash
chef install --host both --project . --offline
chef verify --project .
chef graph-refresh --project . --execute
```

## MCP Servers

Chef ships three MCP entry points after install:

- `chef-knowledge-mcp`
- `chef-review-mcp`
- `chef-security-mcp`

## Manifest

Manifest format and validation live in
[docs/manifest-schema.md](manifest-schema.md)

Catalog details live in
[docs/catalog-schema.md](catalog-schema.md)

## Tests

```bash
python -m unittest discover -s tests -v
```
