---
name: skill-finder
description: Always-on Chef routing skill that runs at the start of any task to find the best specialist skills, choose the smallest useful set, order them, and re-evaluate when the task changes
---

# Skill Finder

## Mission

Use this as Chef's automatic routing layer.

Run it:

- right after `$chef-index` for Codex work
- before choosing specialist skills in Claude work
- again whenever the task changes shape, artifact, or risk

The goal is not to list every possible skill. The goal is to engage the fewest skills that materially improve the work.

## Fast Path

Do not force routing when the task is already small and obvious.

Skip specialist selection when:

- the user asks for a trivial shell action or one-command lookup
- the user names one exact skill or plugin route and no support changes execution
- the current step is a tiny follow-up inside an already-correct skill lane

## Default Behavior

For every non-trivial task:

1. honor explicit skill, plugin, or app requests first
2. classify the task
3. pick one primary skill
4. add at most one execution support and one verification support
5. explain the choice in one short line
6. re-run the check if scope shifts

If no specialist skill clearly helps, say so and continue without forcing one.

## Classification Pass

Look at seven things first:

1. `intent`
   build, review, debug, research, document, design, present, automate
2. `artifact`
   code, UI, deck, doc, spreadsheet, repo config, workflow, knowledge base
3. `risk`
   security, architecture, multi-module change, user-facing polish, external publish
4. `medium`
   terminal, browser, slides, images, docs, video
5. `freshness`
   whether direct graph read, live browsing, or current repo state matters
6. `host`
   Codex runtime, Codex plugin, shared Chef skill, Claude skill
7. `explicit cues`
   user-named skills, plugins, tools, output formats, or platforms

Use the matrix in `references/selection-matrix.md` when the answer is not obvious.

## Routing Rules

### 1. Prefer one strong specialist

Pick narrowest skill that squarely matches task.

Good:

- frontend request -> `frontend-design`
- presentation request -> `talkcraft`
- skill creation request -> `skill-creator`

Bad:

- frontend request -> `frontend-design`, `design-sprint`, `ux-heuristics`, `refactoring-ui`

### 2. Explicit request wins

If user names skill, plugin, or tool surface, start there unless it clearly conflicts with task.

Examples:

- asks for GitHub PR triage -> `github:github`
- asks for Notion capture -> `notion:notion-knowledge-capture`
- asks for PowerPoint deck -> `slides`
- asks for OpenAI API guidance -> `openai-docs`

### 3. Prefer host-native specialists before generic overlap

When current host has a stronger native route, prefer it over a broader fallback.

Examples:

- editable `.pptx` build -> `slides`, not only `talkcraft`
- spreadsheet file work -> `spreadsheet` or `Excel`, not `excel-mcp-server`
- GitHub Actions CI fix -> `github:gh-fix-ci`, not generic review flow
- Slack send or draft -> `slack:slack-outgoing-message`, not plain messaging advice

### 4. Add support only when it changes execution

Supporting skills should change how the work happens, not just sound relevant.

Common support patterns:

- code change + isolation need -> `using-git-worktrees`
- code change + review risk -> `code-reviewer`
- code change + security concern -> `secure-code-guardian`
- codebase question + repo context -> `graph-first-retrieval`
- deck build + weak narrative -> `talkcraft`
- editable artifact + final verification need -> medium-specific verification skill

Treat support lanes as:

- `execution support`
  worktree, graph retrieval, implementation workflow
- `verification support`
  code review, security review, browser verification

Do not add two supports from same lane unless user explicitly asks.

### 5. Avoid overlap twins

Never choose two skills that solve same layer of problem unless user explicitly asks for both.

Common overlaps:

- `slides` and `PowerPoint`
- `spreadsheet` and `Excel`
- `playwright` and `playwright-skill`
- `frontend-design` and `build-web-apps:frontend-skill`
- `code-reviewer` and `github:gh-address-comments`

### 6. Respect stage changes

Re-route when the task moves from one stage to another.

Examples:

- idea -> implementation: add `feature-forge` or `using-git-worktrees`
- implementation -> review: add `code-reviewer`
- notes -> deck strategy: switch to `talkcraft`
- static design -> interactive artifact: switch to `web-artifacts-builder`

### 7. Respect host and project reality

- prefer enabled Chef skills listed in `AGENTS.md` or `CLAUDE.md`
- prefer Codex runtime or plugin skills when current host exposes them
- prefer bundled local skills over hypothetical ones
- do not route to unavailable skills

### 8. Keep the set small

Hard cap:

- `1` primary skill
- `0-2` supporting skills

If you want more than three, the routing pass failed.

## Output Format

When routing matters, announce the decision briefly:

`Using $skill-finder: primary = $frontend-design; support = $using-git-worktrees because this is a UI build with implementation work.`

`Using $skill-finder: primary = $slides; support = $talkcraft because user needs an editable deck and stronger story structure.`

`Using $skill-finder: no specialist added because this is a trivial shell task.`

For Claude-host work, use the same pattern without `$` if needed.

## Re-Route Triggers

Run the routing pass again when:

- the user changes the deliverable
- the task moves from planning to implementation
- the work becomes security-sensitive
- the work becomes presentation- or media-heavy
- the repo reveals a better specialist than the first guess

## Always-On Chef Role

Inside Chef, this skill acts as the default skill broker.

- `chef-index` establishes Chef context
- `skill-finder` chooses specialist skills
- specialist skills drive the actual work

Do not skip straight from `chef-index` to execution on substantial tasks.

## Reference Files

- `references/selection-matrix.md`
  Primary routing table from task type to skill choice.
- `references/routing-rules.md`
  Guardrails, anti-patterns, and re-routing rules.
