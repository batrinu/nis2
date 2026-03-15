---
name: mcp-builder
description: >
  Guide for building MCP (Model Context Protocol) servers that let AI agents interact with
  external services. Use when the user asks to "build an MCP server", "create a tool integration",
  "connect to an API", "make a plugin", or mentions MCP, Model Context Protocol, or wants to
  enable an AI agent to use external tools. Covers TypeScript and Python implementations,
  tool design, testing, and best practices. Kimi Code CLI natively supports MCP servers.
---

# MCP Server Development Guide

Build MCP servers that enable AI agents (Kimi, Claude, Codex, etc.) to interact with external services through well-designed tools.

## Overview

An MCP server exposes **tools** that AI agents can discover and call. A good MCP server:
- Has clear, descriptive tool names (e.g., `github_create_issue`, not `do_thing`)
- Returns focused, relevant data (not entire API responses dumped raw)
- Provides actionable error messages that guide the agent toward solutions
- Supports pagination for list operations
- Uses proper input validation

## Phase 1: Plan

### Understand the API
1. Review the target service's API documentation
2. Identify the most common operations users would want
3. Map out authentication requirements
4. Note rate limits and data constraints

### Design Your Tools
Prioritize comprehensive API coverage over clever workflow shortcuts. List the endpoints to implement, starting with the most common operations.

**Tool naming convention:** `service_action_target`
- `github_create_issue`
- `github_list_repos`
- `slack_send_message`
- `notion_search_pages`

### Choose Your Stack

| Choice | When to Use |
|---|---|
| **TypeScript** (recommended) | Best SDK support, works well with most MCP clients |
| **Python** (FastMCP) | Quick prototyping, familiar for data/ML teams |

| Transport | When to Use |
|---|---|
| **Streamable HTTP** | Remote servers, production deployments |
| **stdio** | Local servers, development, CLI tools |

## Phase 2: Implement

### Project Structure (TypeScript)

```
my-mcp-server/
├── src/
│   ├── index.ts          # Server setup and tool registration
│   ├── tools/            # One file per tool group
│   │   ├── issues.ts
│   │   └── repos.ts
│   ├── client.ts         # API client with auth
│   └── utils.ts          # Shared helpers
├── package.json
├── tsconfig.json
└── README.md
```

### Project Structure (Python)

```
my-mcp-server/
├── server.py             # Server setup and tool registration
├── tools/                # Tool implementations
│   ├── issues.py
│   └── repos.py
├── client.py             # API client with auth
├── utils.py              # Shared helpers
├── pyproject.toml
└── README.md
```

### Tool Implementation Checklist

For every tool, define:

1. **Input Schema** — Use Zod (TypeScript) or Pydantic (Python) with:
   - Clear field descriptions
   - Constraints (min/max, patterns, enums)
   - Required vs optional fields
   - Default values where sensible

2. **Output** — Return structured data:
   - JSON for programmatic consumption
   - Include both `text` content and `structuredContent` when possible
   - Paginated results for lists (include `nextCursor` or `hasMore`)

3. **Tool Description** — Concise summary that helps agents choose the right tool:
   - What it does (one sentence)
   - Key parameters
   - What it returns

4. **Annotations** — Declare behavior:
   - `readOnlyHint`: Does it only read data?
   - `destructiveHint`: Could it delete or overwrite?
   - `idempotentHint`: Safe to retry?

5. **Error Handling** — Return actionable messages:
   ```
   BAD:  "Error: 403"
   GOOD: "Permission denied. The token needs 'repo' scope. Generate a new token at github.com/settings/tokens"
   ```

### Authentication Patterns

```typescript
// Environment variable (most common)
const apiKey = process.env.SERVICE_API_KEY;
if (!apiKey) {
  throw new Error("SERVICE_API_KEY environment variable required. Get one at: https://...");
}

// OAuth (for user-facing services)
// Use the MCP auth flow - see SDK docs
```

## Phase 3: Test

### Manual Testing
1. **Build**: `npm run build` (TypeScript) or `python -m py_compile server.py`
2. **Inspector**: `npx @modelcontextprotocol/inspector` to test tools interactively
3. **Integration**: Test with your target agent (Kimi, Claude Code, etc.)

### Quality Checklist
- [ ] All tools have clear, descriptive names
- [ ] Input schemas have descriptions and constraints
- [ ] Error messages are actionable (tell agent what to do next)
- [ ] List operations support pagination
- [ ] No hardcoded credentials (use env vars)
- [ ] Consistent response format across tools
- [ ] README explains setup, auth, and available tools

### Testing with Kimi Code CLI

```bash
# Add your MCP server
kimi mcp add --transport stdio my-server node dist/index.js

# Or for HTTP transport
kimi mcp add --transport http my-server http://localhost:3000/mcp

# Or via config file
kimi --mcp-config-file mcp-config.json
```

## Phase 4: Deploy

### For Local Use (stdio)
- Package as npm/pip installable
- Document environment variables needed
- Provide a one-line install command

### For Remote Use (HTTP)
- Deploy to cloud (Vercel, Railway, Fly.io, etc.)
- Set up authentication (API key or OAuth)
- Document the server URL for client configuration

## Common Patterns

### Pagination
```typescript
server.registerTool("list_items", {
  description: "List items with pagination",
  inputSchema: z.object({
    cursor: z.string().optional().describe("Pagination cursor from previous response"),
    limit: z.number().min(1).max(100).default(20),
  }),
  async handler({ cursor, limit }) {
    const result = await api.listItems({ cursor, limit });
    return {
      content: [{ type: "text", text: JSON.stringify(result.items, null, 2) }],
      // Include cursor for next page
      ...(result.nextCursor && { nextCursor: result.nextCursor }),
    };
  },
});
```

### Error Handling
```typescript
try {
  const result = await api.createItem(input);
  return { content: [{ type: "text", text: `Created: ${result.id}` }] };
} catch (error) {
  if (error.status === 404) {
    return { content: [{ type: "text", text: `Item not found. Available items: ${await listNames()}` }], isError: true };
  }
  return { content: [{ type: "text", text: `API error: ${error.message}. Check your API key and permissions.` }], isError: true };
}
```

## Resources

- MCP Specification: https://modelcontextprotocol.io/specification/draft
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Kimi MCP docs: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html
