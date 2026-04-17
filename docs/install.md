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

Restore one backed-up managed target:

```bash
chef restore-backup --project . --backup ~/.chef/backups/claude-plugin-chef-20260417T000001Z
```

Use
`--force`
to replace an existing target while preserving one more backup snapshot.

Local wrapper without editable install:

```bash
./bin/chef --help
```

## Verification

```bash
chef verify --project .
chef graph-refresh --project . --host codex --execute
```

## MCP Servers

CHEF ships three MCP entry points after install:

- `chef-knowledge-mcp`
- `chef-review-mcp`
- `chef-security-mcp`

## Manifest

Manifest format and validation live in
[docs/manifest-schema.md](manifest-schema.md)

## Tests

```bash
python -m unittest discover -s tests -v
```
