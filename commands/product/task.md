---
name: task
description: |
  Task creation with intelligent hierarchical decomposition.
  Use to create structured tasks with subtasks and action items.
  Supports: ClickUp, Asana, Linear (via TASK_MANAGER_PROVIDER).
model: sonnet
parameters:
  - name: description
    description: Task description
    required: true
  - name: project_name
    description: Project/list name (optional)
    required: false
---

# 🚀 Task Creation with Decomposition

Create structured tasks in the configured task manager.

## 🚨 MANDATORY ACTION FIRST: Detect Provider

**⚠️ CRITICAL - EXECUTE BEFORE ANY OTHER ACTION:**

**STEP 0 (MANDATORY):** Read `.env` file to detect `TASK_MANAGER_PROVIDER`

```bash
# EXECUTE FIRST: Read .env using read_file
read_file .env
```

**AFTER READING .env, EXTRACT:**

- Value of `TASK_MANAGER_PROVIDER` (can be: `clickup`, `asana`, `linear`, or `none`)
- If `TASK_MANAGER_PROVIDER=clickup`: verify if `CLICKUP_API_TOKEN` exists
- If `TASK_MANAGER_PROVIDER=asana`: verify if `ASANA_ACCESS_TOKEN` exists
- If `TASK_MANAGER_PROVIDER=linear`: verify if `LINEAR_API_KEY` exists
- If `TASK_MANAGER_PROVIDER=none` or doesn't exist: offline mode

**⚠️ NEVER ASSUME THE PROVIDER - ALWAYS READ .env FIRST**

## 🔧 Prerequisite: Verify Provider

Before creating tasks, verify configuration:

1. ✅ **READ `.env` using `read_file .env`** (MANDATORY)
2. Extract `TASK_MANAGER_PROVIDER` from read content
3. If not configured or "none":
   - Warn: "⚠️ No task manager configured. Run /meta/setup-integration"
   - Continue with local structure (no synchronization)
4. If configured:
   - Use corresponding adapter from `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/adapters/`
   - **IF `TASK_MANAGER_PROVIDER=asana`: use `mcp_asana_*` tools**
   - **IF `TASK_MANAGER_PROVIDER=clickup`: use `mcp_ClickUp_*` tools**

## 🎯 Objective

Establish solid foundation for development with Task → Subtask → Action Item decomposition.

## ⚡ Execution Flow

### Step 1: Detect Provider and Configuration

**CRITICAL:** Execute these actions in EXACT order:

1. **MANDATORY - Read `.env` to detect provider:**

   ```bash
   # EXECUTE FIRST: Read .env file
   read_file .env

   # EXTRACT from read content:
   # - TASK_MANAGER_PROVIDER=??? (clickup, asana, linear, or none)
   # - Verify corresponding required variables:
   #   * If clickup: CLICKUP_API_TOKEN
   #   * If asana: ASANA_ACCESS_TOKEN
   #   * If linear: LINEAR_API_KEY
   ```

2. **Validate configuration based on EXTRACTED value:**

   ```markdown
   IF extracted TASK*MANAGER_PROVIDER = 'clickup':
   ✅ Verify CLICKUP_API_TOKEN exists in read .env
   ✅ If doesn't exist: warn and continue in offline mode
   ✅ Use mcp_ClickUp*\* tools to create tasks

   IF extracted TASK*MANAGER_PROVIDER = 'asana':
   ✅ Verify ASANA_ACCESS_TOKEN exists in read .env
   ✅ If doesn't exist: warn and continue in offline mode
   ✅ Use mcp_asana*\* tools to create tasks

   IF extracted TASK_MANAGER_PROVIDER = 'linear':
   ✅ Verify LINEAR_API_KEY exists in read .env
   ✅ If doesn't exist: warn and continue in offline mode

   IF extracted TASK_MANAGER_PROVIDER = 'none' or not found:
   ⚠️ Offline mode - tasks will not be synchronized
   💡 Warn: Run /meta/setup-integration to configure
   ```

3. **Resolve project/list (if `project_name` provided):**

   ```markdown
   IF project_name provided:

   - ClickUp: use mcp_ClickUp_clickup_get_list with list_name
   - Asana: use mcp_asana_asana_get_projects and search by name
   - If not found: ask user or use default

   IF project_name not provided:

   - ClickUp: use CLICKUP_DEFAULT_LIST_ID from .env
   - Asana: use ASANA_DEFAULT_PROJECT_ID from .env
   - If not configured: list options and ask user
   ```

### Step 2: Context Analysis

```bash
# Review project documentation
read_file README.md
ls docs/*.md

# Understand existing structure
list_dir src/
```

### Step 3: Deep Analysis and Understanding

**ALWAYS follow this mandatory sequence:**

#### 📚 Documentation Review (MANDATORY)

1. **Review FIRST the project's current documentation**: README.md and .md files in `docs/` folder
2. **Analyze existing structure** based on reviewed documentation
3. **Identify patterns and technologies** already established in the project

#### 🤔 Task Understanding

1. **Read carefully** the provided task description: `{{description}}`
2. **Formulate internal questions** to clarify ambiguities or missing information
3. **Analyze how the task fits** into the existing project structure
4. **Identify complexity, dependencies and applicable patterns**:
   - Simple (1-3 days): 2-3 subtasks
   - Medium (4-7 days): 3-4 subtasks
   - Complex (1-2 weeks): 4-6 subtasks
   - Epic (>2 weeks): Break into multiple tasks

#### ✅ Confirmation and Clarification (MANDATORY)

1. **Before proceeding**, confirm your understanding of the task
2. **If more information is needed**, state which additional details would be useful
3. **ALWAYS present your plan** to the user before creating the task
4. **Ask for explicit confirmation** before executing creation in Task Manager

### Step 4: Final Plan Presentation (MANDATORY BEFORE CREATING)

**⚠️ CRITICAL: NEVER create task without presenting plan and obtaining confirmation**

**MANDATORY: Present your plan to the user and ask for confirmation before creating:**

```markdown
## 🎯 PROPOSED TASK PLAN

### **📋 Main Task**

**Name**: [TASK_NAME]
**Type**: [Feature/Bug/Improvement/Research]
**Complexity**: [Simple/Medium/High]
**Estimate**: [ESTIMATED_TIME]

### **📝 Functional Description**

[CLEAR_DESCRIPTION_OF_OBJECTIVE]

### **🏗️ Technical Architecture**

[TECHNICAL_DETAIL_AND_IMPLEMENTATION]

### **📚 Suggested Libraries/Dependencies**

[DEPENDENCY_LIST_PRIORITIZING_KNOWN_ONES]

### **🔧 Affected Components**

[COMPONENTS_TO_BE_MODIFIED]

### **✅ Acceptance Criteria**

- [ ] [CRITERION_1]
- [ ] [CRITERION_2]
- [ ] [CRITERION_3]

### **🧪 Testing Points of Attention**

[TEST_STRATEGY_AND_VALIDATION]

❓ **Is this plan correct? Can I proceed with task creation in the Task Manager?** [Y/n]
```

**⚠️ IMPORTANT:**

- **WAIT for explicit user confirmation** before proceeding
- **DO NOT create task** until receiving confirmation
- **If user requests adjustments**, revise plan and present again

### Step 5: Hierarchical Decomposition (AFTER CONFIRMATION)

Consult @task-specialist for structure:

```
📋 TASK (High-Level Objective)
├── 🔧 Subtask 1 (Functional Component)
│   ├── ✅ Action Item 1.1 (1-4h)
│   ├── ✅ Action Item 1.2 (1-4h)
│   └── ✅ Action Item 1.3 (1-4h)
└── 🔧 Subtask 2 (Functional Component)
    ├── ✅ Action Item 2.1 (1-4h)
    └── ✅ Action Item 2.2 (1-4h)
```

### Step 6: Estimate Story Points (Automatic)

**CRITICAL:** After decomposition, ALWAYS estimate story points for main task and each subtask.

#### 6.1. Estimate Main Task

```markdown
@story-points-framework-specialist

Please analyze and estimate the following task:

**Main Task:** {{description}}
**Identified Subtasks:** [list of subtasks]
**Initial Complexity:** [simple/medium/complex]

Provide:

1. Story points for main task
2. Analysis of complexity, risk and uncertainty
3. Recommendations (breakdown, risks, dependencies)
```

**Expected output:**

- Main task story points
- Complete factor analysis
- Recommendations

#### 6.2. Estimate Each Subtask

```markdown
For each identified subtask:

@story-points-framework-specialist

**Subtask:** [subtask name]
**Description:** [subtask description]
**Action items:** [list of action items]

Estimate story points for this subtask.
```

**Store:**

- Story points per subtask
- Total points (sum of subtasks)

#### 6.3. Validate Consistency

```markdown
IF sum(subtasks) > main_task:
⚠️ WARNING: Sum of subtasks greater than main task
Adjust main task to: sum(subtasks)

IF main_task > 13 points:
⚠️ ALERT: Task identified as EPIC
Propose breaking into smaller tasks
```

### Step 7: Create in Manager (AFTER USER CONFIRMATION)

**🚨 CRITICAL EXECUTION ORDER:**

**⚠️ ALWAYS FOLLOW THIS ORDER:**

1. **FIRST**: Create task in Task Manager (record what WILL be done)
2. **THEN**: If task involves immediate work (e.g., delete files, make changes), execute the work
3. **LAST**: Update task with result (comments, status, evidence)

**❌ NEVER DO:**

- Execute work before creating the task
- Create task after work is already done
- Assume work was done before creating the task

**✅ ALWAYS:**

- Create task first to record intention
- Execute work after task is created (if applicable)
- Update task with progress and result

**CRITICAL:**

- ✅ Use MCP tools directly (`mcp_ClickUp_*`, `mcp_asana_*`)
- ✅ Follow Task Manager abstraction pattern to normalize input/output
- ✅ Consult `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/interface.md` for data format
- ✅ Consult `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/adapters/{provider}.md` for specific mappings

**IMPORTANT:** Even when using MCP directly, data must follow abstraction pattern:

- Normalized input (priority: urgent/high/normal/low)
- Normalized output (TaskOutput with standardized fields)
- Status mapping according to interface

#### 6.1. Prepare Normalized Data (Abstraction Pattern)

```markdown
Prepare normalized structure following ITaskManager interface:

**Main Task:**

- name: "{{description}}"
- markdownDescription: [markdown format with objective, criteria, story points]
- priority: 'high' (normalized: urgent/high/normal/low)
- tags: ['feature']
- projectId: [resolved in Step 1]

**Each Subtask:**

- name: [subtask name]
- markdownDescription: [description + story points]
- priority: [inherit from main task or 'normal']
- tags: [subtask tags if any]
```

#### 6.2. Create Main Task (Execute MCP)

**IF provider = 'clickup':**

```markdown
1. Call mcp_ClickUp_clickup_create_task with:
   - list_id: [resolved projectId]
   - name: [normalized name]
   - markdown_description: [complete markdown description]
   - priority: 'high' (map: high → 'high' in ClickUp)
   - tags: ['feature']
   - workspace_id: [CLICKUP_WORKSPACE_ID from .env, if available]

2. Extract task.id from response
3. Store task.url for final output
```

**IF provider = 'asana':**

```markdown
1. Call mcp_asana_asana_create_task with:
   - name: [normalized name]
   - html_notes: [markdown description converted to HTML]
   - project_id: [resolved projectId]
   - workspace: [ASANA_WORKSPACE_ID from .env, if available]

2. Extract task.gid from response (data.gid)
3. Build URL: https://app.asana.com/0/0/{gid}
```

**IF provider = 'none' or not configured:**

```markdown
⚠️ Offline mode - create local structure only

- Generate local ID: local-{timestamp}
- Create document in .claude/sessions/tasks/{id}.md
- Warn that it will not be synchronized
```

#### 6.3. Create Subtasks (Execute MCP)

**For each subtask in decomposition:**

**IF provider = 'clickup':**

```markdown
Call mcp_ClickUp_clickup_create_task with:

- list_id: [same list_id as main task]
- parent: [task.id of created main task]
- name: [subtask name]
- markdown_description: [description + story points]
- priority: [map to ClickUp]
- tags: [subtask tags]
```

**IF provider = 'asana':**

```markdown
Call mcp_asana_asana_create_task with:

- name: [subtask name]
- html_notes: [description + story points in HTML]
- parent: [task.gid of main task]
- workspace: [ASANA_WORKSPACE_ID]
```

**IF provider = 'none':**

```markdown
Create local document: .claude/sessions/tasks/{parent-id}/subtasks/{subtask-id}.md
```

#### 6.4. Add Initial Comment (Execute MCP)

**Prepare formatted comment:**

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 TASK CREATED VIA /product/task
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 COMPLEXITY: ${complexity}
🎲 STORY POINTS:
∟ Main Task: ${mainTaskStoryPoints} points
∟ Subtasks: ${subtasksPoints} points (${subtasks.length} subtasks)
∟ Total: ${totalPoints} points

⚡ FACTORS:
${factorsSummary}

💡 RECOMMENDATIONS:
${recommendations}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**IF provider = 'clickup':**

```markdown
Call mcp_ClickUp_clickup_create_task_comment with:

- task_id: [task.id]
- comment_text: [formatted comment above]
```

**IF provider = 'asana':**

```markdown
Call mcp_asana_asana_create_task_story with:

- task_id: [task.gid]
- text: [formatted comment above]
```

**IF provider = 'none':**

```markdown
Add comment to local document
```

#### 6.5. Normalize Output (Abstraction Pattern)

```markdown
After creating, normalize response to standard format:

**Normalized TaskOutput:**

- id: [task.id or task.gid]
- provider: [clickup/asana/none]
- name: [task name]
- url: [complete task URL]
- status: 'todo' (initial default)
- createdAt: [ISO timestamp]
- projectId: [project/list ID]
- storyPoints: [main task story points]
- subtasks: [array of normalized subtasks]
```

### Step 8: Execute Work (If Applicable)

**⚠️ ONLY if task involves immediate work:**

If the task description indicates work that should be executed immediately (e.g., "Remove files X", "Create structure Y", "Update configuration Z"):

1. **AFTER creating the task in Task Manager**, execute the described work
2. **Document what was done** during execution
3. **Update the task** with detailed comment of the result

**If task is only for planning/future development:**

- Skip this step
- Task remains as "To Do" for later execution

### Step 9: Update Task with Result

**If work was executed in Step 8:**

1. **Add detailed comment** in task with:
   - What was done
   - Files modified/created/deleted
   - Execution result
   - Next steps (if any)

2. **Update status** if appropriate:
   - If work complete: status → "Done"
   - If partial: status → "In Progress"
   - If only planning: keep "To Do"

### Step 10: Present Result

## 📤 Expected Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TASK CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Task: {{description}}
🔗 URL: [provider url]
📊 Provider: [clickup/asana/linear/local]

🎲 STORY POINTS:
∟ Main Task: [X] points
∟ Subtasks: [Y] points ([N] subtasks)
∟ Total: [Z] points

📊 ANALYSIS:
∟ Complexity: [high/medium/low]
∟ Risk: [high/medium/low]
∟ Uncertainty: [high/medium/low]

🔧 STRUCTURE:
├── Subtask 1: [name] - [X] points
│   ├── ✅ Item 1.1
│   └── ✅ Item 1.2
└── Subtask 2: [name] - [Y] points
    └── ✅ Item 2.1

💡 RECOMMENDATIONS:
${recommendations}

🚀 Next: /engineer/start [feature-slug]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📏 Decomposition Rules

| Type    | Duration | Subtasks | Action Items/Subtask |
| ------- | -------- | -------- | -------------------- |
| Simple  | 1-3d     | 2-3      | 2-3                  |
| Medium  | 4-7d     | 3-4      | 3-4                  |
| Complex | 1-2wk    | 4-6      | 3-5                  |
| Epic    | >2wk     | Break    | -                    |

## 🔗 References

### Task Manager Abstraction

- **Interface:** `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/interface.md` - Normalized input/output format
- **Detector:** `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/detector.md` - How to detect provider from .env
- **Adapters (Mapping Guides):**
  - `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/adapters/clickup.md` - ClickUp MCP mapping
  - `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/adapters/asana.md` - Asana MCP mapping
  - `${CLAUDE_PLUGIN_ROOT}/reference/utils/task-manager/types.md` - Shared types

### Decomposition and Estimates

- **Decomposition:** @task-specialist
- **Estimates:** @story-points-framework-specialist, /product/estimate
- **Framework:** `docs/knowbase/frameworks/framework_story_points.md`

### Formatting Patterns

- **ClickUp:** `${CLAUDE_PLUGIN_ROOT}/reference/common/prompts/clickup-patterns.md`
- **Formatting:** `${CLAUDE_PLUGIN_ROOT}/reference/docs/clickup/clickup-formatting.md`

## ⚠️ Notes

- **MANDATORY:** ALWAYS present plan and ask for confirmation before creating task
- **MANDATORY:** Create task FIRST, then execute work (if applicable)
- Action items: maximum 4h each
- If epic: suggest breaking into multiple tasks
- If provider not configured: works in local mode
- **Automatic estimates:** Story points automatically calculated for main task and all subtasks
- **Validation:** If sum(subtasks) > main task, adjust main task
- **Epics:** If task > 13 points, alert and propose breakdown
