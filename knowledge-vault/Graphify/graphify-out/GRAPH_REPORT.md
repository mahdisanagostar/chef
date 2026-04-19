# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-19)

## Corpus Check
- 29 files · ~37,637 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 323 nodes · 837 edges · 18 communities detected
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 262 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]

## God Nodes (most connected - your core abstractions)
1. `read_text()` - 49 edges
2. `ChefCliTests` - 28 edges
3. `sync_external_items()` - 21 edges
4. `run_command()` - 20 edges
5. `manifest_warning()` - 20 edges
6. `fetch_snapshot()` - 16 edges
7. `resolve_enabled_items()` - 15 edges
8. `read_pack_registry()` - 14 edges
9. `vault_dir()` - 13 edges
10. `ChefExternalTests` - 12 edges

## Surprising Connections (you probably didn't know these)
- `read_item_catalog()` --calls--> `read_text()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/mcp/common.py
- `read_item_catalog()` --calls--> `read_pack_registry()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/packs.py
- `read_item_catalog()` --calls--> `resolve_enabled_items()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/catalog.py → /Users/mahdi/Desktop/git/chef/src/chef/packs.py
- `vendor_dir()` --calls--> `vendor_root()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/paths.py → /Users/mahdi/Desktop/git/chef/src/chef/external.py
- `install_state_file()` --calls--> `build_verify_checks()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/paths.py → /Users/mahdi/Desktop/git/chef/src/chef/scaffold.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (40): graph_dir(), graph_index_path(), graph_report_path(), is_vault_note(), manifest_warning(), note_identifier(), note_rel_path(), read_path_snippets() (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (37): Exception, adapter_notes_for_host(), build_install_record(), build_wrapper_skill(), copy_directory(), detect_claude_plugin_dir(), detect_skill_dir(), download_repo_zip() (+29 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (31): normalize_catalog_item(), read_item_catalog(), codex_mcp_path(), codex_plugin_path(), ensure_codex_plugin_declares_mcp(), merge_codex_mcp_entries(), verify_external_items(), verify_external_items_report() (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (30): cmd_graph_refresh(), detect_agent_host(), graph_json_path(), graph_report_file(), graph_status(), _ignored_graph_path(), iter_graph_inputs(), refresh_graph_if_stale() (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (32): apply_pack_state(), build_bundled_records(), build_install_plan(), build_parser(), build_verify_report(), cmd_init(), cmd_install(), cmd_pack_disable() (+24 more)

### Community 5 - "Community 5"
Cohesion: 0.19
Nodes (4): read_text(), SyncResult, ChefCliTests, run_command()

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (13): build_policy_checks(), _claude_commands(), _enabled_skill_items(), _format_list(), _graphify_codex_section(), _load_manifest(), _project_path_value(), render_claude_policy() (+5 more)

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (14): build_report(), Check, detect_concreteness(), detect_transitions(), extract_fence_sections(), FenceSection, Heading, main() (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.53
Nodes (8): choose_runtime(), find_validator(), main(), repo_root(), runtime_candidates(), skill_root(), supports_yaml(), validator_candidates()

### Community 9 - "Community 9"
Cohesion: 0.58
Nodes (8): compare_dirs(), default_mirror(), iter_files(), main(), relative_file_map(), repo_root(), skill_root(), sync_dirs()

### Community 10 - "Community 10"
Cohesion: 0.31
Nodes (2): HtmlTextExtractor, HTMLParser

### Community 11 - "Community 11"
Cohesion: 0.57
Nodes (6): merge_host_records(), read_install_state(), record_for(), state_key(), write_install_state(), install_state_file()

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (1): TalkCraftTests

### Community 13 - "Community 13"
Cohesion: 0.67
Nodes (2): getTypedText(), MyAnimation()

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **1 isolated node(s):** `Check`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (1 nodes): `text-animations-word-highlight.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `charts-bar-chart.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 11`, `Community 12`?**
  _High betweenness centrality (0.393) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 3` to `Community 4`, `Community 5`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `manifest_warning()` connect `Community 0` to `Community 3`, `Community 5`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `read_text()` (e.g. with `.test_quick_validate_uses_override_validator()` and `.test_skill_finder_docs_cover_host_native_routes_and_fast_path()`) actually correct?**
  _`read_text()` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `sync_external_items()` (e.g. with `.test_sync_external_installs_codex_wrapper_skill()` and `.test_sync_external_installs_claude_plugin_when_detected()`) actually correct?**
  _`sync_external_items()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `manifest_warning()` (e.g. with `.test_external_vault_resolution_and_warnings()` and `.test_invalid_manifest_warning_falls_back_to_default_vault()`) actually correct?**
  _`manifest_warning()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Check` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._