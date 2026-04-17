# CHEF Architecture

## Shape

CHEF ships one repository with one shared core and two isolated host adapters.

- `core/` holds policy, routing, manifests, and orchestration extraction.
- `adapters/claude/` holds Claude-specific commands and plugin metadata.
- `adapters/codex/` holds Codex-specific plugin metadata, skills, and config templates.
- `catalog/` maps capability ids to host support, upstream source, and install method.
- `mcp/` holds future MCP bridges for knowledge, review, and security.
- `packs/` groups optional capability bundles and now acts as the canonical pack registry source.
- `templates/` stores reusable vault and project scaffolding.

## Python Modules

- `src/chef/cli.py` keeps argument parsing and command dispatch.
- `src/chef/catalog.py` owns catalog loading and validation.
- `src/chef/external.py` owns external source fetch, wrapper generation, Claude plugin sync, and Codex MCP config writes.
- `src/chef/scaffold.py` owns vault creation, compatibility links, manifests, and verification checks.
- `src/chef/packs.py` owns pack registry, enabled-pack state, and item resolution.
- `src/chef/hosts.py` owns host-specific install copy logic, backup restore behavior, and bundled Codex skill selection.
- `src/chef/graphify.py` owns Graphify binary resolution and refresh execution helpers.

## Generated State

- `.chef/chef.json` stores validated host and vault routing data.
- `.chef/enabled-packs.json` stores selected pack ids.
- Manifest schema details live in
  [docs/manifest-schema.md](manifest-schema.md)
- Catalog schema details live in
  [docs/catalog-schema.md](catalog-schema.md)

## Pack Resolution

- Packs resolve through `catalog/items.json`, not free-form strings.
- Each pack item must exist in the catalog.
- `chef pack-status` expands enabled packs into concrete item ids.
- `chef install` installs bundled Codex skills from that resolved set.
- Manual catalog items now sync into local skill/plugin targets or Codex MCP config.
- `chef verify` checks enabled external item targets too.

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
