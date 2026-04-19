# Agent Compatibility

## Goal

Keep the skill useful across Codex, Claude, and simpler agents with different tool access.

## Default Strategy

Produce the thinking artifacts first:

- audience
- promise
- slogan
- structure
- timing
- opening
- close
- Q&A

This works everywhere.

## If Slide Tooling Exists

After the strategy passes audit:

- generate a slide-by-slide plan
- write concise slide copy
- add speaker notes
- keep one idea per slide
- keep one fence thread visible across slides

Use the host's slide or document tool only after the outline stabilizes.

## If No Slide Tooling Exists

Return:

- markdown outline
- slide table with title, intent, evidence
- speaker notes
- rehearsal memo
- one-line cut plan

Do not block on deck tooling.

## If The User Gives Raw Notes

1. infer audience and objective
2. derive promise and slogan
3. cluster notes into fences
4. run `scripts/audit_outline.py`
5. rewrite weakest fence first
6. hand off with `assets/slide-plan-template.md` if slides requested

## If The User Gives A Finished Deck

Review for:

- opening clarity
- section logic
- evidence density
- transition clarity
- close strength
- Q&A readiness

Prefer critique tied to sections and specific slides, not generic design advice.
