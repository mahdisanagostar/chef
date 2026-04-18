# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-18)

## Corpus Check
- 21 files · ~23,123 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 189 nodes · 449 edges · 13 communities detected
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 148 edges (avg confidence: 0.8)
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
1. `read_text()` - 31 edges
2. `ChefCliTests` - 22 edges
3. `run_command()` - 16 edges
4. `sync_external_items()` - 16 edges
5. `manifest_warning()` - 14 edges
6. `fetch_snapshot()` - 13 edges
7. `cmd_graph_refresh()` - 11 edges
8. `read_pack_registry()` - 10 edges
9. `resolve_enabled_items()` - 10 edges
10. `install_claude()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `read_item_catalog()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `vendor_dir()` --calls--> `vendor_root()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/paths.py → /Users/mahdi/Desktop/git/chef/src/chef/external.py
- `claude_plugin_dir()` --calls--> `install_claude_plugin_item()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/paths.py → /Users/mahdi/Desktop/git/chef/src/chef/external.py
- `claude_skill_dir()` --calls--> `install_skill_like_item()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/paths.py → /Users/mahdi/Desktop/git/chef/src/chef/external.py
- `codex_skill_dir()` --calls--> `install_skill_like_item()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/paths.py → /Users/mahdi/Desktop/git/chef/src/chef/external.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (30): Exception, build_wrapper_skill(), copy_directory(), detect_claude_plugin_dir(), detect_skill_dir(), download_repo_zip(), ensure_clean_cache(), ensure_codex_plugin_declares_mcp() (+22 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (18): graph_dir(), graph_index_path(), graph_report_path(), manifest_warning(), read_text(), resolve_project(), vault_dir(), list_graph_pages() (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (23): cmd_graph_refresh(), cmd_verify(), resolve_graphify_binary(), run_graphify_command(), sync_graphify_outputs(), build_manifest(), build_verify_checks(), ensure_graph_placeholders() (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (21): codex_mcp_path(), codex_plugin_path(), verify_external_items(), copy_asset(), install_bundled_skills(), install_claude(), install_codex(), replace_path() (+13 more)

### Community 4 - "Community 4"
Cohesion: 0.21
Nodes (18): normalize_catalog_item(), read_item_catalog(), build_parser(), cmd_init(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.22
Nodes (3): SyncResult, ChefCliTests, run_command()

### Community 6 - "Community 6"
Cohesion: 0.44
Nodes (10): build_policy_checks(), _claude_commands(), _enabled_skill_items(), _format_list(), _load_manifest(), _project_path_value(), render_claude_policy(), render_codex_policy() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.29
Nodes (2): HtmlTextExtractor, HTMLParser

### Community 8 - "Community 8"
Cohesion: 0.67
Nodes (2): getTypedText(), MyAnimation()

### Community 9 - "Community 9"
Cohesion: 1.0
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
- **Thin community `Community 9`** (1 nodes): `text-animations-word-highlight.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `charts-bar-chart.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.439) - this node is a cross-community bridge._
- **Why does `manifest_warning()` connect `Community 1` to `Community 2`, `Community 5`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `verify_external_items()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `read_text()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_writes_codex_mcp_config()`) actually correct?**
  _`read_text()` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `sync_external_items()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_installs_claude_plugin_when_detected()`) actually correct?**
  _`sync_external_items()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `manifest_warning()` (e.g. with `.test_external_vault_resolution_and_warnings()` and `.test_invalid_manifest_warning_falls_back_to_default_vault()`) actually correct?**
  _`manifest_warning()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._