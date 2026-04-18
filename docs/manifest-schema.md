# Chef Manifest Schema

## File

`project/.chef/chef.json`

## Purpose

Chef writes one manifest per initialized project.

The manifest records host mode, vault location, and graph entrypoints.

CLI verification, graph refresh, and MCP vault resolution all depend on this file.

## Required Keys

```json
{
  "project": "chef/",
  "host": "both",
  "vault": "knowledge-vault",
  "generated_at": "2026-04-17T13:20:12.626956+00:00",
  "graph_index": "knowledge-vault/Graphify/graphify-out/wiki/index.md",
  "graph_report": "knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md"
}
```

## Field Rules

- `project`
  Constant string for the Chef project family.
- `host`
  One of
  `claude`
  `codex`
  `both`
- `vault`
  Relative path from project root when vault lives inside project, or absolute path for external vaults.
- `generated_at`
  Non-empty ISO
  8601
  timestamp.
- `graph_index`
  Relative or absolute path to
  `wiki/index.md`
  inside graph output.
- `graph_report`
  Relative or absolute path to
  `GRAPH_REPORT.md`
  inside graph output.

## Validation Behavior

- Missing manifest makes
  `chef verify`
  and
  `chef graph-refresh`
  fail.
- Invalid JSON or unsupported host value makes CLI commands fail with a clear validation error.
- MCP helpers fall back to default
  `knowledge-vault`
  resolution and prepend a warning when manifest data looks invalid.

## External Vault Example

```json
{
  "project": "chef/",
  "host": "codex",
  "vault": "/Users/example/shared-vault",
  "generated_at": "2026-04-17T13:20:12.626956+00:00",
  "graph_index": "/Users/example/shared-vault/Graphify/graphify-out/wiki/index.md",
  "graph_report": "/Users/example/shared-vault/Graphify/graphify-out/GRAPH_REPORT.md"
}
```

## Notes

- Chef treats the manifest as generated state.
- Edit by hand only when repairing a broken setup.
- Re-running
  `chef init`
  rewrites the manifest from current project inputs.
