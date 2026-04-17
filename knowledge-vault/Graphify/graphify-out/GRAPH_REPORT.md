# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-18)

## Corpus Check
- 20 files · ~21,387 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 182 nodes · 424 edges · 12 communities detected
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 139 edges (avg confidence: 0.8)
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

## God Nodes (most connected - your core abstractions)
1. `read_text()` - 27 edges
2. `ChefCliTests` - 21 edges
3. `run_command()` - 15 edges
4. `sync_external_items()` - 14 edges
5. `manifest_warning()` - 14 edges
6. `fetch_snapshot()` - 13 edges
7. `cmd_graph_refresh()` - 11 edges
8. `backup_existing_path()` - 10 edges
9. `read_pack_registry()` - 10 edges
10. `restore_target()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `read_item_catalog()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `read_item_catalog()` --calls--> `read_pack_registry()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/packs.py
- `read_item_catalog()` --calls--> `resolve_enabled_items()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/packs.py
- `vendor_root()` --calls--> `vendor_dir()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/external.py → /Users/mahdi/Desktop/git/chef/src/chef/paths.py
- `install_claude_plugin_item()` --calls--> `claude_plugin_dir()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/external.py → /Users/mahdi/Desktop/git/chef/src/chef/paths.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (32): read_text(), Exception, backup_and_copy_skill(), build_wrapper_skill(), codex_mcp_path(), codex_plugin_path(), copy_directory(), detect_claude_plugin_dir() (+24 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (36): build_parser(), cmd_graph_refresh(), cmd_init(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github(), cmd_restore_backup() (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (25): install_skill_like_item(), backup_existing_path(), backup_root(), copy_asset(), install_bundled_skills(), install_claude(), install_codex(), parse_backup_label() (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (18): graph_dir(), graph_index_path(), graph_report_path(), manifest_warning(), resolve_project(), vault_dir(), list_graph_pages(), read_graph_index() (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (5): SyncResult, resolve_graphify_binary(), run_graphify_command(), ChefCliTests, run_command()

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (3): extract_html_text(), HtmlTextExtractor, HTMLParser

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (2): getTypedText(), MyAnimation()

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (2): normalize_catalog_item(), read_item_catalog()

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0): 

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (0): 

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **Thin community `Community 8`** (1 nodes): `text-animations-word-highlight.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `charts-bar-chart.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.437) - this node is a cross-community bridge._
- **Why does `manifest_warning()` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `verify_external_items()` connect `Community 0` to `Community 1`, `Community 2`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `read_text()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_writes_codex_mcp_config()`) actually correct?**
  _`read_text()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `sync_external_items()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_installs_claude_plugin_when_detected()`) actually correct?**
  _`sync_external_items()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `manifest_warning()` (e.g. with `.test_external_vault_resolution_and_warnings()` and `.test_invalid_manifest_warning_falls_back_to_default_vault()`) actually correct?**
  _`manifest_warning()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._