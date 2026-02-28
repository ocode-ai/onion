# Onion Framework

**Turn Claude Code into a full development workflow engine.**

Onion adds 88 commands, 45 specialized agents, and 8 skills to [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — giving you a structured path from idea to shipped feature.

## Why Onion?

Claude Code is powerful, but open-ended. Every session starts from scratch — you describe what you want, Claude figures out how to do it. That works for simple tasks, but breaks down when you're managing a real product:

- Requirements live in your head (or scattered across Slack, docs, and meetings)
- There's no repeatable process for going from idea to PR
- Context gets lost between sessions
- Task managers, git workflows, and documentation are disconnected from your AI workflow

Onion fixes this by giving Claude Code **structured commands for every phase of development**. Instead of explaining your workflow each time, you run `/onion:product:collect` to capture an idea, `/onion:engineer:start` to begin building, and `/onion:engineer:pr` to ship it. Each command knows what to do, what context it needs, and what comes next.

## See It In Action

```
You:  /onion:product:collect
      "Users should be able to export reports as PDF"

Claude: Captured. Created feature brief with acceptance criteria,
        edge cases, and technical considerations.

You:  /onion:product:task

Claude: Created task TSK-142 in ClickUp with 3 subtasks:
        1. Add PDF generation endpoint
        2. Create export button in reports UI
        3. Add e2e tests for export flow

You:  /onion:engineer:start TSK-142

Claude: Session started. Analyzed task, read codebase, created
        feature/TSK-142-pdf-export branch. Ready to build.

        Plan:
        1. Install pdf-lib dependency
        2. Create /api/reports/:id/export endpoint
        3. Add ExportButton component to ReportHeader
        4. Write tests

You:  /onion:engineer:work

Claude: Continuing session. Picking up from step 2...
        [builds the feature]

You:  /onion:engineer:pre-pr

Claude: Pre-PR check:
        ✓ Code follows project patterns
        ✓ Tests passing (12 new, 340 total)
        ✓ No lint errors
        ✓ Branch is up to date with develop

You:  /onion:engineer:pr

Claude: Created PR #87 "feat: PDF export for reports"
        → https://github.com/your-org/app/pull/87
```

Six commands. Idea to PR.

## Quick Start

### 1. Install

```
/plugin install onion
```

Or for development/testing:

```bash
claude --plugin-dir /path/to/onion
```

### 2. Initialize Your Project (optional)

```
/onion:init
```

This interactively creates a `.onion/` directory with task manager settings (ClickUp, Linear, Asana, or offline mode), language preferences, git workflow, and integration toggles. Commit `config.yaml` for team sharing; keep `.env` local.

### 3. Start Using It

Open Claude Code in your project and run any `/onion:*` command.

## What's Included

### Commands (88)

Organized by development phase:

| Phase | Key Commands | What It Does |
|-------|-------------|--------------|
| **Requirements** | `collect` → `refine` → `spec` | Capture ideas, clarify requirements, write specs |
| **Planning** | `task` → `plan` | Create structured tasks, plan implementation |
| **Development** | `start` → `work` | Begin features with full context, resume sessions |
| **Quality** | `pre-pr` → `test:unit` | Validate code, run tests |
| **Delivery** | `pr` → `feature:finish` | Create PRs, merge with GitFlow |
| **Documentation** | `build-tech-docs` → `build-business-docs` | Generate docs from your codebase |

All commands are prefixed with `/onion:` (e.g., `/onion:product:collect`, `/onion:engineer:start`) so they never conflict with your own.

<details>
<summary>Full command reference</summary>

#### Entry Points

| Command | Description |
|---------|-------------|
| `/onion:onion` | Intelligent entry point — ask anything about the framework |
| `/onion:warm-up` | Load project context and prepare for work |

#### Product

| Command | Description |
|---------|-------------|
| `/onion:product:collect` | Collect feature ideas or bug reports |
| `/onion:product:refine` | Refine requirements through clarification questions |
| `/onion:product:spec` | Create product specification from requirements |
| `/onion:product:task` | Create structured tasks with subtasks and action items |
| `/onion:product:feature` | Create feature tasks for planning and backlog |
| `/onion:product:estimate` | Story point estimation |
| `/onion:product:check` | Verify requirements against project meta-specs |
| `/onion:product:validate-task` | Validate existing tasks |
| `/onion:product:light-arch` | Lightweight architecture design for features |
| `/onion:product:branding` | Branding and positioning analysis |
| `/onion:product:analyze-pain-price` | Customer pain and pricing analysis |
| `/onion:product:presentation` | Generate presentations via Gamma.app |
| `/onion:product:extract-meeting` | Extract structured knowledge from meeting transcripts |
| `/onion:product:consolidate-meetings` | Consolidate multiple meetings into strategic insights |

#### Engineering

| Command | Description |
|---------|-------------|
| `/onion:engineer:start` | Start feature development — creates session, analyzes tasks |
| `/onion:engineer:plan` | Plan feature implementation with structured approach |
| `/onion:engineer:work` | Continue work on active feature with session context |
| `/onion:engineer:pre-pr` | Pre-PR validation — checks patterns and quality |
| `/onion:engineer:pr` | Create Pull Request with GitFlow integration |
| `/onion:engineer:pr-update` | Update existing PR with additional changes |
| `/onion:engineer:hotfix` | Emergency workflow: task + hotfix branch + development |
| `/onion:engineer:docs` | Invoke documentation agent for current branch |
| `/onion:engineer:bump` | Semantic version bump (major, minor, patch) |
| `/onion:engineer:warm-up` | Load project context for engineering work |

#### Git

| Command | Description |
|---------|-------------|
| `/onion:git:feature:start` | Start GitFlow feature branch |
| `/onion:git:feature:finish` | Finish feature with merge to develop |
| `/onion:git:feature:publish` | Publish feature branch to remote |
| `/onion:git:hotfix:start` | Start hotfix branch for production fixes |
| `/onion:git:hotfix:finish` | Finish hotfix with merge to main and develop |
| `/onion:git:release:start` | Start release branch with versioning |
| `/onion:git:release:finish` | Finish release with merge, tag, and publish |
| `/onion:git:fast-commit` | Quick commit for typical workflow changes |
| `/onion:git:sync` | Sync with remote using GitFlow conventions |
| `/onion:git:code-review` | Setup and manage automated code review |
| `/onion:git:init` | Initialize repository with GitFlow conventions |

#### Documentation

| Command | Description |
|---------|-------------|
| `/onion:docs:build-tech-docs` | Generate comprehensive technical documentation |
| `/onion:docs:build-business-docs` | Generate business context and strategy docs |
| `/onion:docs:build-compliance-docs` | Generate compliance documentation (ISO 27001, SOC2, etc.) |
| `/onion:docs:reverse-consolidate` | Reverse-engineer project documentation |
| `/onion:docs:validate-docs` | Validate documentation completeness |
| `/onion:docs:docs-health` | Documentation health check |
| `/onion:docs:build-index` | Manage and update documentation indexes |
| `/onion:docs:refine-vision` | Refine product/project vision and strategy |

#### Testing

| Command | Description |
|---------|-------------|
| `/onion:test:unit` | Unit test generation and execution |
| `/onion:test:integration` | Integration test workflows |
| `/onion:test:e2e` | End-to-end test workflows |

#### Validation

| Command | Description |
|---------|-------------|
| `/onion:validate:workflow` | Validate workflow completeness |
| `/onion:validate:test-strategy:create` | Create test strategy |
| `/onion:validate:test-strategy:analyze` | Analyze existing test strategy |
| `/onion:validate:qa-points:estimate` | QA story points estimation |
| `/onion:validate:collab:three-amigos` | Three Amigos collaboration session |
| `/onion:validate:collab:pair-testing` | Pair testing session |

#### Meta

| Command | Description |
|---------|-------------|
| `/onion:meta:create-agent` | Create new AI agents for the framework |
| `/onion:meta:create-command` | Create new commands |
| `/onion:meta:create-knowledge-base` | Create structured knowledge bases via research |
| `/onion:meta:create-abstraction` | Create abstraction layers |
| `/onion:meta:analyze-complex-problem` | Structured analysis of complex problems |
| `/onion:meta:setup-integration` | Configure task manager and API integrations |

</details>

### Agents (45)

Specialized AI agents that Claude Code can delegate to:

| Category | Count | Examples |
|----------|-------|---------|
| **Development** | 17 | React, Node.js, Nx monorepo, Docker, PostgreSQL, Mermaid |
| **Product** | 8 | Product management, storytelling, branding, meeting extraction |
| **Compliance** | 5 | ISO 27001, SOC2, PMBOK, corporate compliance |
| **Meta** | 4 | Agent creator, command creator, gate keeper |
| **Git** | 4 | Code review, documentation, test planning per branch |
| **Testing** | 3 | Test strategy, test engineering, test planning |
| **Review** | 2 | Code reviewer, compliance reviewer |
| **Deployment** | 1 | Docker specialist |
| **Research** | 1 | Multi-source research and analysis |

Use `@onion` in Claude Code to access the master orchestrator — it knows all agents and routes your request to the right specialist.

### Skills (8)

| Skill | Description |
|-------|-------------|
| `onion:init` | Interactive project setup — task manager, language, git workflow |
| `onion-codebase-visualizer` | Interactive collapsible tree visualization of your codebase |
| `onion-db-schema-visualizer` | ERD generation from Prisma, TypeORM, or raw SQL |
| `onion-collect` | Structured feature idea and bug collection |
| `onion-create-rule` | Claude Code rule creation with best practices |
| `onion-sync-meetings` | Meeting transcript synchronization |

## Common Workflows

### Feature Development

The most common workflow — idea to PR in 5 commands:

```
/onion:product:task          # Create the task
/onion:engineer:start        # Start development session
/onion:engineer:work         # Continue working (resume context)
/onion:engineer:pre-pr       # Validate before PR
/onion:engineer:pr           # Create the Pull Request
```

### Hotfix

Urgent production fix with a single entry point:

```
/onion:engineer:hotfix       # Creates task + hotfix branch + starts dev
/onion:engineer:work         # Fix the issue
/onion:engineer:pr           # Create PR
/onion:git:hotfix:finish     # Merge to main and develop
```

### New Project Setup

Full project bootstrap from scratch:

```
/onion:init                   # Configure project
/onion:warm-up                # Load project context
/onion:product:collect        # Collect initial requirements
/onion:product:refine         # Refine through questions
/onion:product:spec           # Write specifications
/onion:product:light-arch     # Design architecture
/onion:product:task           # Create tasks
/onion:engineer:start         # Begin development
```

### Documentation Generation

```
/onion:docs:build-tech-docs       # Technical documentation
/onion:docs:build-business-docs   # Business documentation
/onion:docs:build-compliance-docs # Compliance docs (ISO 27001, SOC2)
```

## Task Manager Integration

Connect Onion to your existing task management tool:

| Provider | Connection | How It Works |
|----------|------------|-------------|
| **ClickUp** | MCP integration | Tasks sync bidirectionally via MCP server |
| **Linear** | API | Full task lifecycle via GraphQL API |
| **Asana** | MCP integration | Task management via MCP server |
| **None** | Offline mode | Local-only task tracking, no external service |

Configure with `/onion:init` or `/onion:meta:setup-integration`.

## Project Configuration

After installing the plugin, optionally configure each project:

```
/onion:init
```

This creates:

```
your-project/
└── .onion/
    ├── config.yaml       ← Team settings (commit this)
    ├── .env              ← API keys and secrets (gitignored)
    └── .env.example      ← Template for team onboarding (commit this)
```

### Team Onboarding

New team members clone the repo and run:

```bash
cp .onion/.env.example .onion/.env
# Fill in API keys
```

Then use `/onion:meta:setup-integration` for guided configuration.

## How It Works

Onion is a [Claude Code Plugin](https://docs.anthropic.com/en/docs/claude-code/plugins). When installed, Claude Code automatically discovers all commands, agents, and skills from the plugin directory.

```
onion/                        ← Plugin root
├── .claude-plugin/
│   └── plugin.json           ← Plugin manifest
├── commands/                 ← 88 commands (accessible as /onion:*)
├── agents/                   ← 45 specialized agents
├── skills/                   ← 8 skills
└── reference/                ← Documentation, utilities, rules
```

**Namespaced**: Commands use `onion:`, agents use `onion/`. No conflicts with your existing setup.

**Zero pollution**: Nothing is copied to your `~/.claude/` directory. The plugin lives in its own cache at `~/.claude/plugins/cache/onion/`.

## Contributing

```
├── .claude-plugin/plugin.json   # Plugin manifest
├── commands/                    # Command definitions (.md)
├── agents/                      # Agent definitions (.md)
├── skills/                      # Skill definitions (SKILL.md + scripts)
└── reference/                   # Docs, utilities, and rules
    ├── docs/                    # Framework documentation
    ├── utils/                   # Shared utilities (task manager, etc.)
    └── rules/                   # Quality rules
```

To develop locally:

```bash
claude --plugin-dir /path/to/onion
```

## Requirements

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — this is a Claude Code plugin

## License

MIT
