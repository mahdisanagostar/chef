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
pip install graphifyy
```

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
