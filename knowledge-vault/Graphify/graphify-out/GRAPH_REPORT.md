# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 13 files · ~5,796 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 91 nodes · 203 edges · 13 communities detected
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.8)
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
1. `read_text()` - 16 edges
2. `ChefCliTests` - 14 edges
3. `manifest_warning()` - 13 edges
4. `cmd_graph_refresh()` - 11 edges
5. `run_command()` - 9 edges
6. `detect_project()` - 8 edges
7. `cmd_init()` - 8 edges
8. `read_pack_registry()` - 8 edges
9. `graph_index_path()` - 8 edges
10. `graph_report_path()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `install_claude()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `install_codex()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `cmd_init()` --calls--> `ensure_vault()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py
- `cmd_init()` --calls--> `ensure_graphify_compat()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py
- `cmd_init()` --calls--> `ensure_project_files()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/cli.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.23
Nodes (17): cmd_verify(), build_manifest(), build_verify_checks(), ensure_graph_placeholders(), ensure_project_files(), ensure_vault(), load_manifest(), load_manifest_if_present() (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.25
Nodes (14): build_parser(), cmd_init(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github(), detect_project(), main() (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.36
Nodes (2): ChefCliTests, run_command()

### Community 3 - "Community 3"
Cohesion: 0.33
Nodes (6): cmd_graph_refresh(), resolve_graphify_binary(), run_graphify_command(), sync_graphify_outputs(), ensure_graphify_compat(), merge_tree()

### Community 4 - "Community 4"
Cohesion: 0.31
Nodes (7): graph_dir(), read_text(), list_graph_pages(), read_graph_index(), read_graph_page(), read_graph_report(), vault_summary()

### Community 5 - "Community 5"
Cohesion: 0.39
Nodes (5): backup_existing_path(), backup_root(), install_claude(), install_codex(), timestamp_label()

### Community 6 - "Community 6"
Cohesion: 0.61
Nodes (7): graph_index_path(), graph_report_path(), manifest_warning(), review_context(), review_sources(), security_context(), security_review_order()

### Community 7 - "Community 7"
Cohesion: 0.67
Nodes (0): 

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (2): resolve_project(), vault_dir()

### Community 9 - "Community 9"
Cohesion: 0.67
Nodes (0): 

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

- **Why does `read_text()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.315) - this node is a cross-community bridge._
- **Why does `ChefCliTests` connect `Community 2` to `Community 1`, `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `read_text()` (e.g. with `.test_existing_vault_content_survives_init()` and `.test_graph_refresh_dry_run_preserves_existing_graph_outputs()`) actually correct?**
  _`read_text()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `manifest_warning()` (e.g. with `.test_mcp_common_uses_manifest_defined_external_vault()` and `.test_verify_reports_invalid_manifest_cleanly()`) actually correct?**
  _`manifest_warning()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `cmd_graph_refresh()` (e.g. with `manifest_path()` and `load_manifest()`) actually correct?**
  _`cmd_graph_refresh()` has 9 INFERRED edges - model-reasoned connections that need verification._