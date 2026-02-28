---
name: create-rule
description: Create a path-specific Claude Code rule (.claude/rules/*.md) with guided scope validation, overlap detection, and best-practice guardrails.
---

# Create Rule

Create a new `.claude/rules/*.md` file through a guided workflow that validates scope, prevents bad rules, and ensures the right mechanism is used.

## Step 1: Understand Intent

The user provides a topic or area they want a rule for (e.g., "invitations feature", "API DTOs", "Prisma schema").

Parse the input to identify:

- **Domain**: Which feature, technology, or concern?
- **Goal**: What should Claude know or do differently when working in this area?

If the input is vague (e.g., just "auth"), ask ONE clarifying question about what specifically the rule should cover.

## Step 2: Validate — Should This Be a Rule?

Before proceeding, evaluate whether a rule is the right mechanism. Check these conditions and **advise the user** if a different mechanism is better:

**Redirect to CLAUDE.md if:**

- The guidance applies universally to ALL files in the project (e.g., "always use pnpm", "port 3000")
- It's about project setup, build commands, or universal conventions
- Say: "This applies to the entire project. It belongs in CLAUDE.md, not a path-specific rule. Want me to add it there instead?"

**Redirect to CLAUDE.local.md if:**

- It's a personal preference not shared with the team (e.g., "I prefer verbose output")
- Say: "This is a personal preference. It belongs in CLAUDE.local.md. Want me to add it there instead?"

**Redirect to auto memory if:**

- It's a discovered insight or debugging finding (e.g., "the audit_logs table needs an index")
- It's temporary or session-specific context
- Say: "This is learned knowledge, not a permanent convention. It's better stored in auto memory. Want me to save it there instead?"

**Redirect to a skill if:**

- The user wants to execute an action or workflow, not provide passive context
- Say: "This sounds like an action, not context. A skill (/skill-name) would be more appropriate. Want me to create a skill instead?"

If the rule IS appropriate, proceed to Step 3.

## Step 3: Explore the Codebase

Based on the identified domain, explore the relevant code to understand:

1. **File patterns**: Which directories and file types are involved? Use Glob to discover the actual file structure.
2. **Key conventions**: Read 2-3 representative files to understand existing patterns.
3. **Design specs**: Check if `docs/architecture` and `docs/ARCHITECTURE.md` has a relevant spec file for this feature.
4. **Related docs**: Check `CLAUDE.md` for existing guidance on this area.

Build a mental model of what paths the rule should cover and what content would be most valuable.

## Step 4: Check for Overlap

Read all existing rule files in `.claude/rules/` and check:

1. **Direct overlap**: Does an existing rule already cover these paths or this topic?
2. **Partial overlap**: Would this rule's paths intersect with an existing rule's paths?
3. **CLAUDE.md duplication**: Is this guidance already in the project's CLAUDE.md?

If overlap is found:

- If minor: suggest extending the existing rule instead of creating a new one
- If the existing rule is stale or wrong: suggest updating it
- If no overlap: proceed

Report findings to the user before continuing.

## Step 5: Propose the Rule

Present the proposed rule to the user for approval. Show:

1. **Filename**: `{topic}.md` in kebab-case
2. **Path patterns**: The glob patterns that will trigger this rule
3. **Content preview**: The full markdown content

### Content Guidelines

The rule content MUST follow these principles:

**DO include:**

- Pointers to design spec files (e.g., "Read `docs/design/X-spec.md` before making changes")
- Key architectural constraints (2-3 bullet points)
- Common mistakes to avoid in this area (learned patterns)
- Import conventions specific to this area
- Brief context on why things are done this way

**DO NOT include:**

- Full design spec content (just reference the file path)
- Content already in CLAUDE.md (don't duplicate)
- Generic coding advice (keep it specific to this area)
- Marketing language, motivational text, or emojis in headers
- More than 100 lines (if longer, suggest splitting into multiple rules)

### File Format

```markdown
---
paths:
  - 'pattern/one/**'
  - 'pattern/two/**/*.ts'
---

# [Rule Title]

[Brief context: what this area is about, 1-2 sentences]

## Key Decisions

- [Architectural decision 1]
- [Architectural decision 2]

## Conventions

- [Pattern or convention specific to these files]
- [Import rule or naming convention]

## Common Mistakes

- [Thing that's easy to get wrong]
- [Another pitfall]

## Reference

- Design spec: `docs/design/relevant-spec.md`
- Related: `other-relevant-file.md`
```

## Step 6: Confirm and Create

Ask the user: "Does this look right? Want me to adjust the paths, content, or filename?"

Wait for explicit confirmation before creating the file.

Once confirmed, create the file at `.claude/rules/{filename}.md`.

After creation, remind the user: "The rule will take effect in your next Claude Code session (rules load at session startup)."

## Error Handling

- **No matching files for proposed paths**: Warn the user that the glob patterns don't match any existing files. Ask if this is intentional (e.g., for files that will be created soon).
- **Too many matching files (>500)**: Warn that the rule might be too broad. Suggest narrowing the paths.
- **Rule file already exists with same name**: Ask if they want to update the existing rule or choose a different name.
