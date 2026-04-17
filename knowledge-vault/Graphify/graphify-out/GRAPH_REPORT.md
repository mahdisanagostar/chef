# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 17 files · ~10,345 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 158 nodes · 360 edges · 13 communities detected
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 112 edges (avg confidence: 0.8)
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
1. `read_text()` - 26 edges
2. `ChefCliTests` - 19 edges
3. `run_command()` - 14 edges
4. `manifest_warning()` - 14 edges
5. `fetch_snapshot()` - 12 edges
6. `sync_external_items()` - 12 edges
7. `cmd_graph_refresh()` - 11 edges
8. `read_pack_registry()` - 10 edges
9. `detect_project()` - 9 edges
10. `cmd_init()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `read_item_catalog()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `backup_and_copy_skill()` --calls--> `backup_existing_path()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/external.py → /Users/mahdi/Desktop/git/chef/src/chef/hosts.py
- `install_claude_plugin_item()` --calls--> `backup_existing_path()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/external.py → /Users/mahdi/Desktop/git/chef/src/chef/hosts.py
- `restore_backup()` --calls--> `cmd_restore_backup()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `install_claude()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (18): graph_dir(), graph_index_path(), graph_report_path(), manifest_warning(), read_text(), resolve_project(), vault_dir(), list_graph_pages() (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (5): SyncResult, resolve_graphify_binary(), run_graphify_command(), ChefCliTests, run_command()

### Community 2 - "Community 2"
Cohesion: 0.22
Nodes (19): normalize_catalog_item(), read_item_catalog(), build_parser(), cmd_init(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github() (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.2
Nodes (20): cmd_graph_refresh(), sync_graphify_outputs(), build_manifest(), build_verify_checks(), ensure_graph_placeholders(), ensure_graphify_compat(), ensure_project_files(), ensure_vault() (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.23
Nodes (17): backup_and_copy_skill(), build_wrapper_skill(), claude_plugin_target(), claude_skill_target(), codex_mcp_path(), codex_plugin_path(), codex_skill_target(), copy_directory() (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.31
Nodes (8): backup_existing_path(), backup_root(), install_claude(), install_codex(), parse_backup_label(), restore_backup(), restore_target(), timestamp_label()

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (10): Exception, download_repo_zip(), ensure_clean_cache(), fetch_snapshot(), InstallError, raw_github_url(), repo_readme_url(), request_bytes() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (4): fallback_snapshot(), Snapshot, sync_external_items(), ChefExternalTests

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (3): extract_html_text(), HtmlTextExtractor, HTMLParser

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (2): GitHubSource, parse_github_url()

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
- **Thin community `Community 9`** (2 nodes): `GitHubSource`, `parse_github_url()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `paths.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.469) - this node is a cross-community bridge._
- **Why does `manifest_warning()` connect `Community 0` to `Community 1`, `Community 3`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `ChefCliTests` connect `Community 1` to `Community 5`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `read_text()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_writes_codex_mcp_config()`) actually correct?**
  _`read_text()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `manifest_warning()` (e.g. with `.test_external_vault_resolution_and_warnings()` and `.test_invalid_manifest_warning_falls_back_to_default_vault()`) actually correct?**
  _`manifest_warning()` has 11 INFERRED edges - model-reasoned connections that need verification._