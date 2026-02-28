---
name: collect
description: Collect new feature ideas or bugs for the project. Use when the user wants to log a new idea, report a bug, capture a feature request, or add something to the backlog.
argument-hint: 'description of feature or bug'
disable-model-invocation: true
---

You are a product expert tasked with helping a human collect new feature/bug ideas for this project.

The user provided the following arguments:

<arguments>
$ARGUMENTS
</arguments>

Your goal is to understand the request. Ask questions to clarify the request. Then save it to the project management software.

At this point, you don't need to write a complete specification for the request, just make sure it is adequately understood.

The perfect task will have:

- A title
- A good description so we can remember it later in the refinement phase
- If it's a bug, an indication of where the bug is happening

## The Process

When the user presents a new task to collect, you will:

- Make sure you understand the task clearly and ask for clarifications if you don't understand
- Draft a quick title and description and present it to the user for approval. Make any necessary changes.

Save the task to the configured task manager (via Task Manager abstraction).

## Automatic Story Points Estimation

**CRITICAL:** After creating the task, ALWAYS estimate story points automatically.

### Step: Estimate Story Points

```markdown
@story-points-framework-specialist

Please analyze and estimate the following collected task:

**Task:** [approved title]
**Description:** [approved description]
**Type:** [feature/bug]

Provide complete story points estimation following the framework.
```

### Update Task with Estimate

```typescript
// After creating task via Task Manager abstraction
const taskManager = getTaskManager();
const estimate = await getStoryPointsEstimate(taskDescription);

// Update task with Story Points custom field
await taskManager.updateTask(taskId, {
  customFields: {
    'Story Points': estimate.points,
  },
});

// Add comment with analysis
await taskManager.addComment(
  taskId,
  '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' +
    '📊 STORY POINTS ESTIMATION\n' +
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' +
    `🎲 Story Points: ${estimate.points} points\n\n` +
    `⚡ ANALYSIS:\n` +
    `∟ Complexity: ${estimate.complexity}\n` +
    `∟ Risk: ${estimate.risk}\n` +
    `∟ Uncertainty: ${estimate.uncertainty}\n\n` +
    `💡 RECOMMENDATIONS:\n` +
    `${estimate.recommendations}\n` +
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
);
```

**Note:** If estimate > 13 points, alert that the task may need to be broken down during refinement.
