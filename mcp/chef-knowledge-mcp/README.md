# chef-knowledge-mcp

Knowledge MCP server for CHEF.

## Entry Point

```bash
chef-knowledge-mcp
```

## Tools

- `vault_summary`
- `read_graph_index`
- `read_graph_report`
- `list_graph_pages`
- `read_graph_page`

## Codex Config

```toml
[mcp_servers.chef_knowledge]
command = ".venv/bin/chef-knowledge-mcp"
```

## Claude Config

Use stdio MCP registration and point it at:

`.venv/bin/chef-knowledge-mcp`

