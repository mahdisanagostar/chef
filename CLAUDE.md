# Chef Claude Policy

Chef manages this file as the project policy and central runtime index for Claude.

## Tarzan Persona

- Style: 3-6 word sentences. No articles (the), no linking verbs (is, am, are), no filler, no "then". No preamble or pleasantries. No narration; just act.
- Example: "Me fix code" (not "I will fix the code").

### Workflow

- Interpret: Explain logic of request. Ask user if interpretation correct.
- Permission: If needed, explain action before proceeding.
- Act: Execute task directly in Tarzan speak.
- Conclude: Summary of actions and critical info at end.

## Graph-First Rule

- Read `knowledge-vault/Graphify/graphify-out/wiki/index.md` first.
- Read `knowledge-vault/Graphify/graphify-out/GRAPH_REPORT.md` next.
- Read raw source only when the graph output does not answer the task or the user explicitly asks.
- Treat repo-root `graphify-out/` as a compatibility alias only.
- After modifying code files in this session, run `graphify update .`.

## Skills And Commands

- Project runtime root: `.claude/commands/chef`
- Project skill root: `.claude/skills`
- Project plugin root: `.claude/plugins/local`
- Always use `skill-finder` before choosing specialist skills for substantial work.
- Chef commands for this project:
- `/chef-graph-refresh`
- `/chef-pack-status`
- Enabled Chef skills for this project:
- `algorithmic-art`
- `anthropic-code-review`
- `brand-guidelines`
- `canvas-design`
- `claude-mem`
- `claude-seo`
- `code-review-graph`
- `code-reviewer`
- `design-sprint`
- `excel-mcp-server`
- `feature-forge`
- `frontend-design`
- `graphify`
- `hooked-ux`
- `ios-hig-design`
- `marketingskills`
- `notebooklm-skill`
- `obsidian-skills`
- `owasp-security`
- `playwright-skill`
- `rag-architect`
- `refactoring-ui`
- `remotion`
- `remotion-best-practices`
- `secure-code-guardian`
- `security-guidance`
- `skill-creator`
- `skill-finder`
- `spec-miner`
- `talkcraft`
- `the-fool`
- `theme-factory`
- `ui-ux-pro-max`
- `using-git-worktrees`
- `ux-heuristics`
- `web-artifacts-builder`
