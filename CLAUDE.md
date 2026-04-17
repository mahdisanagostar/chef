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

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
