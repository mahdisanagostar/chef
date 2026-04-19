# Skill Finder Matrix

Use this file when the best skill is not obvious from the request alone.

## First-Pass Overrides

- user explicitly names a skill -> start with that skill
- user explicitly names a plugin or app -> prefer that plugin surface first
- tiny shell or one-command task -> no specialist skill

## Shared Chef Baseline

- Chef project work -> `chef-index`
- codebase understanding -> `graph-first-retrieval`
- skill selection itself -> `skill-finder`

## Codex Native Artifact Skills

- editable `.pptx` deck -> `slides`
- talk strategy, rehearsal, deck narrative -> `talkcraft`
- spreadsheet file work -> `spreadsheet`
- workbook-heavy spreadsheet modeling -> `Excel`
- `.docx` authoring or editing -> `doc`
- PDF generation or review -> `pdf`
- browser automation from terminal -> `playwright`
- image generation or edit -> `imagegen`
- speech generation -> `speech`
- transcription -> `transcribe`
- Sora video generation or edit -> `sora`
- OpenAI product or API guidance -> `openai-docs`

## Plugin-First Routes

- GitHub repo or PR triage -> `github:github`
- GitHub review-comment response -> `github:gh-address-comments`
- GitHub Actions CI failure -> `github:gh-fix-ci`
- commit, push, and PR publish flow -> `github:yeet`
- Notion knowledge capture -> `notion:notion-knowledge-capture`
- Notion research synthesis -> `notion:notion-research-documentation`
- Notion meeting prep -> `notion:notion-meeting-intelligence`
- Notion spec to build plan -> `notion:notion-spec-to-implementation`
- Slack read or analysis -> `slack:slack`
- Slack reply drafting -> `slack:slack-reply-drafting`
- Slack outbound message or draft -> `slack:slack-outgoing-message`
- Vercel deploy -> `build-web-apps:deploy-to-vercel`
- React or Next performance -> `build-web-apps:react-best-practices`
- shadcn/ui component work -> `build-web-apps:shadcn`
- Stripe implementation -> `build-web-apps:stripe-best-practices`
- Supabase or Postgres optimization -> `build-web-apps:supabase-postgres-best-practices`
- web design audit -> `build-web-apps:web-design-guidelines`
- iOS simulator run or debug -> `build-ios-apps:ios-debugger-agent`
- SwiftUI refactor -> `build-ios-apps:swiftui-view-refactor`
- SwiftUI performance audit -> `build-ios-apps:swiftui-performance-audit`
- App Intents or shortcuts -> `build-ios-apps:ios-app-intents`
- browser game routing -> `game-studio:game-studio`
- Phaser 2D game work -> `game-studio:phaser-2d-game`
- React Three Fiber game work -> `game-studio:react-three-fiber-game`
- plain Three.js game work -> `game-studio:three-webgl-game`

## Build And Refactor

- new feature or implementation plan -> `feature-forge`
- isolated branch or parallel workspace need -> `using-git-worktrees`
- frontend UI build or redesign -> `frontend-design`
- Chef-oriented browser verification flow -> `playwright-skill`
- repository automation or command workflow shaping -> `gstack`

## Review And Safety

- general code review -> `code-reviewer`
- security-sensitive changes -> `secure-code-guardian`
- graph-shaped review exploration -> `code-review-graph`
- adversarial or skeptical challenge pass -> `the-fool`

## Research And Knowledge

- graph-first repo or vault retrieval -> `graphify`
- external knowledge synthesis or retrieval architecture -> `rag-architect`
- notebook-driven research flow -> `notebooklm-mcp`
- Obsidian-oriented knowledge work -> `obsidian-skills`
- formal spec extraction -> `spec-miner`

## Design And Product

- UX improvement or interface critique -> `ux-heuristics`
- UI polish with stronger visual judgment -> `refactoring-ui`
- product framing or structured ideation -> `design-sprint`
- Apple platform design language -> `ios-hig-design`

## Media And Presentation

- presentations, talks, deck structure, rehearsal -> `talkcraft`
- motion or video storytelling -> `remotion-best-practices`
- static visuals or posters -> `canvas-design`
- themed artifacts -> `theme-factory`
- rich web artifact generation -> `web-artifacts-builder`
- generative visuals -> `algorithmic-art`

## Business And Operations

- SEO-oriented content or strategy -> `claude-seo`
- marketing tasks -> `marketingskills`
- spreadsheet-heavy work -> `excel-mcp-server`

## Creation Of New Skills

- new skill or major skill rewrite -> `skill-creator`

## Support Lanes

- execution support -> `using-git-worktrees`, `graph-first-retrieval`, `feature-forge`
- verification support -> `code-reviewer`, `secure-code-guardian`, `playwright`, `playwright-skill`

## Routing Patterns

### Strong defaults

- code implementation -> `feature-forge` + optional `using-git-worktrees`
- UI implementation -> `frontend-design` + optional `playwright-skill`
- editable slide deck -> `slides` + optional `talkcraft`
- presentation work without deck build -> `talkcraft`
- skill creation -> `skill-creator`

### Review defaults

- code review -> `code-reviewer`
- security review -> `secure-code-guardian`
- architecture doubt -> `the-fool`

### Avoid

- stacking multiple generic skills when one specific skill fits
- picking both Codex-native and Chef overlap twins for same layer
- using media skills for plain docs work
- adding review skills before there is anything concrete to review
