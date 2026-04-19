# Routing Rules

## Goal

Pick the smallest skill set that changes the outcome.

## Start Here

1. honor explicit skill, plugin, or app requests
2. skip routing for trivial tasks
3. prefer most specific available specialist
4. add support only when execution changes

## Good Routing

- one primary skill
- optional execution support
- optional review or verification support

## Bad Routing

- listing every remotely relevant skill
- adding support skills that do not affect execution
- keeping the first skill choice after the task obviously changed
- picking two skills that solve same layer of work

## Re-Route On

- new output format
- move from planning to implementation
- move from implementation to review
- new security or architecture risk
- user changes audience, medium, or deliverable

## Priority Order

1. explicit user request
2. host-native specialist skill
3. already-enabled shared Chef skill
4. execution support
5. verification support
6. stop at three skills

## Overlap Guard

Do not pick both items from same overlap pair unless user explicitly asks:

- `slides` and `PowerPoint`
- `spreadsheet` and `Excel`
- `playwright` and `playwright-skill`
- `frontend-design` and `build-web-apps:frontend-skill`
- `code-reviewer` and `github:gh-address-comments`

## Fast Path

Skip specialist routing when:

- one shell command solves task
- user asks tiny factual follow-up
- current lane already fits and no new artifact or risk appears

## Communication Rule

When routing is not obvious, say what you selected and why in one short line.

## Chef Rule

In Chef projects:

1. `chef-index` first
2. `skill-finder` second
3. specialist skills after that
