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
- Chef records install results and fidelity in `.chef/install-state.json`
- Codex registers built-in `chef-knowledge-mcp` and pack-aware built-in review and security MCPs, and also merges MCP-capable catalog items into project-local `.codex-plugin/.mcp.json`
- `chef install --offline` avoids network access and reuses cache or writes wrapper fallbacks
- always-on Chef routing skills such as `chef-index`, `graph-first-retrieval`, and `skill-finder` install even when no optional packs are enabled
- heavyweight orchestration frameworks stay in the optional `orchestration` pack so default installs avoid overlapping agent frameworks

Enable and install more packs later:

```bash
chef pack-enable --project . --pack ux --pack media --offline
chef pack-disable --project . --pack media
chef pack-profile --project . --profile full --offline
```

`chef pack-enable` now writes enabled-pack state and installs pack assets for the project host in one step.
The `media` pack includes `talkcraft` for presentation strategy and rehearsal support.
The `orchestration` pack groups `gstack`, `massgen`, `ruflo`, and `superpowers`.

Local wrapper without editable install:

```bash
./bin/chef --help
```

## Verification

`chef graph-refresh` auto-detects the current agent host when `--host` is omitted.
`chef verify` now defaults to human-readable output. Use `--json` for structured automation.

```bash
chef install --host both --project . --offline
chef install --host both --project . --plan --json
chef verify --project . --json
chef graph-refresh --project . --execute
```

## MCP Servers

Chef ships three MCP entry points:

- `chef-knowledge-mcp`
- `chef-review-mcp`
- `chef-security-mcp`

Codex auto-registers:

- `chef-knowledge-mcp` always
- `chef-review-mcp` when `review` pack stays enabled
- `chef-security-mcp` when `security` pack stays enabled

## Manifest

Manifest format and validation live in
[docs/manifest-schema.md](manifest-schema.md)

Catalog details live in
[docs/catalog-schema.md](catalog-schema.md)

Skill overlap and Codex adaptation decisions live in
[docs/skill-audit.md](skill-audit.md)

## Tests

```bash
python -m unittest discover -s tests -v
```
