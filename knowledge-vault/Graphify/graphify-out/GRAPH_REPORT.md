# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 8 files · ~4,321 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 66 nodes · 137 edges · 13 communities detected
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `read_text()` - 14 edges
2. `cmd_graph_refresh()` - 9 edges
3. `detect_project()` - 8 edges
4. `cmd_init()` - 8 edges
5. `ChefCliTests` - 7 edges
6. `read_enabled_packs()` - 7 edges
7. `graph_index_path()` - 7 edges
8. `graph_report_path()` - 7 edges
9. `run_command()` - 6 edges
10. `ensure_vault()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `graph_dir()` --calls--> `list_graph_pages()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/knowledge.py
- `read_template()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `read_pack_registry()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `read_enabled_packs()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `cmd_graph_refresh()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.36
Nodes (2): ChefCliTests, run_command()

### Community 1 - "Community 1"
Cohesion: 0.32
Nodes (6): read_text(), list_graph_pages(), read_graph_index(), read_graph_page(), read_graph_report(), vault_summary()

### Community 2 - "Community 2"
Cohesion: 0.4
Nodes (6): cmd_init(), manifest_path_value(), pack_state_path(), write_enabled_packs(), write_file(), write_manifest()

### Community 3 - "Community 3"
Cohesion: 0.53
Nodes (5): build_parser(), cmd_install(), install_claude(), install_codex(), main()

### Community 4 - "Community 4"
Cohesion: 0.47
Nodes (6): cmd_graph_refresh(), ensure_graphify_compat(), merge_tree(), resolve_graphify_binary(), run_graphify_command(), sync_graphify_outputs()

### Community 5 - "Community 5"
Cohesion: 0.4
Nodes (3): graph_report_path(), review_context(), review_sources()

### Community 6 - "Community 6"
Cohesion: 0.4
Nodes (3): graph_index_path(), security_context(), security_review_order()

### Community 7 - "Community 7"
Cohesion: 0.6
Nodes (5): ensure_graph_placeholders(), ensure_project_files(), ensure_vault(), read_template(), write_file_if_missing()

### Community 8 - "Community 8"
Cohesion: 0.83
Nodes (4): cmd_pack_enable(), cmd_pack_status(), read_enabled_packs(), read_pack_registry()

### Community 9 - "Community 9"
Cohesion: 0.5
Nodes (4): cmd_publish_github(), cmd_verify(), detect_project(), resolve_project_path()

### Community 10 - "Community 10"
Cohesion: 0.83
Nodes (3): graph_dir(), resolve_project(), vault_dir()

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **Thin community `Community 11`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 1` to `Community 0`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.546) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 4` to `Community 9`, `Community 3`, `Community 1`, `Community 7`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `read_pack_registry()` connect `Community 8` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `read_text()` (e.g. with `.test_existing_vault_content_survives_init()` and `.test_graph_refresh_dry_run_preserves_existing_graph_outputs()`) actually correct?**
  _`read_text()` has 13 INFERRED edges - model-reasoned connections that need verification._