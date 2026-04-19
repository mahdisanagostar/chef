# Skill Audit

Chef uses this audit to keep the skill catalog useful, non-redundant, and host-aware.

## What Changed

- default `core` pack now stays focused on broadly useful implementation and review skills
- heavy orchestration frameworks moved into a separate `orchestration` pack
- HTML-backed skill pages now import cleaner text instead of large script and CSS blobs
- selected shared skills now inject Codex-specific adapter notes during install
- Chef install now prunes disabled managed host skills, stale Claude plugin wrappers, and stale Codex MCP entries

## Overlap Groups

### Review and Security

- `code-reviewer`: default general review lane
- `code-review-graph`: graph-backed review support for wide blast radius
- `the-fool`: adversarial challenge pass after a proposal or diff exists
- `secure-code-guardian`: explicit security implementation and validation lane
- `security-guidance`, `owasp-security`, `anthropic-code-review`: Claude-only support surfaces

### UX and Frontend

- `frontend-design`: default implementation lane for web UI work
- `design-sprint`: early ideation and framing
- `hooked-ux`, `ux-heuristics`, `refactoring-ui`, `ui-ux-pro-max`: critique and polish support
- `ios-hig-design`, `building-native-ui`: platform-specific product design lanes

### Research and Knowledge

- `graphify`: graph-first repo and vault retrieval
- `rag-architect`: retrieval system design
- `obsidian-skills`: vault and note workflows
- `notebooklm-skill`: Claude local NotebookLM skill
- `notebooklm-mcp`: Codex MCP-backed NotebookLM access

### Media and Artifact Creation

- `talkcraft`: presentation structure and rehearsal
- `remotion`: video engine
- `remotion-best-practices`: Remotion implementation guidance
- `canvas-design`, `theme-factory`, `web-artifacts-builder`, `algorithmic-art`: different visual output lanes

### Orchestration Frameworks

- `gstack`
- `massgen`
- `ruflo`
- `superpowers`

Chef should not auto-stack these. Use one only when the user explicitly wants that framework.

## Shared Skills Audit

| Skill | Role | Main overlap | Codex status | Chef decision |
| --- | --- | --- | --- | --- |
| `secure-code-guardian` | security implementation | `security-guidance`, `owasp-security` | adapted | keep shared; add Codex notes |
| `feature-forge` | feature planning to execution | `spec-miner` | adapted | keep shared; add Codex notes |
| `code-reviewer` | default code review | `code-review-graph`, `the-fool` | adapted | keep shared; findings-first in Codex |
| `playwright-skill` | browser verification | built-in `playwright` skill | works as-is | keep shared; use as Chef verification lane |
| `rag-architect` | retrieval architecture | `graphify`, NotebookLM tools | adapted | keep shared; Codex uses primary-source evidence |
| `the-fool` | adversarial challenge pass | `code-reviewer` | adapted | keep shared; not default first pass |
| `spec-miner` | extract requirements from existing material | `feature-forge` | adapted | keep shared; convert results into tasks |
| `using-git-worktrees` | isolated implementation support | `superpowers` | bundled and optimized | keep shared; preferred default |
| `design-sprint` | product framing | `hooked-ux`, `ui-ux-pro-max` | works as-is | keep shared; ideation only |
| `ui-ux-pro-max` | visual and UX critique | `hooked-ux`, `ux-heuristics`, `refactoring-ui` | works as-is | keep shared; support lane only |
| `ios-hig-design` | Apple design guidance | `building-native-ui` | works as-is | keep shared |
| `frontend-design` | web UI implementation | `ui-ux-pro-max`, `web-artifacts-builder` | works as-is | keep shared; default UI build lane |
| `hooked-ux` | behavioral UX lens | `ux-heuristics` | works as-is | keep shared; support lane only |
| `ux-heuristics` | heuristic UX audit | `hooked-ux`, `refactoring-ui` | works as-is | keep shared; support lane only |
| `refactoring-ui` | visual polish heuristics | `frontend-design`, `ui-ux-pro-max` | works as-is | keep shared; support lane only |
| `code-review-graph` | graph-backed review | `code-reviewer` | adapted | keep shared; use only when structure matters |
| `superpowers` | broad methodology framework | `using-git-worktrees`, `gstack`, `ruflo`, `massgen` | adapted | move to `orchestration` pack |
| `gstack` | workflow and browser-heavy orchestration | `ruflo`, `massgen`, `superpowers` | adapted | move to `orchestration` pack |
| `remotion-best-practices` | Remotion implementation guidance | `remotion` | bundled and optimized | keep shared |
| `algorithmic-art` | generative visuals | `canvas-design` | works as-is | keep shared |
| `canvas-design` | static visual design | `theme-factory`, `web-artifacts-builder` | works as-is | keep shared |
| `theme-factory` | reusable artifact theming | `canvas-design` | works as-is | keep shared |
| `web-artifacts-builder` | complex web artifact generation | `frontend-design` | works as-is | keep shared |
| `massgen` | multi-agent orchestration and debate | `gstack`, `ruflo`, `superpowers` | works as-is | move to `orchestration` pack |
| `remotion` | video creation engine | `remotion-best-practices` | works as-is | keep shared |
| `claude-seo` | SEO audits and strategy | `marketingskills` | adapted | keep shared; Codex ignores Claude-only install steps |
| `brand-guidelines` | brand system enforcement | `theme-factory` | works as-is | keep shared |
| `marketingskills` | broad marketing workflow | `claude-seo` | works as-is | keep shared |
| `excel-mcp-server` | MCP spreadsheet automation | built-in `Excel` and `spreadsheet` skills | adapted | keep shared; not default for simple local edits |
| `obsidian-skills` | note and vault workflows | `graphify` | adapted | keep shared; file-based in Codex |
| `ruflo` | swarm orchestration and MCP framework | `gstack`, `massgen`, `superpowers` | adapted | move to `orchestration` pack |
| `building-native-ui` | Expo and React Native UI | `ios-hig-design` | works as-is | keep Codex-focused |

## Claude-Only Audit

| Skill | Role | Codex status | Chef decision |
| --- | --- | --- | --- |
| `security-guidance` | Anthropic security plugin | Claude-only by design | keep Claude-only |
| `anthropic-code-review` | Anthropic review plugin | Claude-only by design | keep Claude-only |
| `claude-mem` | Claude memory plugin | Claude-only by design | keep Claude-only |
| `owasp-security` | OWASP-focused Claude skill | Claude-only by design | keep Claude-only |
| `notebooklm-skill` | local NotebookLM skill | not needed in Codex because MCP variant exists | keep Claude-only |
| `skill-creator` | Anthropic skill authoring workflow | Codex already has a native system skill-creator | keep Claude-only in catalog |

## Codex-Only Audit

| Skill | Role | Codex status | Chef decision |
| --- | --- | --- | --- |
| `notebooklm-mcp` | NotebookLM MCP server | native fit for Codex MCP runtime | keep Codex-only |

## Pack Strategy

- `core`: small default set for implementation, review, retrieval, and isolation
- `review`: optional deeper review and adversarial analysis
- `security`: optional security-focused overlays
- `research`: optional knowledge and retrieval tools
- `ux`: optional design and critique tools
- `media`: optional artifact and media generation tools
- `business`: optional SEO, spreadsheet, and marketing tools
- `orchestration`: optional heavyweight multi-agent frameworks
