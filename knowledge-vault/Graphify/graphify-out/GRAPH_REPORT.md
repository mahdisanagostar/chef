# Graph Report - /Users/mahdi/Desktop/git/chef  (2026-04-17)

## Corpus Check
- 13 files · ~5,367 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 87 nodes · 180 edges · 12 communities detected
- Extraction: 65% EXTRACTED · 35% INFERRED · 0% AMBIGUOUS · INFERRED: 63 edges (avg confidence: 0.8)
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
1. `read_text()` - 15 edges
2. `ChefCliTests` - 14 edges
3. `cmd_graph_refresh()` - 11 edges
4. `run_command()` - 9 edges
5. `detect_project()` - 8 edges
6. `cmd_init()` - 8 edges
7. `read_pack_registry()` - 8 edges
8. `graph_index_path()` - 8 edges
9. `graph_report_path()` - 8 edges
10. `load_manifest()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `install_claude()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `install_codex()` --calls--> `cmd_install()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/hosts.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `run_graphify_command()` --calls--> `cmd_graph_refresh()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/graphify.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `resolve_graphify_binary()` --calls--> `cmd_graph_refresh()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/graphify.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py
- `sync_graphify_outputs()` --calls--> `cmd_graph_refresh()`  [INFERRED]
  /Users/mahdi/Desktop/git/chef/src/chef/graphify.py → /Users/mahdi/Desktop/git/chef/src/chef/cli.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.2
Nodes (4): install_claude(), install_codex(), ChefCliTests, run_command()

### Community 1 - "Community 1"
Cohesion: 0.25
Nodes (13): build_parser(), cmd_install(), cmd_pack_enable(), cmd_pack_status(), cmd_publish_github(), detect_project(), main(), normalize_legacy_registry() (+5 more)

### Community 2 - "Community 2"
Cohesion: 0.3
Nodes (13): cmd_init(), sync_graphify_outputs(), build_manifest(), ensure_graph_placeholders(), ensure_graphify_compat(), ensure_project_files(), ensure_vault(), manifest_path_value() (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.36
Nodes (10): cmd_graph_refresh(), cmd_verify(), read_text(), build_verify_checks(), load_manifest(), load_manifest_if_present(), manifest_path(), resolve_project_path() (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.33
Nodes (5): graph_dir(), list_graph_pages(), read_graph_index(), read_graph_page(), read_graph_report()

### Community 5 - "Community 5"
Cohesion: 0.4
Nodes (3): graph_index_path(), review_context(), review_sources()

### Community 6 - "Community 6"
Cohesion: 0.4
Nodes (3): graph_report_path(), security_context(), security_review_order()

### Community 7 - "Community 7"
Cohesion: 0.4
Nodes (2): resolve_graphify_binary(), run_graphify_command()

### Community 8 - "Community 8"
Cohesion: 0.67
Nodes (3): resolve_project(), vault_dir(), vault_summary()

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
- **Thin community `Community 9`** (1 nodes): `paths.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.416) - this node is a cross-community bridge._
- **Why does `cmd_graph_refresh()` connect `Community 3` to `Community 1`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `ChefCliTests` connect `Community 0` to `Community 1`, `Community 7`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `read_text()` (e.g. with `.test_existing_vault_content_survives_init()` and `.test_graph_refresh_dry_run_preserves_existing_graph_outputs()`) actually correct?**
  _`read_text()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `cmd_graph_refresh()` (e.g. with `manifest_path()` and `load_manifest()`) actually correct?**
  _`cmd_graph_refresh()` has 9 INFERRED edges - model-reasoned connections that need verification._