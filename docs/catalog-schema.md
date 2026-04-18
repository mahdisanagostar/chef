# Chef Catalog Schema

Chef keeps one capability catalog in
`catalog/items.json`
.

Each entry uses the item id as the JSON key and defines:

- `name`: human label
- `kind`: capability type such as `skill`, `plugin`, `mcp_server`, `repo`, or `codex_skill`
- `hosts`: one or both of `claude`, `codex`
- `install.method`: `bundled` or `manual`
- `install.path`: required for `bundled` items
- `source_url`: required for `manual` items
- `mcp`: optional command and args for Codex MCP registration
- `always_installed`: optional boolean for baseline bundled items

Meaning:

- `bundled` items ship inside this repo and Chef can install them directly into project-local runtime
- `manual` items fetch from upstream URLs into `.chef/vendor/` and install into managed local targets
- `always_installed` applies to bundled baseline items that should install even when no pack enables them
- `mcp` lets Chef write Codex MCP server entries during install

Pack rules:

- `packs/*/pack.json` must reference valid catalog ids
- `chef pack-status` resolves enabled packs into catalog items
- `chef install` syncs manual items into local skill or plugin targets and writes Codex MCP config when available
- `chef install --offline` reuses cache or emits managed wrapper fallbacks instead of reaching upstream
