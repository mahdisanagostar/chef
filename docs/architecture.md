# Chef Architecture

## Shape

Chef ships one repository with one shared core and two isolated host adapters.

- `core/` holds policy, routing, manifests, and orchestration extraction.
- `adapters/claude/` holds Claude-specific commands and plugin metadata.
- `adapters/codex/` holds Codex-specific plugin metadata, skills, and config templates.
- `adapters/shared/` holds vendored cross-host bundled skills.
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
- `src/chef/hosts.py` owns host-specific install copy logic, target replacement behavior, and bundled skill selection.
- `src/chef/graphify.py` owns Graphify binary resolution and refresh execution helpers.

## Generated State

- `.chef/chef.json` stores validated host and vault routing data.
- `.chef/enabled-packs.json` stores selected pack ids.
- `.chef/vendor/` stores cached upstream material snapshots.
- `.claude/commands/`, `.claude/plugins/`, and `.claude/skills/` store project-local Claude runtime output.
- `.codex/skills/` stores project-local Codex skills.
- `.codex-plugin/` stores project-local Codex plugin and MCP config.
- Manifest schema details live in
  [docs/manifest-schema.md](manifest-schema.md)
- Catalog schema details live in
  [docs/catalog-schema.md](catalog-schema.md)

Chef no longer writes runtime assets into home directories. Install output stays inside the project tree so the repo behaves like a self-contained workspace image.

## Pack Resolution

- Packs resolve through `catalog/items.json`, not free-form strings.
- Each pack item must exist in the catalog.
- `chef pack-status` expands enabled packs into concrete item ids.
- `chef install` materializes bundled items into project-local host runtime from that resolved set.
- Manual catalog items sync into `.chef/vendor/` first and install into local skill/plugin targets or Codex MCP config.
- `chef pack-enable` also installs newly enabled packs into the project runtime for the manifest host.
- `chef install --offline` uses cache-first behavior and wrapper fallbacks.
- `chef verify` checks enabled item targets inside the project tree.

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

Chef absorbs patterns from external frameworks without stacking them whole.

- Superpowers: planning gates, explicit handoffs, review discipline.
- gstack: operator commands, host-aware install, role packs.
- MassGen: task graph, retry model, subagent tracking.
- ruflo: swarm lifecycle, state model, memory-aware orchestration.
