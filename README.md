# Claude Code Prompt Architecture

Analysis of Claude Code's four prompt augmentation mechanisms through network traffic instrumentation.

## Architecture Overview

Claude Code operates on three layers:

```
API Request Structure:
├── system[]           ← Output Styles
├── messages[]         ← Slash Commands & Skills
└── tools[]            ← Sub-Agents
```

## The Four Mechanisms

### 1. Output Styles: System Prompt Mutation

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

### 2. Slash Commands: Deterministic Prompt Injection

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

### 3. Skills: Model-Invoked Capability Extension

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

### 4. Sub-Agents: Conversation Delegation

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

### Skills vs Slash Commands vs MCP

| Dimension | Skills | Slash Commands | MCP |
|-----------|--------|----------------|-----|
| **Invocation** | Model-decided | User-explicit | Model-decided |
| **I/O** | Unstructured | Unstructured | Structured (JSON) |
| **Security** | Direct exec (sandbox required) | Prompt only | Access-controlled |
| **Use Case** | Domain expertise | Workflows | External integrations |

### Output Styles vs Sub-Agents

| Dimension | Output Styles | Sub-Agents |
|-----------|---------------|------------|
| **Scope** | Session-wide | Single task |
| **Mechanism** | System prompt mutation | Conversation delegation |
| **Persistence** | Until changed | One-shot |

---

## Data Source

Analysis derived from network logs in `data/`:

- `output-style.log` - System prompt override mechanism
- `skills.log` - Skill tool invocation patterns
- `slash-command.log` - File content injection
- `sub-agent.log` - Task tool delegation

Full technical writeup: [blog-effective-claude-code.md](blog-effective-claude-code.md)
