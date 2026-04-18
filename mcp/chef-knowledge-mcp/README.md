# chef-knowledge-mcp

Knowledge MCP server for Chef.

## Entry Point

```bash
chef-knowledge-mcp
```

## Tools

- `vault_summary`
- `search_vault_notes`
- `read_note`
- `write_note`
- `list_backlinks`
- `read_graph_index`
- `read_graph_report`
- `list_graph_pages`
- `read_graph_page`
- `graph_status`
- `refresh_graph_if_stale`

## Codex Config

```toml
[mcp_servers.chef_knowledge]
command = ".venv/bin/chef-knowledge-mcp"
```

## Claude Config

Use stdio MCP registration and point it at:

`.venv/bin/chef-knowledge-mcp`
