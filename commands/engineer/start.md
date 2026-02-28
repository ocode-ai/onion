---
name: start
description: |
  Start feature development. Creates session and analyzes tasks.
  Supports multiple task managers via TASK_MANAGER_PROVIDER.
model: sonnet
---

# Engineer Start

This is the command to start developing a feature.

## 🔧 Prerequisite: Detect Provider

```typescript
// Consult ${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/detector.md
const config = detectProvider();
const taskManager = getTaskManager();

// If there's a task-id in the input, validate compatibility
if (taskId) {
  const validation = validateProviderMatch(taskId, config.provider);
  if (!validation.valid) {
    console.warn(validation.warning);
    // Ask the user how to proceed
  }
}
```

## Configuration

- If we're not on a feature branch, ask permission to create one
- If we're on a feature branch that matches the feature name, we're ready
- Make sure a folder exists at .claude/sessions/<feature-slug>
- Ask the user for input for this session (you will receive one or more tasks to work on)

## Analysis

Analyze the tasks, parents and children if necessary, and build an initial understanding of what needs to be developed.

### **📋 Analysis via Task Manager:**

**IMPORTANT**: Use the abstraction to read tasks regardless of the provider:

```typescript
// Via abstraction - works for any provider (ClickUp, Asana, Linear)
const task = await taskManager.getTask(taskId);
const subtasks = await taskManager.getSubtasks(taskId);

// Document in context.md
console.log(`Provider: ${task.provider}`);
console.log(`Task: ${task.name}`);
console.log(`URL: ${task.url}`);
```

### **🎲 Story Points Validation (Optional but Recommended):**

**CRITICAL:** Before starting development, validate if task has story points estimate:

```typescript
// Check if task has estimated story points
const storyPoints = task.customFields?.find(
  (f) => f.name === 'Story Points',
)?.value;

if (!storyPoints || storyPoints === 0) {
  console.warn(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ WARNING: TASK WITHOUT STORY POINTS ESTIMATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Task: ${task.name}
🎲 Story Points: Not estimated

💡 RECOMMENDATIONS:
∟ Estimate before starting development
∟ Use: /product/estimate "${task.name}"
∟ Or: @story-points-framework-specialist

⚠️ Continuing without estimate may affect:
   - Sprint planning
   - Velocity tracking
   - Delivery predictability

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  `);

  // Ask the user if they want to estimate now
  const shouldEstimate = await askUser(
    'Do you want to estimate story points now? (y/n)',
  );

  if (shouldEstimate) {
    // Invoke estimation agent
    await invokeStoryPointsEstimation(task);
  }
} else if (storyPoints > 13) {
  console.warn(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ ALERT: TASK IDENTIFIED AS EPIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Task: ${task.name}
🎲 Story Points: ${storyPoints} points

💡 RECOMMENDATIONS:
∟ Consider breaking into multiple smaller tasks
∟ Use: /product/refine to detail requirements
∟ Verify if it really needs to be a single task

⚠️ Tasks > 13 points have:
   - Higher margin of error in estimate
   - Risk of not fitting in sprint
   - Difficulty tracking progress

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  `);

  // Ask the user if they want to continue
  const shouldContinue = await askUser('Do you want to continue anyway? (y/n)');
  if (!shouldContinue) {
    console.log(
      '💡 Suggestion: Use /product/refine to detail and break down the task',
    );
    return;
  }
} else {
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ESTIMATE VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Task: ${task.name}
🎲 Story Points: ${storyPoints} points

✅ Valid estimate for development

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  `);
}
```

### **🔍 Incompatible ID Validation:**

If the saved task-id is from a different provider than the configured one:

```
⚠️ INCOMPATIBILITY DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task ID: "86adfe9eb"
Detected provider: clickup
Configured provider: asana

💡 Suggested actions:
   1. Change TASK_MANAGER_PROVIDER to 'clickup' in .env
   2. Or clear the current session and create a new task
   3. Run /meta/setup-integration to reconfigure
```

### **🔍 Analysis Questions:**

Think carefully about what is being requested, make sure you understand exactly: - Why this is being built (context) - What is the expected outcome for this task? (objective) - How it should be built, only directionally, not in detail (approach) - If it requires the use of new APIs/tools, do you understand them? - How should it be tested? - What are the dependencies? - What are the constraints?

After reflecting on these questions, formulate the 3-5 most important clarifications needed to complete the task. Ask these questions to the human, while also providing your understanding and suggestions.

After getting the human's answers, consider whether you need to ask more questions. If so, ask more questions to the human.

Once you have a good understanding of what is being built, save it to the file .claude/sessions/<feature-slug>/context.md and ask the human to review.

If the human agrees with your understanding, you can proceed to the next step. Otherwise, continue iterating together until you get explicit approval to move forward.

If something you discussed here affects what was written in the requirements, ask the human for permission to edit those requirements and make adjustments.

## Architecture

Given your understanding of what will be built, you will now proceed to develop the feature architecture.

This is where you will put on your ultra-thinking hat and consider the best path to build the feature, also considering the patterns and best practices of this project.

Your architecture document should include: - A high-level overview of the system (before and after the change) - Affected components and their relationships, dependencies - Patterns and best practices that will be maintained or introduced - External dependencies - Constraints and assumptions - Trade-offs and alternatives - List of main files to be edited/created

Once you have a good understanding of what is being built, save it to the file .claude/sessions/<feature-slug>/architecture.md and ask the human to review.

## 🔄 **Auto-Update Task Manager**

This command **automatically updates** the task when it starts:

### **✅ Automatic Updates ALWAYS:**

```typescript
// Via abstraction - works for any provider
if (taskManager.isConfigured && taskId) {
  // Update status
  await taskManager.updateStatus(taskId, 'in_progress');

  // Add start comment
  await taskManager.addComment(
    taskId,
    `
🚀 DEVELOPMENT STARTED

━━━━━━━━━━━━━━━━━━━━━━━━

🏗️ SESSION ACTIVATED:
   ▶ Branch: feature/[slug]
   ▶ Session: .claude/sessions/[slug]/
   ▶ Provider: ${taskManager.provider}

📋 IMPLEMENTATION PLAN:
   ∟ Phase 1: [Description]
   ∟ Phase N: [Description]

━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Started: ${new Date().toISOString()}
  `,
  );
}
```

### **📋 Task Identification:**

1. **Context.md**: Reads task-id from the `.claude/sessions/[slug]/context.md` file
2. **Task Manager**: Uses `taskManager.getTask(taskId)` for complete structure
3. **🆕 PHASE-SUBTASK MAPPING**: Creates automatic phase→subtask mapping in context.md
4. **ID Validation**: Verifies ID compatibility with configured provider
5. **Not found**: Asks the user if they should link to a specific task

### **🗺️ REQUIRED: Create Phase-Subtask Mapping**

When subtasks exist, the system must **automatically**:

1. **Detect subtasks** via `taskManager.getSubtasks(taskId)`
2. **Correlate with phases** from plan.md (by order or name)
3. **Save mapping** in context.md for use by `/engineer/work`
4. **Validate correlation** and alert if there's a mismatch

## Research

If you're not sure how a specific library works, you can use Context7 and Perplexity to search for information about it. So, don't try to guess.

## 🔗 References

- Abstraction: `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/`
- Detector: `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/detector.md`
- Factory: `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/factory.md`

<feature-slug>
#$ARGUMENTS
</feature-slug>
