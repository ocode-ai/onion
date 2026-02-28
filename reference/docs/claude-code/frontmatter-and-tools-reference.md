# Claude Code: Frontmatter & Tools Reference

> Concise reference for configuring agents, skills, commands, and rules in Claude Code.
> Source: [Official Claude Code Docs](https://code.claude.com/docs/)

---

## 1. Subagents (`.claude/agents/*.md`)

Subagents are specialized AI assistants with isolated context, custom prompts, and tool restrictions.

### File Structure

```markdown
---
name: my-agent
description: When Claude should delegate to this agent
---

System prompt content here (markdown body).
```

### Frontmatter Properties

| Field             | Required | Type                    | Default     | Description                                                                                     |
|-------------------|----------|-------------------------|-------------|-------------------------------------------------------------------------------------------------|
| `name`            | **Yes**  | string                  | —           | Unique identifier. Lowercase letters and hyphens only.                                          |
| `description`     | **Yes**  | string                  | —           | When Claude should delegate to this agent. Include "use proactively" for auto-delegation.       |
| `tools`           | No       | comma-separated string  | inherit all | Allowlist of tools. Use `Task(worker, researcher)` to restrict spawnable subagents.             |
| `disallowedTools` | No       | comma-separated string  | —           | Denylist of tools, removed from inherited/specified list.                                       |
| `model`           | No       | string                  | `inherit`   | `sonnet`, `opus`, `haiku`, or `inherit`.                                                        |
| `permissionMode`  | No       | string                  | `default`   | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan`.                            |
| `maxTurns`        | No       | number                  | —           | Maximum agentic turns before stopping.                                                          |
| `skills`          | No       | list of skill names     | —           | Skills injected into agent context at startup (full content, not just descriptions).            |
| `mcpServers`      | No       | list/object             | —           | MCP server names or inline definitions available to this agent.                                 |
| `hooks`           | No       | object                  | —           | Lifecycle hooks scoped to this agent (`PreToolUse`, `PostToolUse`, `Stop`).                     |
| `memory`          | No       | string                  | —           | Persistent memory scope: `user`, `project`, or `local`. Enables cross-session learning.         |
| `background`      | No       | boolean                 | `false`     | Always run as a background task.                                                                |
| `isolation`       | No       | string                  | —           | Set to `worktree` to run in a temporary git worktree (isolated repo copy).                      |

### Storage Locations (by priority)

| Location                     | Scope            | Priority    |
|------------------------------|------------------|-------------|
| `--agents` CLI flag (JSON)   | Current session  | 1 (highest) |
| `.claude/agents/`            | Current project  | 2           |
| `~/.claude/agents/`          | All projects     | 3           |
| Plugin `agents/` directory   | Where enabled    | 4 (lowest)  |

---

## 2. Skills (`.claude/skills/<name>/SKILL.md`)

Skills extend Claude's capabilities. They follow the [Agent Skills](https://agentskills.io) open standard.

### File Structure

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── reference.md       # Optional supporting files
├── examples/
└── scripts/
```

```markdown
---
name: my-skill
description: What this skill does and when to use it
---

Skill instructions here (markdown body).
```

### Frontmatter Properties

| Field                      | Required    | Type                   | Default   | Description                                                                                    |
|----------------------------|-------------|------------------------|-----------|------------------------------------------------------------------------------------------------|
| `name`                     | No          | string                 | dir name  | Display name / slash-command name. Lowercase, numbers, hyphens. Max 64 chars.                  |
| `description`              | Recommended | string                 | 1st para  | What it does and when to use it. Claude uses this for auto-invocation decisions.                |
| `argument-hint`            | No          | string                 | —         | Hint shown during autocomplete. E.g., `[issue-number]`, `[filename] [format]`.                 |
| `disable-model-invocation` | No          | boolean                | `false`   | `true` = only user can invoke via `/name`. Prevents Claude from auto-loading.                  |
| `user-invocable`           | No          | boolean                | `true`    | `false` = hidden from `/` menu. Only Claude can invoke. For background knowledge.              |
| `allowed-tools`            | No          | comma-separated string | —         | Tools Claude can use without permission when this skill is active.                             |
| `model`                    | No          | string                 | —         | Model override when skill is active.                                                           |
| `context`                  | No          | string                 | —         | Set to `fork` to run in an isolated subagent context.                                          |
| `agent`                    | No          | string                 | `general-purpose` | Which subagent type to use when `context: fork`. Built-in or custom agent name.        |
| `hooks`                    | No          | object                 | —         | Hooks scoped to this skill's lifecycle.                                                        |

### Invocation Control Matrix

| Frontmatter                      | User can invoke | Claude can invoke | Context loading                                  |
|----------------------------------|-----------------|-------------------|--------------------------------------------------|
| *(default)*                      | Yes             | Yes               | Description always loaded; full content on invoke |
| `disable-model-invocation: true` | Yes             | No                | Description NOT in context; loads on user invoke  |
| `user-invocable: false`          | No              | Yes               | Description always loaded; full content on invoke |

### String Substitutions

| Variable               | Description                                        |
|------------------------|----------------------------------------------------|
| `$ARGUMENTS`           | All arguments passed when invoking the skill       |
| `$ARGUMENTS[N]`        | Specific argument by 0-based index                 |
| `$N`                   | Shorthand for `$ARGUMENTS[N]` (`$0`, `$1`, etc.)  |
| `${CLAUDE_SESSION_ID}` | Current session ID                                 |
| `` !`command` ``       | Dynamic context injection (runs before skill sent) |

### Storage Locations (by priority)

| Location                                     | Scope         |
|----------------------------------------------|---------------|
| Enterprise managed settings                  | Organization  |
| `~/.claude/skills/<name>/SKILL.md`           | Personal      |
| `.claude/skills/<name>/SKILL.md`             | Project       |
| Plugin `skills/` directory                   | Plugin scope  |

---

## 3. Commands (`.claude/commands/*.md`)

> **Note**: Commands have been merged into Skills. `.claude/commands/` files still work and support the same frontmatter. Skills are recommended for new work.

### File Structure

```markdown
---
description: What this command does
allowed-tools: Read, Grep, Bash
---

Command instructions here.
```

### Frontmatter Properties

Commands support the **same frontmatter as Skills**:

| Field                      | Required    | Description                                                |
|----------------------------|-------------|------------------------------------------------------------|
| `name`                     | No          | Display name (defaults to filename without `.md`)          |
| `description`              | Recommended | Description shown in `/help`                               |
| `argument-hint`            | No          | Hint for expected arguments                                |
| `disable-model-invocation` | No          | Prevent auto-invocation by Claude                          |
| `user-invocable`           | No          | Hide from `/` menu                                         |
| `allowed-tools`            | No          | Tools allowed without permission prompts                   |
| `model`                    | No          | Model override                                             |
| `context`                  | No          | `fork` for isolated execution                              |
| `agent`                    | No          | Subagent type for forked context                           |
| `hooks`                    | No          | Scoped hooks                                               |

### Storage Locations

| Location                        | Scope       |
|---------------------------------|-------------|
| `.claude/commands/`             | Project     |
| `~/.claude/commands/`           | Personal    |

If a skill and command share the same name, the **skill takes precedence**.

---

## 4. Rules (`.claude/rules/*.md`)

Rules provide modular, topic-specific instructions loaded as project memory.

### File Structure

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

### Frontmatter Properties

| Field   | Required | Type              | Default | Description                                                    |
|---------|----------|-------------------|---------|----------------------------------------------------------------|
| `paths` | No       | list of strings   | —       | Glob patterns. Rule only loads when Claude works with matching files. |

Rules **without** a `paths` field are loaded unconditionally.

### Glob Pattern Syntax

| Pattern                | Matches                                |
|------------------------|----------------------------------------|
| `**/*.ts`              | All TypeScript files in any directory  |
| `src/**/*`             | All files under `src/`                 |
| `*.md`                 | Markdown files in project root         |
| `src/components/*.tsx` | React components in specific directory |
| `src/**/*.{ts,tsx}`    | Brace expansion for multiple extensions|
| `{src,lib}/**/*.ts`    | Brace expansion for multiple directories|

**Important YAML note**: Patterns starting with `*` or `{` must be quoted in YAML:
```yaml
paths:
  - "**/*.ts"           # Correct (quoted)
  - "src/**/*.{ts,tsx}" # Correct (quoted)
```

### Storage Locations

| Location              | Scope     | Priority |
|-----------------------|-----------|----------|
| `~/.claude/rules/`   | Personal  | Lower    |
| `.claude/rules/`     | Project   | Higher   |

Rules support subdirectories (discovered recursively) and symlinks.

---

## 5. Available Tools

These are the internal tools that can be referenced in `tools`, `disallowedTools`, and `allowed-tools` fields.

### Core Tools

| Tool              | Category       | Description                                                      |
|-------------------|----------------|------------------------------------------------------------------|
| `Read`            | File ops       | Read files (text, images, PDFs, notebooks)                       |
| `Write`           | File ops       | Create or overwrite files                                        |
| `Edit`            | File ops       | Exact string replacements in files                               |
| `NotebookEdit`    | File ops       | Edit Jupyter notebook cells                                      |
| `Bash`            | Execution      | Execute shell commands with optional timeout and background      |
| `Glob`            | Search         | Fast file pattern matching (e.g., `**/*.ts`)                     |
| `Grep`            | Search         | Regex content search (built on ripgrep)                          |
| `WebFetch`        | Web            | Fetch and process URL content                                    |
| `WebSearch`       | Web            | Search the web for current information                           |
| `Agent`           | Orchestration  | Launch subagents for complex tasks (alias: `Task`)               |
| `Task`            | Orchestration  | Spawn subagents. Use `Task(name)` to restrict to specific agents |
| `TodoWrite`       | Orchestration  | Create and manage structured task lists                          |
| `AskUserQuestion` | Interaction    | Ask the user questions during execution                          |
| `Skill`           | Orchestration  | Invoke a skill within the conversation                           |
| `EnterPlanMode`   | Workflow       | Transition to plan mode for implementation planning              |
| `ExitPlanMode`    | Workflow       | Signal plan completion for user approval                         |
| `EnterWorktree`   | Workflow       | Create isolated git worktree for the session                     |

### MCP Tools

MCP tools follow the naming pattern `mcp__<server>__<tool>`:

| Pattern                              | Description                         |
|--------------------------------------|-------------------------------------|
| `mcp__<server>`                      | All tools from a server             |
| `mcp__<server>__*`                   | Wildcard: all tools from a server   |
| `mcp__<server>__<specific_tool>`     | Specific tool from a server         |

### Permission Rule Syntax for Tools

| Rule                             | Effect                                            |
|----------------------------------|---------------------------------------------------|
| `Bash`                           | Matches all Bash commands                         |
| `Bash(npm run *)`                | Wildcard matching for Bash commands               |
| `Bash(npm run build)`            | Exact command match                               |
| `Read(./.env)`                   | Specific file path                                |
| `Read(src/**)`                   | Gitignore-style glob patterns                     |
| `Edit(/docs/**)`                 | Relative to project root                          |
| `Read(~/.zshrc)`                 | Home directory path                               |
| `Read(//tmp/file)`               | Absolute filesystem path (double slash)           |
| `WebFetch(domain:example.com)`   | Domain-specific web fetch                         |
| `Task(Explore)`                  | Specific subagent                                 |
| `Task(agent1, agent2)`           | Multiple allowed subagents                        |
| `Skill(commit)`                  | Exact skill match                                 |
| `Skill(review-pr *)`             | Prefix match with arguments                       |
| `mcp__server__tool`              | Specific MCP tool                                 |

### Tool Categories for Quick Reference

```
Read-only (no approval needed):  Read, Glob, Grep
File modification (session approval): Edit, Write, NotebookEdit
Execution (per-use approval):    Bash
Web access:                      WebFetch, WebSearch
Orchestration:                   Agent/Task, TodoWrite, Skill
Interaction:                     AskUserQuestion
Workflow:                        EnterPlanMode, ExitPlanMode, EnterWorktree
```

---

## 6. Quick Comparison

| Aspect         | Agents                        | Skills                       | Commands                  | Rules                    |
|----------------|-------------------------------|------------------------------|---------------------------|--------------------------|
| **File**       | `agents/*.md`                 | `skills/<name>/SKILL.md`     | `commands/*.md`           | `rules/*.md`             |
| **Purpose**    | Isolated task delegation      | Extend capabilities          | Reusable prompts          | Persistent instructions  |
| **Context**    | Own context window            | Main or forked context       | Main or forked context    | Always loaded            |
| **Invocation** | Auto by Claude or explicit    | Auto by Claude or `/name`    | `/name` only              | Auto (path-conditional)  |
| **Required FM**| `name`, `description`         | `description` (recommended)  | `description` (recommended)| None                    |
| **Key FM**     | `tools`, `model`, `memory`    | `allowed-tools`, `context`   | `allowed-tools`, `context`| `paths`                  |
| **Supports files** | No (single .md)          | Yes (directory with SKILL.md)| No (single .md)           | No (single .md)          |

---

## Sources

- [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Slash commands](https://code.claude.com/docs/en/slash-commands)
- [Manage Claude's memory](https://code.claude.com/docs/en/memory)
- [Configure permissions](https://code.claude.com/docs/en/permissions)
- [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
