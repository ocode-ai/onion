---
name: work
description: |
  Continue work on active feature. Read session and identify next phase.
  Update progress via Task Manager abstraction.
model: sonnet
---

# Engineer Work

We are currently working on a feature that is specified in the following folder:

<folder>
#$ARGUMENTS
</folder>

To work on this, you should:

- Read all markdown files in the folder
- Review the plan.md file and identify which Phase is currently in progress
- Present the user with a plan to approach the next phase

## 🔄 **Auto-Update Task Manager**

This command **automatically updates** the task during development using the abstraction:

```typescript
// Detect provider and get adapter
const config = detectProvider();
const taskManager = getTaskManager();

if (!taskManager.isConfigured) {
  console.warn('⚠️ Offline mode - progress will not be synced');
}
```

### **✅ Automatic Updates FOR EACH PHASE:**

- **Progress comment** when phase is completed
- **SUBTASK STATUS UPDATE** - Updates corresponding subtask status to "done"
- **plan.md update** with status and decisions
- **Estimated % progress** based on completed phases
- **Activity timestamp** for temporal tracking

### **🔗 CRITICAL: Phase→Subtask Mapping**

**MANDATORY**: When a phase is completed, the system must:

1. **Identify corresponding subtask** via mapping established in context.md
2. **Update subtask status** to "done" automatically
3. **Document completion** with timestamp and phase metrics

### **💬 DUAL Comment Strategy:**

When completing a phase, the system automatically:

1. **Creates DETAILED comment on SUBTASK**
2. **Creates SUMMARY comment on MAIN TASK**

### **📋 Task Identification:**

1. **Context.md**: Read task-id from session context file
2. **Active session**: Automatically detect session in `.claude/sessions/`
3. **🆕 PHASE-SUBTASK MAPPING**: Read mapping from context.md to correlate phases→subtasks

### **🗺️ SUBTASK MAPPING STRUCTURE (context.md):**

```markdown
## 📋 Phase-Subtask Mapping

- **Phase 1**: "Phase Name" → Subtask ID: [subtask-id-1]
- **Phase 2**: "Phase Name" → Subtask ID: [subtask-id-2]
```

### **⚡ AUTOMATIC EXECUTION (Via Abstraction):**

When a phase is marked as "Completed ✅" in plan.md, the system must **EXECUTE IN THIS ORDER**:

```typescript
// 1. Get task manager
const taskManager = getTaskManager();

if (taskManager.isConfigured) {
  // 2. DETAILED comment on SUBTASK
  await taskManager.addComment(
    subtaskId,
    `
🔧 PHASE COMPLETED: ${phaseName}

━━━━━━━━━━━━━━

📁 FILES MODIFIED:
${filesModified.map((f) => `   ∟ ${f}`).join('\n')}

🔧 IMPLEMENTATIONS:
${implementations.map((impl) => `   ▶ ${impl}`).join('\n')}

💡 TECHNICAL DECISIONS:
${decisions.map((d) => `   ∟ ${d}`).join('\n')}

🚀 NEXT STEPS:
   ∟ ${nextPhase}

━━━━━━━━━━━━━━

⏰ Completed: ${timestamp} | 🎯 Status: Done
  `,
  );

  // 3. Update SUBTASK STATUS
  await taskManager.updateStatus(subtaskId, 'done');

  // 4. SUMMARY comment on MAIN TASK
  await taskManager.addComment(
    mainTaskId,
    `
📝 PROGRESS: Phase ${phaseNum}/${totalPhases} Completed

✅ ${phaseName} - Completed
   ∟ Subtask: #${subtaskId}
   ∟ Details: See comment on subtask

🎯 Next: Phase ${phaseNum + 1}/${totalPhases} - ${nextPhaseName}

⏰ ${timestamp}
  `,
  );
}
```

## Important:

When you develop the code for the current phase, use the development, code-review, and test sub-agents when appropriate to preserve as much of your context as possible.

Every time you complete a phase of the plan:

- **AUTO-UPDATE**: Add progress comment via abstraction
- **TRACKING**: Check checkboxes in the description corresponding to completed criteria
- Pause and ask the user to validate your code.
- Make necessary changes until approved
- Update the corresponding phase in the plan.md file marking what was done and adding helpful comments for the developer who will approach the next phases, especially about questions, decisions, etc.
- Only start the next phase after the user agrees that you should begin.

## 🔗 References

- Abstraction: `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/`
- Detector: `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/detector.md`
- Factory: `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/factory.md`
- Comment patterns: `common/prompts/clickup-patterns.md`

Now, review the current development phase and provide the user with a plan on how to approach it.
