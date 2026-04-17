# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 15 files · ~7,930 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 109 nodes · 244 edges · 13 communities detected
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.8)
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
1. `ChefCliTests` - 19 edges
2. `read_text()` - 18 edges
3. `run_command()` - 14 edges
4. `manifest_warning()` - 14 edges
5. `cmd_graph_refresh()` - 11 edges
6. `read_pack_registry()` - 10 edges
7. `detect_project()` - 9 edges
8. `cmd_init()` - 9 edges
9. `read_enabled_packs()` - 8 edges
10. `resolve_enabled_items()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `graph_dir()` --calls--> `list_graph_pages()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/knowledge.py
- `read_item_catalog()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `restore_backup()` --calls--> `cmd_restore_backup()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `install_claude()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `install_codex()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.22
Nodes (18): normalize_catalog_item(), read_item_catalog(), build_parser(), cmd_init(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github() (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.23
Nodes (17): cmd_verify(), build_manifest(), build_verify_checks(), ensure_graph_placeholders(), ensure_project_files(), ensure_vault(), load_manifest(), load_manifest_if_present() (+9 more)

### Community 2 - "Community 2"
Cohesion: 0.21
Nodes (2): ChefCliTests, run_command()

### Community 3 - "Community 3"
Cohesion: 0.31
Nodes (8): backup_existing_path(), backup_root(), install_claude(), install_codex(), parse_backup_label(), restore_backup(), restore_target(), timestamp_label()

### Community 4 - "Community 4"
Cohesion: 0.33
Nodes (6): cmd_graph_refresh(), resolve_graphify_binary(), run_graphify_command(), sync_graphify_outputs(), ensure_graphify_compat(), merge_tree()

### Community 5 - "Community 5"
Cohesion: 0.43
Nodes (6): graph_index_path(), graph_report_path(), review_sources(), security_review_order(), ChefMcpTests, run_command()

### Community 6 - "Community 6"
Cohesion: 0.38
Nodes (5): read_text(), list_graph_pages(), read_graph_index(), read_graph_page(), read_graph_report()

### Community 7 - "Community 7"
Cohesion: 0.57
Nodes (5): graph_dir(), manifest_warning(), resolve_project(), vault_dir(), vault_summary()

### Community 8 - "Community 8"
Cohesion: 0.5
Nodes (1): security_context()

### Community 9 - "Community 9"
Cohesion: 0.5
Nodes (1): review_context()

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (0): 

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **Thin community `Community 10`** (1 nodes): `paths.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 6` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 7`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.378) - this node is a cross-community bridge._
- **Why does `manifest_warning()` connect `Community 7` to `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `ChefCliTests` connect `Community 2` to `Community 3`, `Community 4`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `read_text()` (e.g. with `.test_existing_vault_content_survives_init()` and `.test_graph_refresh_dry_run_preserves_existing_graph_outputs()`) actually correct?**
  _`read_text()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `manifest_warning()` (e.g. with `.test_external_vault_resolution_and_warnings()` and `.test_invalid_manifest_warning_falls_back_to_default_vault()`) actually correct?**
  _`manifest_warning()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `cmd_graph_refresh()` (e.g. with `manifest_path()` and `load_manifest()`) actually correct?**
  _`cmd_graph_refresh()` has 9 INFERRED edges - model-reasoned connections that need verification._