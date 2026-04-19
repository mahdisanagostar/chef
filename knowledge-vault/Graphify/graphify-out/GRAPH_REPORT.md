# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-19)

## Corpus Check
- 24 files · ~28,763 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 245 nodes · 589 edges · 15 communities detected
- Extraction: 68% EXTRACTED · 32% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]

## God Nodes (most connected - your core abstractions)
1. `read_text()` - 39 edges
2. `ChefCliTests` - 24 edges
3. `run_command()` - 16 edges
4. `sync_external_items()` - 16 edges
5. `manifest_warning()` - 16 edges
6. `fetch_snapshot()` - 13 edges
7. `vault_dir()` - 13 edges
8. `cmd_graph_refresh()` - 12 edges
9. `list_backlinks()` - 12 edges
10. `read_pack_registry()` - 10 edges

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
Cohesion: 0.1
Nodes (33): read_text(), Exception, build_wrapper_skill(), copy_directory(), detect_claude_plugin_dir(), detect_skill_dir(), download_repo_zip(), ensure_clean_cache() (+25 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (32): graph_dir(), graph_index_path(), graph_report_path(), is_vault_note(), manifest_warning(), note_identifier(), note_rel_path(), resolve_note_path() (+24 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (31): cmd_graph_refresh(), cmd_verify(), detect_agent_host(), graph_json_path(), graph_report_file(), graph_status(), _ignored_graph_path(), iter_graph_inputs() (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (23): codex_mcp_path(), codex_plugin_path(), verify_external_items(), codex_builtin_mcp_servers(), copy_asset(), ensure_codex_builtin_mcp(), install_bundled_skills(), install_claude() (+15 more)

### Community 4 - "Community 4"
Cohesion: 0.23
Nodes (18): normalize_catalog_item(), read_item_catalog(), build_parser(), cmd_init(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.2
Nodes (3): SyncResult, ChefCliTests, run_command()

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (14): build_report(), Check, detect_concreteness(), detect_transitions(), extract_fence_sections(), FenceSection, Heading, main() (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.39
Nodes (11): build_policy_checks(), _claude_commands(), _enabled_skill_items(), _format_list(), _graphify_codex_section(), _load_manifest(), _project_path_value(), render_claude_policy() (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.57
Nodes (6): compare_dirs(), iter_files(), main(), relative_file_map(), skill_root(), sync_dirs()

### Community 9 - "Community 9"
Cohesion: 0.5
Nodes (1): TalkcraftTests

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (2): getTypedText(), MyAnimation()

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **1 isolated node(s):** `Check`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (1 nodes): `text-animations-word-highlight.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `charts-bar-chart.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.407) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 2` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `ChefCliTests` connect `Community 5` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `read_text()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_writes_codex_mcp_config()`) actually correct?**
  _`read_text()` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `sync_external_items()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_installs_claude_plugin_when_detected()`) actually correct?**
  _`sync_external_items()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `manifest_warning()` (e.g. with `.test_external_vault_resolution_and_warnings()` and `.test_invalid_manifest_warning_falls_back_to_default_vault()`) actually correct?**
  _`manifest_warning()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Check` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._