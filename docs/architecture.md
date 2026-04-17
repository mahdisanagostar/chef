# CHEF Architecture

## Shape

CHEF ships one repository with one shared core and two isolated host adapters.

- `core/` holds policy, routing, manifests, and orchestration extraction.
- `adapters/claude/` holds Claude-specific commands and plugin metadata.
- `adapters/codex/` holds Codex-specific plugin metadata, skills, and config templates.
- `mcp/` holds future MCP bridges for knowledge, review, and security.
- `packs/` groups optional capability bundles and now acts as the canonical pack registry source.
- `templates/` stores reusable vault and project scaffolding.

## Python Modules

- `src/chef/cli.py` keeps argument parsing and command dispatch.
- `src/chef/scaffold.py` owns vault creation, compatibility links, manifests, and verification checks.
- `src/chef/packs.py` owns pack registry and enabled-pack state.
- `src/chef/hosts.py` owns host-specific install copy logic.
- `src/chef/graphify.py` owns Graphify binary resolution and refresh execution helpers.

## Graph-First Protocol

1. Query graph index first.
2. Query graph report next.
3. Query graph wiki pages next.
4. Read raw source only on explicit user request.

Primary index:

`chef/knowledge-vault/Graphify/graphify-out/wiki/index.md`

Compatibility path:

`chef/graphify-out/`

## Structured Knowledge Base

Required vault layout:

- `Home/`
- `Memory/`
- `Graphify/`

Required files:

- `Home/Home.md`
- `Memory/Memory.md`
- `Graphify/index.md`
- `Graphify/graphify-out/`

Repo root keeps one compatibility symlink:

- `graphify-out/ -> knowledge-vault/Graphify/graphify-out/`

## Routing

Claude:

- Executor: Sonnet
- Expert: Opus

Codex:

- Default: `gpt-5.4-mini` with `high`
- Expert: `gpt-5.4` with `xhigh`

## Orchestration Extraction

CHEF absorbs patterns from external frameworks without stacking them whole.

- Superpowers: planning gates, explicit handoffs, review discipline.
- gstack: operator commands, host-aware install, role packs.
- MassGen: task graph, retry model, subagent tracking.
- ruflo: swarm lifecycle, state model, memory-aware orchestration.
