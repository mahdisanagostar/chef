# CHEF Claude Policy

## Graph-First Rule

1. Query `knowledge-vault/Graphify/graphify-out/wiki/index.md` first.
2. Query `knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md` next.
3. Read raw source only when user explicitly requests.
4. Treat repo-root `graphify-out/` as compatibility alias only.

## Routing

- Default executor: Sonnet
- Expert advisor: Opus

## Commands

- `/chef-graph-refresh`
- `/chef-expert-plan`
- `/chef-pack-status`
