# Kimi Code Skills Pack — Web App Building Superpowers

A curated collection of Agent Skills adapted for **Kimi Code CLI** (and compatible with Claude Code, Codex, etc.) to dramatically improve web app building quality.

## What's Inside

### Core App Building
| Skill | Purpose | Adapted From |
|---|---|---|
| `web-app-builder` | Full-stack app scaffolding, architecture, and building workflow | Original |
| `frontend-design` | Distinctive UI/UX that avoids generic "AI slop" | Claude.ai built-in |
| `canvas-design` | Museum-quality visual art, posters, and design as PNG/PDF | Anthropic `canvas-design` |

### Development Workflow
| Skill | Purpose | Adapted From |
|---|---|---|
| `systematic-dev` | Brainstorm → Plan → Build → Review methodology (flow skill) | Superpowers |
| `project-planning` | Break work into atomic tasks with verification steps | Superpowers |
| `code-quality` | TDD, debugging, and verification practices | Superpowers + Pickle Rick |

### Tooling & Docs
| Skill | Purpose | Adapted From |
|---|---|---|
| `mcp-builder` | Build MCP servers for AI agent tool integrations | Anthropic `mcp-builder` |
| `doc-coauthoring` | Structured co-authoring workflow for specs, PRDs, RFCs | Anthropic `doc-coauthoring` |
| `skill-creator` | Create and improve new Agent Skills | Anthropic `skill-creator` |

## Installation

### Option A: User-level (all projects)

```bash
# Kimi Code CLI recommended path
cp -r ./*/ ~/.config/agents/skills/

# Or use Kimi-specific path
cp -r ./*/ ~/.kimi/skills/

# Or Claude-compatible path (Kimi also checks this!)
cp -r ./*/ ~/.claude/skills/
```

### Option B: Project-level (single project)

```bash
# In your project root
mkdir -p .agents/skills
cp -r ./*/ .agents/skills/
```

### Option C: CLI flag

```bash
kimi --skills-dir /path/to/kimi-skills-pack
```

## Usage

Skills auto-trigger based on context. You can also invoke explicitly:

```
/skill:web-app-builder Build me a task management app with React
/skill:frontend-design Make the UI feel premium and distinctive
/skill:systematic-dev Let's plan this feature properly before coding
/skill:project-planning Break this into atomic implementation tasks
/skill:code-quality Review this code and add tests
```

### Flow Skills

The `systematic-dev` skill includes a flow mode for automated multi-step workflows:

```
/flow:systematic-dev Build a real-time chat application
```

## Compatibility

These skills use the open Agent Skills format (SKILL.md) and work with:
- ✅ Kimi Code CLI (primary target)
- ✅ Claude Code
- ✅ OpenAI Codex
- ✅ Gemini CLI / Antigravity
- ✅ Cursor, Windsurf, OpenCode, and others

## Credits & Inspiration

- [anthropics/skills](https://github.com/anthropics/skills) — Official Anthropic skill repo: `canvas-design`, `mcp-builder`, `doc-coauthoring`, `skill-creator`, `frontend-design`
- [obra/superpowers](https://github.com/obra/superpowers) — Development methodology and workflow patterns
- [galz10/pickle-rick-extension](https://github.com/galz10/pickle-rick-extension) — Iterative agent loop and "God Mode" engineering philosophy
- [Kimi Code CLI docs](https://moonshotai.github.io/kimi-cli/en/customization/skills.html) — Skills system reference
- [Agent Skills spec](https://agentskills.io/) — Open standard for cross-tool skill format

## License

MIT
