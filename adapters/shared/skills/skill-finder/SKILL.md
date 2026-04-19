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

## Default Behavior

For every non-trivial task:

1. classify the task
2. pick one primary skill
3. add at most two supporting skills
4. explain the choice in one short line
5. re-run the check if scope shifts

If no specialist skill clearly helps, say so and continue without forcing one.

## Classification Pass

Look at five things first:

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

Use the matrix in `references/selection-matrix.md` when the answer is not obvious.

## Routing Rules

### 1. Prefer one strong specialist

Pick the narrowest skill that squarely matches the task.

Good:

- frontend request -> `frontend-design`
- presentation request -> `talkcraft`
- skill creation request -> `skill-creator`

Bad:

- frontend request -> `frontend-design`, `design-sprint`, `ux-heuristics`, `refactoring-ui`

### 2. Add support only when it changes execution

Supporting skills should change how the work happens, not just sound relevant.

Common support patterns:

- code change + isolation need -> `using-git-worktrees`
- code change + review risk -> `code-reviewer`
- code change + security concern -> `secure-code-guardian`
- codebase question + repo context -> `graph-first-retrieval`

### 3. Respect stage changes

Re-route when the task moves from one stage to another.

Examples:

- idea -> implementation: add `feature-forge` or `using-git-worktrees`
- implementation -> review: add `code-reviewer`
- notes -> deck strategy: switch to `talkcraft`
- static design -> interactive artifact: switch to `web-artifacts-builder`

### 4. Respect host and project reality

- prefer enabled Chef skills listed in `AGENTS.md` or `CLAUDE.md`
- prefer bundled local skills over hypothetical ones
- do not route to unavailable skills

### 5. Keep the set small

Hard cap:

- `1` primary skill
- `0-2` supporting skills

If you want more than three, the routing pass failed.

## Output Format

When routing matters, announce the decision briefly:

`Using $skill-finder: primary = $frontend-design; support = $using-git-worktrees because this is a UI build with implementation work.`

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
