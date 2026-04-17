# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 7 files · ~3,093 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 55 nodes · 117 edges · 9 communities detected
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.8)
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

## God Nodes (most connected - your core abstractions)
1. `read_text()` - 11 edges
2. `cmd_graph_refresh()` - 9 edges
3. `detect_project()` - 8 edges
4. `cmd_init()` - 8 edges
5. `read_enabled_packs()` - 7 edges
6. `graph_index_path()` - 7 edges
7. `graph_report_path()` - 7 edges
8. `write_file()` - 6 edges
9. `ensure_vault()` - 6 edges
10. `graph_dir()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `read_template()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `read_pack_registry()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `read_enabled_packs()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `cmd_graph_refresh()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `cmd_verify()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.24
Nodes (6): graph_index_path(), graph_report_path(), review_context(), review_sources(), security_context(), security_review_order()

### Community 1 - "Community 1"
Cohesion: 0.27
Nodes (9): graph_dir(), read_text(), resolve_project(), vault_dir(), list_graph_pages(), read_graph_index(), read_graph_page(), read_graph_report() (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.48
Nodes (7): cmd_init(), cmd_pack_enable(), cmd_pack_status(), pack_state_path(), read_enabled_packs(), read_pack_registry(), write_enabled_packs()

### Community 3 - "Community 3"
Cohesion: 0.47
Nodes (6): ensure_graph_placeholders(), ensure_project_files(), ensure_vault(), read_template(), write_file(), write_manifest()

### Community 4 - "Community 4"
Cohesion: 0.47
Nodes (6): cmd_graph_refresh(), ensure_graphify_compat(), merge_tree(), resolve_graphify_binary(), run_graphify_command(), sync_graphify_outputs()

### Community 5 - "Community 5"
Cohesion: 0.53
Nodes (5): build_parser(), cmd_install(), install_claude(), install_codex(), main()

### Community 6 - "Community 6"
Cohesion: 0.5
Nodes (4): cmd_publish_github(), cmd_verify(), detect_project(), resolve_project_path()

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (0): 

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **Thin community `Community 7`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.495) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 4` to `Community 1`, `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `security_context()` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `read_text()` (e.g. with `read_template()` and `read_pack_registry()`) actually correct?**
  _`read_text()` has 10 INFERRED edges - model-reasoned connections that need verification._