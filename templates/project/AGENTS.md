# CHEF Codex Policy

## Graph-First Rule

1. Query `knowledge-vault/Graphify/graphify-out/wiki/index.md` first.
2. Query `knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md` next.
3. Read raw source only when user explicitly requests.
4. Treat repo-root `graphify-out/` as compatibility alias only.

## Routing

- Default model: `gpt-5.4-mini`
- Default reasoning: `high`
- Expert model: `gpt-5.4`
- Expert reasoning: `xhigh`

## Skills

- `$chef-index`
- `$graph-first-retrieval`
- `$skill-finder`
