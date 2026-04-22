**Task:** Design and plan a modular agent-enhancement package named **"CHEF"** for **Claude** and **Codex**. **Current Phase:** Planning and Architectural Design only. No implementation yet.

**Mandatory Rules (Do Not Modify)**

**1. Ensure the Persian text is readable:**

- When you reply in Persian, write the Persian text normally.
- Put each English section, number, code snippet, version name, or any left-to-right phrase on a separate line.
- Then continue the Persian text again on the next line.
- For English text, use normal left-to-right writing.

**2. Tarzan Persona:**

- Style: 3-6 word sentences. No articles (the), no linking verbs (is, am, are), no filler, no "then". No preamble or pleasantries. No narration; just act.
- Example: "Me fix code" (not "I will fix the code").

**Workflow:**

- Interpret: Explain logic of request. Ask user if interpretation correct.
- Permission: If needed, explain action before proceeding.
- Act: Execute task directly in Tarzan speak.
- Conclude: Summary of actions and critical info at end.

  

**Project Scope & Features**

**1. Architecture:**

- Modular package for various projects.
- Optimized for both Claude and Codex full potential.
- Use CLAUDE.md/AGENTS.md as a central index.
- Find optimal folder/file structure for multi-agent environments to maximize potential.

**2. Integrations:**

- **Obsidian & Graphify:** Connect agents to Obsidian via safishamsi/graphify. Adapt for Codex if needed.
- Run /graphify ~/.claude or agent-specific equivalent. Auto-detect agent and execute matching command.

**3. Context Protocol (Mandatory):**

- **Graph-First Retrieval:** Always query the knowledge graph before reading any project files.
- **Manual Override Only:** Do not access or read raw source files unless explicitly requested by the user.
- **Primary Documentation Source:** Use graphify-out/wiki/index.md as the authoritative index for all codebase knowledge.

**4. Advisory Strategy:** - Implement model routing. Low-token model for bulk work. High-token "Expert" (Opus/GPT-4o) for complex tasks.

**5. Custom Skills:**

- Patrick Winston Presentation Framework.
- Skill-finder: Autonomous agent to find/engage best skills for any task.

**6. Plugin Analysis:**

- Analyze provided repository lists (Security, Review, UX, etc.).
- Identify conflicts/redundancies. Suggest optimal setup.
- Convert "Claude-only" skills to MCP for Codex compatibility.

**7. Deployment:**

- Precise pre-requisites for GitHub.
- Easy install and verification methods.

  

Skill list:

Claude and Codex:  
[https://jeffallan.github.io/claude-skills/skills/security/secure-code-guardian/](https://jeffallan.github.io/claude-skills/skills/security/secure-code-guardian/)

[https://jeffallan.github.io/claude-skills/skills/workflow/feature-forge/](https://jeffallan.github.io/claude-skills/skills/workflow/feature-forge/)

[https://jeffallan.github.io/claude-skills/skills/quality/code-reviewer/](https://jeffallan.github.io/claude-skills/skills/quality/code-reviewer/)

[https://github.com/testdino-hq/playwright-skill](https://github.com/testdino-hq/playwright-skill)

[https://jeffallan.github.io/claude-skills/skills/data-ml/rag-architect/](https://jeffallan.github.io/claude-skills/skills/data-ml/rag-architect/)  
[https://jeffallan.github.io/claude-skills/skills/workflow/the-fool/](https://jeffallan.github.io/claude-skills/skills/workflow/the-fool/)

[https://jeffallan.github.io/claude-skills/skills/workflow/spec-miner/](https://jeffallan.github.io/claude-skills/skills/workflow/spec-miner/)

[https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees)

[https://skills.sh/wondelai/skills/design-sprint](https://skills.sh/wondelai/skills/design-sprint)  
[https://skills.sh/nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max](https://skills.sh/nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max)  
[https://skills.sh/wondelai/skills/ios-hig-design](https://skills.sh/wondelai/skills/ios-hig-design)  
[https://github.com/anthropics/skills/blob/main/skills/frontend-design/](https://github.com/anthropics/skills/blob/main/skills/frontend-design/)

[https://skills.sh/wondelai/skills/hooked-ux](https://skills.sh/wondelai/skills/hooked-ux)

[https://skills.sh/wondelai/skills/ux-heuristics](https://skills.sh/wondelai/skills/ux-heuristics)

[https://skills.sh/wondelai/skills/refactoring-ui](https://skills.sh/wondelai/skills/refactoring-ui)

[https://github.com/tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph)

[https://github.com/obra/superpowers](https://github.com/obra/superpowers)

[https://github.com/garrytan/gstack](https://github.com/garrytan/gstack)

[https://github.com/openclaw/skills/blob/main/skills/am-will/remotion-best-practices/](https://github.com/openclaw/skills/blob/main/skills/am-will/remotion-best-practices/)

[https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/](https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/)

[https://github.com/anthropics/skills/blob/main/skills/canvas-design/](https://github.com/anthropics/skills/blob/main/skills/canvas-design/)

[https://github.com/anthropics/skills/blob/main/skills/theme-factory/](https://github.com/anthropics/skills/blob/main/skills/theme-factory/)

[https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/](https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/)

[https://github.com/massgen/MassGen](https://github.com/massgen/MassGen)

[https://github.com/remotion-dev/remotion](https://github.com/remotion-dev/remotion)

[https://github.com/AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)

[https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/)

[https://github.com/coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)

[https://github.com/haris-musa/excel-mcp-server](https://github.com/haris-musa/excel-mcp-server)

[https://github.com/kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

[https://github.com/ruvnet/ruflo](https://github.com/ruvnet/ruflo)

[https://github.com/expo/skills/blob/main/plugins/expo/skills/building-native-ui/](https://github.com/expo/skills/blob/main/plugins/expo/skills/building-native-ui/)

  

Claude-only:

[https://github.com/anthropics/claude-code/tree/main/plugins/security-guidance](https://github.com/anthropics/claude-code/tree/main/plugins/security-guidance)

[https://github.com/anthropics/claude-code/tree/main/plugins/code-review](https://github.com/anthropics/claude-code/tree/main/plugins/code-review)

[https://github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)

[https://github.com/agamm/claude-code-owasp/blob/main/.claude/skills/owasp-security](https://github.com/agamm/claude-code-owasp/blob/main/.claude/skills/owasp-security)

[https://github.com/PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill)

[https://github.com/anthropics/skills/blob/main/skills/skill-creator/](https://github.com/anthropics/skills/blob/main/skills/skill-creator/)

  

Codex-only:

[https://github.com/PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp)