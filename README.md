# Claude Code Prompt Architecture

Analysis of Claude Code's five prompt augmentation mechanisms through network traffic instrumentation.

## Architecture Overview

Claude Code operates on three layers:

```
API Request Structure:
├── system[]           ← Output Styles
├── messages[]         ← CLAUDE.md, Slash Commands & Skills
└── tools[]            ← Sub-Agents
```

## The Five Mechanisms

### 1. CLAUDE.md: Project-Level Context Injection

CLAUDE.md is automatically injected into every user message as a `<system-reminder>` if the file exists in your project root. This is completely transparent and persists for all requests.

**Network trace:**
```json
{
  "messages": [{
    "role": "user",
    "content": [{
      "type": "text",
      "text": "<system-reminder>\n# claudeMd\nContents of /path/to/CLAUDE.md (project instructions):\n\n[your CLAUDE.md content]\n</system-reminder>"
    }]
  }]
}
```

**Use for:** Project standards, architecture decisions, domain knowledge (committed to git)

---

### 2. Output Styles: System Prompt Mutation

When you run `/output-style software-architect`, Claude Code appends a text block to the `system` array in the API request. This persists for the entire session.

**Network trace:**
```json
{
  "system": [
    {"type": "text", "text": "You are Claude Code..."},
    {"type": "text", "text": "# Output Style: software-architect\n[instructions...]"}
  ],
  "messages": [...]
}
```

**Use for:** Session-wide behavior changes (response format, technical depth, verbosity)

---

### 3. Slash Commands: Deterministic Prompt Injection

Slash commands read `.claude/commands/*.md`, replace `{arg1}` placeholders, and inject into the current user message.

**Network trace:**
```json
{
  "messages": [{
    "role": "user",
    "content": [{
      "type": "text",
      "text": "<command-message>review is running…</command-message>\n[file contents]\nARGUMENTS: @file.js"
    }]
  }]
}
```

**Use for:** Repeatable workflows with explicit triggers

---

### 4. Skills: Model-Invoked Capability Extension

Claude autonomously decides when to invoke a skill by matching requests against SKILL.md frontmatter descriptions.

**Network trace:**
```json
// Assistant decides to use skill
{
  "role": "assistant",
  "content": [{
    "type": "tool_use",
    "name": "Skill",
    "input": {"command": "slack-gif-creator"}
  }]
}

// Skill content returned
{
  "role": "user",
  "content": [{
    "type": "tool_result",
    "content": "[SKILL.md injected]"
  }]
}
```

**Security note:** Skills execute code directly. Use MCP for production.

**Use for:** Domain-specific expertise that should activate automatically

---

### 5. Sub-Agents: Conversation Delegation

Sub-agents spawn entirely separate conversations with their own system prompts.

**Network trace:**
```json
// Main conversation delegates
{"role": "assistant", "content": [{
  "type": "tool_use",
  "name": "Task",
  "input": {
    "subagent_type": "Explore",
    "prompt": "Analyze auth flows..."
  }
}]}

// Sub-agent runs in isolated conversation
{
  "system": "[Explore agent system prompt]",
  "messages": [{"role": "user", "content": "Analyze auth flows..."}]
}

// Results returned
{"role": "user", "content": [{
  "type": "tool_result",
  "content": "[findings]"
}]}
```

**Use for:** Multi-step autonomous tasks (codebase analysis, security audits)

---

## Comparison Matrix

| Mechanism | Injection Point | Activation | Scope |
|-----------|----------------|------------|-------|
| **CLAUDE.md** | User messages (`<system-reminder>`) | Automatic | Project-wide |
| **Output Styles** | System prompt | Manual | Session-wide |
| **Slash Commands** | User messages (`<command-message>`) | User-explicit | Single turn |
| **Skills** | User messages (via `tool_result`) | Model-decided | Single turn |
| **Sub-Agents** | Separate conversation | Model-decided | Isolated |

### Quick Decision Guide

**CLAUDE.md vs Output Styles:**
- Team-wide standards → CLAUDE.md (committed to repo)
- Personal preferences → Output styles (session-only)

**Skills vs Slash Commands vs MCP:**
- Need automation → Skills or MCP
- Need control → Slash commands
- Need security → MCP only

**MCP Resources:** Check out [AgiFlow's AI Code Toolkit](https://github.com/AgiFlow/aicode-toolkit) for production-ready MCP servers and tooling.

---

## Data Source

Analysis derived from network logs in `data/`:

- `claude-md.log` - CLAUDE.md automatic injection mechanism
- `output-style.log` - System prompt override mechanism
- `skills.log` - Skill tool invocation patterns
- `slash-command.log` - File content injection
- `sub-agents.log` - Task tool delegation

Full technical writeup: [blog.md](https://agiflow.io/blog/claude-code-internals-reverse-engineering-prompt-augmentation) - Deep dive into all five mechanisms with network traces, security analysis, and practical recommendations.
