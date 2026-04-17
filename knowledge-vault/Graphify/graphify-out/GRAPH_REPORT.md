# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 13 files · ~4,771 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 78 nodes · 153 edges · 9 communities detected
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 57 edges (avg confidence: 0.8)
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
1. `read_text()` - 15 edges
2. `ChefCliTests` - 11 edges
3. `cmd_graph_refresh()` - 10 edges
4. `detect_project()` - 8 edges
5. `cmd_init()` - 8 edges
6. `read_enabled_packs()` - 7 edges
7. `graph_index_path()` - 7 edges
8. `graph_report_path()` - 7 edges
9. `run_command()` - 6 edges
10. `ensure_vault()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `cmd_init()` --calls--> `ensure_vault()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py
- `cmd_init()` --calls--> `ensure_graphify_compat()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py
- `cmd_init()` --calls--> `ensure_project_files()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py
- `cmd_init()` --calls--> `write_manifest()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py
- `cmd_graph_refresh()` --calls--> `load_manifest()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.2
Nodes (5): cmd_install(), install_claude(), install_codex(), ChefCliTests, run_command()

### Community 1 - "Community 1"
Cohesion: 0.23
Nodes (11): cmd_verify(), graph_dir(), read_text(), resolve_project(), vault_dir(), list_graph_pages(), read_graph_index(), read_graph_page() (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (11): build_parser(), cmd_init(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github(), detect_project(), main(), pack_state_path() (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.32
Nodes (11): build_manifest(), build_verify_checks(), ensure_graph_placeholders(), ensure_project_files(), ensure_vault(), manifest_path_value(), read_template(), resolve_project_path() (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.24
Nodes (6): graph_index_path(), graph_report_path(), review_context(), review_sources(), security_context(), security_review_order()

### Community 5 - "Community 5"
Cohesion: 0.33
Nodes (6): cmd_graph_refresh(), resolve_graphify_binary(), run_graphify_command(), sync_graphify_outputs(), ensure_graphify_compat(), merge_tree()

### Community 6 - "Community 6"
Cohesion: 1.0
Nodes (0): 

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (0): 

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **Thin community `Community 6`** (1 nodes): `paths.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.523) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 5` to `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Why does `ChefCliTests` connect `Community 0` to `Community 5`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `read_text()` (e.g. with `.test_existing_vault_content_survives_init()` and `.test_graph_refresh_dry_run_preserves_existing_graph_outputs()`) actually correct?**
  _`read_text()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `cmd_graph_refresh()` (e.g. with `load_manifest()` and `resolve_project_path()`) actually correct?**
  _`cmd_graph_refresh()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `cmd_init()` (e.g. with `ensure_vault()` and `ensure_graphify_compat()`) actually correct?**
  _`cmd_init()` has 6 INFERRED edges - model-reasoned connections that need verification._