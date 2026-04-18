---
name: claude-build-loop
description: >
  Continuous Interruptable Build-Testing Loop. TRIGGER when user says
  "/claude-build-loop", "/build-loop", "start the build loop", "run the build-test loop",
  "keep building", "start building", "continuous build", or asks to initiate a
  persistent build-and-test workflow that references a wiki for context and conventions.

  This skill ALWAYS starts with a PLANNING phase followed by a CONFIRM gate before any
  agents are spawned. It then enters an autonomous execute loop via CronCreate scheduling.
  Human can intervene at any time: add topics, pause, stop, check status.

  DO NOT USE THIS when:
  - You want one-shot code generation (just write the code normally)
  - You want a quick build without per-stage testing
  - The user has not specified a wiki to reference
---

# Claude-Build-Loop — Continuous Interruptable Build-Testing Loop

## Core Philosophy

> "Build with confidence: plan first, confirm before you act, then execute continuously
> with a dedicated tester per stage, persistent state across restarts, and the ability
> for humans to intervene at any moment."

This skill implements a **structured build pipeline** with three mandatory phases:

1. **PLANNING** — Analyze the wiki, create an ordered build plan, show the user
2. **CONFIRM GATE** — Wait for explicit user approval before touching any code
3. **EXECUTE** — Continuous build-test loop via CronCreate-scheduled cycles

The key differences from AutoResearch:
- **Starts with a plan + confirm gate** (not autonomous from the start)
- **Build stages are ordered and sequential** (not just gap-filling)
- **Has a dedicated tester agent per stage** that runs tests and records results
- **Result tracking per step** (not just pages created)
- **References a wiki** for context, conventions, and existing patterns

---

## Why This Architecture?

### The Confirm Gate Matters

AutoResearch is purely additive (adding wiki pages), so wrong turns are low-cost.
Build-work is destructive by default — a wrong stage can corrupt modules, break tests,
or leave the codebase in an inconsistent state. The confirm gate forces the human to
review the plan BEFORE any code is written, dramatically reducing wasted work.

### Ordered Stages vs Gap-Filling

AutoResearch's gap model (find a hole, fill it) works for knowledge bases where topics
are independent. Build work has hard dependencies — you cannot test a model until
it exists, you cannot write views until models are defined. Ordered stages make
dependencies explicit and prevent wasted effort on work that cannot succeed yet.

### Dedicated Tester Per Stage

A builder that also tests itself is subject to confirmation bias — it will mark its
own work as passing to feel productive. The separate tester agent has no stake in
whether the builder succeeded, so its assessment is more honest.

### State File Per-Step Tracking

AutoResearch tracks aggregate metrics (total pages created). This skill tracks each
stage individually: what was built, what tests ran, what passed/failed, and why.
This means restarts are surgical — we resume exactly where we left off, not by
re-assessing the whole workspace.

---

## Loop Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  BUILD LOOP — Three Phases                                   │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  PHASE 1: PLANNING (human participates)                 │ │
│  │  Read wiki → Analyze conventions → Create build plan    │ │
│  │  Output: ordered list of stages with descriptions        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  PHASE 2: CONFIRM GATE (human decides)                  │ │
│  │  Show full plan → Ask "proceed?" → WAIT                 │ │
│  │  If no → modify plan, re-show, re-confirm                │ │
│  │  If yes → proceed to Phase 3                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  PHASE 3: EXECUTE (CronCreate-scheduled loop)           │ │
│  │                                                           │ │
│  │  CYCLE START (via CronCreate trigger)                    │ │
│  │    ↓                                                     │ │
│  │  1. CHECK INTERVENTIONS  ── queue? → process first      │ │
│  │    ↓                                                     │ │
│  │  2. FIND NEXT STAGE   ── first non-completed stage      │ │
│  │    ↓                                                     │ │
│  │  3. ANALYZE STATE     ── last step, pending, retry?     │ │
│  │    ↓                                                     │ │
│  │  4. EXECUTE STAGE     ── builder + tester concurrently  │ │
│  │    ↓                                                     │ │
│  │  5. RECORD RESULTS    ── update state.json              │ │
│  │    ↓                                                     │ │
│  │  6. IF PASSES → next stage                              │ │
│  │     IF FAILS  → retry 3x, then pause + ask human        │ │
│  │    ↓                                                     │ │
│  │  7. REPORT TO HUMAN  ── status box                      │ │
│  │    ↓                                                     │ │
│  │  8. SCHEDULE NEXT CYCLE ── CronCreate                   │ │
│  │    ↓                                                     │ │
│  │  [Human can intervene at any time]                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**CronCreate is the survival mechanism.** Without it, Claude Code restarts kill the loop.
With it, the loop resumes automatically from wherever state.json was last updated.

---

## Step 0 — Skill Invocation & Initialization

### 0.1 Invocation Detection

This skill activates when the user says:
- `/claude-build-loop` or `/build-loop`
- "start the build loop" or "run the build-test loop"
- "keep building" or "start building"
- "continuous build" or similar phrasings

### 0.2 Collect Required Inputs

**Input 1: Build Goal**
Ask the user: "What do you want to build? Describe the end goal clearly."

If the user provides a goal in the same message as the invocation, use that.

**Input 2: Wiki Path**
Ask the user: "Which wiki should I reference for context and conventions?"

Options:
- If user provides an explicit path → use that
- If user says "this wiki" or similar → use the current working directory if it has a wiki structure (check for CLAUDE.md, index.md, wiki/ directory)
- If user says "detect" → use the `odoo-path-resolver` skill to find the wiki path
- If no wiki is available → abort with error: "This skill requires a wiki to reference for conventions and patterns. Please specify a wiki path."

**Validate inputs before proceeding.**

### 0.3 Detect Resume vs Fresh Start

```
IF .claude-build-loop/state.json exists:
  READ state
  IF status == "paused":
    → Offer to resume (show current stage + summary)
    → Wait for user confirm ("resume" or "start fresh")
  IF status == "completed":
    → Announce completion + summary
    → Offer to start a new build
  IF status == "failed":
    → Show failed stage + error notes
    → Offer to retry, skip stage, or start fresh
  IF status == "waiting_confirm":
    → This should not happen if skill was properly exited, but if it does,
      re-show the plan and re-enter Phase 2
  IF status == "running":
    → Warn: loop may already be running via cron
    → Show current status
    → Ask: "Resume from current state or start fresh?"
ELSE:
  → Fresh start
```

### 0.4 Initialize State (Fresh Start)

Create `.claude-build-loop/state.json`:
```json
{
  "started_at": "<ISO timestamp>",
  "build_goal": "<user's goal>",
  "wiki_path": "<resolved wiki path>",
  "status": "planning",
  "current_stage_index": 0,
  "build_plan": [],
  "intervention_topics": [],
  "last_cycle_at": null,
  "cycle_count": 0,
  "cron_job_id": null
}
```

Create the directory if it doesn't exist:
```bash
mkdir -p .claude-build-loop
```

### 0.5 Load Wiki Context

Read the wiki files in this order (use the wiki_path resolved in Step 0.2):

1. `<wiki_path>/CLAUDE.md` — schema, conventions, page types
2. `<wiki_path>/index.md` — content catalog, existing modules/features
3. `<wiki_path>/log.md` — recent activity (last 20 lines) for context
4. Any domain-specific reference files relevant to the build goal (e.g., architecture docs, module structure docs)

Also search for any existing build-related documentation in the wiki:
```bash
Glob: <wiki_path>/**/*build*.md
Glob: <wiki_path>/**/*architecture*.md
Glob: <wiki_path>/**/*module*.md
```

---

## Phase 1 — PLANNING

**Purpose:** Analyze the wiki, understand existing patterns, and create an ordered build
plan. This phase is always the first step and requires reading the wiki thoroughly.

### P1.1 Analyze Wiki Conventions

Read enough of the wiki to understand:
- **Module structure**: How are modules organized? What directories exist?
- **Naming conventions**: File naming, function naming, class naming
- **Existing modules**: What already exists that the build should extend or integrate with?
- **Testing patterns**: How are tests structured? What test frameworks are used?
- **View patterns**: How are XML views defined? What common patterns exist?
- **Model patterns**: How are Odoo models defined? Field types? Computed fields?
- **Workflow conventions**: How does code get committed? Branch strategy?

Use Grep to find patterns across the codebase:
```bash
# Find existing model definitions
Grep: "class .*\\(models\\.Model\\)" path=<wiki_path>

# Find existing test files
Glob: <wiki_path>/**/*test*.py

# Find view XML patterns
Glob: <wiki_path>/**/*.xml

# Find field definitions as examples
Grep: "^    \\w* = fields\\." path=<wiki_path>
```

### P1.2 Identify Build Dependencies

From the wiki analysis and the user's goal, determine:
1. **What modules/components need to be created** (new files)
2. **What existing modules need to be extended** (modifications)
3. **What tests need to be written** (test coverage per stage)
4. **What wiki references apply to each stage** (conventions to follow)
5. **What dependencies exist** (Stage B cannot start until Stage A completes)

### P1.3 Create Ordered Build Plan

Structure the build as a list of ordered stages. Each stage must have:

| Field | Description |
|-------|-------------|
| `id` | Unique ID in format "stage-1", "stage-2", etc. |
| `name` | Short, descriptive name for this stage |
| `description` | Detailed description of what this stage builds |
| `wiki_references` | List of wiki files/pages this stage references |
| `dependencies` | List of stage IDs that must complete before this stage |
| `test_coverage` | What tests should run during this stage |
| `expected_outcome` | What files should exist/modified after this stage |
| `status` | Always "pending" at plan creation time |

**Stage ordering principles:**
- Put foundation stages first (models, base modules)
- Put integration/UI stages after foundation
- Put tests as late as possible (but within the same stage as the code they test)
- Each stage should be completable in 5-15 minutes of agent work
- If a stage feels larger than that, split it into two stages

### P1.4 Display Plan and Transition to Phase 2

Show the build plan to the user in this format:

```
═══════════════════════════════════════════════════════════════
  BUILD PLAN — <user goal>
═══════════════════════════════════════════════════════════════
  Wiki:   <wiki path>
  Stages: <N> total

  [1] <Stage 1 Name>
      <description>
      Wiki refs: <list>
      Tests:    <test coverage description>
      Depends:  none

  [2] <Stage 2 Name>
      <description>
      Wiki refs: <list>
      Tests:    <test coverage description>
      Depends:  stage-1

  ...

═══════════════════════════════════════════════════════════════
  Does this plan look right? Proceed, or suggest changes?
═══════════════════════════════════════════════════════════════
```

**CRITICAL:** After showing the plan, STOP and wait for user input.
Do NOT proceed to Phase 2 without explicit confirmation. Do NOT spawn any agents.
Just wait.

---

## Phase 2 — CONFIRM GATE

**Purpose:** Wait for explicit human approval before any code is written or agents are spawned.

### C2.1 Display Full Plan with Details

Show the complete numbered plan. For each stage, display:
- Stage number and name
- Full description of what gets built
- Wiki references (which files/conventions apply)
- Test coverage expectations
- Dependencies (which prior stages must complete)

### C2.2 Ask for Confirmation

```
═══════════════════════════════════════════════════════════════
  CONFIRM GATE
═══════════════════════════════════════════════════════════════

  I will NOT spawn any agents or write any code until you confirm.

  Review the plan above, then:

  YES / PROCEED / START
    → Begin executing from Stage 1

  CHANGE / MODIFY / NO
    → Tell me what to change (add/remove/reorder stages,
      change descriptions, adjust test coverage)
    → I will regenerate the plan and re-show it

  ABORT
    → Stop and discard this build plan entirely
═══════════════════════════════════════════════════════════════
```

### C2.3 Handle User Response

**If YES/PROCEED/START (or equivalent):**
1. Update `state.json`: set `status` to `"running"`, keep `build_plan` as-is
2. Proceed to Phase 3 (EXECUTE), Cycle 1

**If CHANGE/MODIFY/NO:**
1. Ask what specifically to change
2. Accept additions, removals, reorders, description changes
3. Regenerate the plan
4. Re-show the updated plan
5. Return to C2.2 (re-ask for confirmation)

**If ABORT:**
1. Update `state.json`: set `status` to `"completed"` (clean exit)
2. Announce: "Build plan discarded. Say /claude-build-loop to start fresh."
3. Do nothing else

**If the user provides no clear signal:**
- Keep waiting. Do not timeout. Do not proceed autonomously.

---

## Phase 3 — EXECUTE (Continuous Loop)

**Purpose:** Execute stages sequentially, spawn builder+tester agents per stage,
track results, and schedule the next cycle via CronCreate.

### E3.1 Cycle Start (CronCreate Trigger)

Each cycle begins when:
- **First cycle:** triggered by user confirming the plan (Phase 2)
- **Subsequent cycles:** triggered by CronCreate scheduling (Step E3.9)

When a CronCreate trigger fires, the prompt it sends is:
```
Continue the claude-build-loop — run the /claude-build-loop skill.
Read .claude-build-loop/state.json to understand current state.
Resume from where you left off. Do NOT re-announce startup unless status is "planning".
```

### E3.2 Check Intervention Topics

```
1. Read intervention_topics from state.json
2. If intervention_topics is non-empty:
     → Process the first topic (see Human Intervention section)
     → Update state.json (remove processed topic)
     → Continue to E3.3
3. If intervention_topics is empty:
     → Continue to E3.3
```

Intervention topics are added by the user during the loop and processed before the
next stage executes. They allow human direction without stopping the loop.

### E3.3 Find Next Pending Stage

```
1. Read state.json
2. Iterate build_plan in order (stage-1, stage-2, ...)
3. Find the first stage where status is NOT "completed", "skipped", or "failed"
   (pending, in_progress, or paused-still)
4. Set current_stage_index to that stage's index
5. If all stages are completed → set status to "completed", announce success, stop loop
```

### E3.4 Analyze Current State

Before spawning agents, assess:
- **What was the last stage?** (check last completed stage's notes + test_notes)
- **What is the current stage?** (read its definition from build_plan)
- **Has this stage been attempted before?** (check retry count in notes)
- **What wiki context applies?** (load the stage's wiki_references)

If the current stage was previously attempted and failed, check:
- How many retries have occurred? (look for "retry" in notes)
- Was the failure due to a transient issue (network, timeout) or a real problem?
- Should we retry or ask the human?

### E3.5 Execute Current Stage (Builder + Tester Concurrently)

**This is the core execution step. Builder and tester run concurrently.**

#### E3.5.1 Mark Stage as In-Progress

Before spawning agents, update state.json:
```json
{
  "status": "running",
  "build_plan": [
    {
      "id": "stage-1",
      "status": "in_progress",
      "started_at": "<ISO timestamp>",
      "agents": ["builder-1", "tester-1"]
    }
  ]
}
```

#### E3.5.2 Spawn Builder Agent

Spawn a general-purpose background agent with:

```
Model: sonnet
Isolation: worktree
Background: true
Tools: Read, Glob, Grep, Bash, WebSearch, WebFetch, Write, Edit, Agent
Skills: <relevant domain skills based on stage type>

Prompt to builder agent:
---
Execute Stage <N>: <stage name>

Goal: <user's overall build goal>
Stage description: <stage description from build_plan>
Wiki path: <wiki path>
Wiki references: <list of wiki files to consult>
Expected outcome: <expected_outcome from build_plan>
Test coverage expected: <test_coverage from build_plan>

Task:
1. Read the wiki references to understand conventions
2. Implement the stage according to the description
3. Follow wiki naming conventions and patterns exactly
4. Write tests that match the test_coverage description
5. Do NOT modify files outside this stage's scope
6. When done, write a completion note to /tmp/builder-<stage-id>.txt:
   - What files were created/modified
   - What was the implementation approach
   - Any issues encountered
   - What tests were written

Work in: <the actual working directory or worktree path>
---
```

#### E3.5.3 Spawn Tester Agent

Spawn a general-purpose background agent with:

```
Model: sonnet
Isolation: worktree
Background: true
Tools: Read, Glob, Grep, Bash, Write, Agent

Prompt to tester agent:
---
Test Stage <N>: <stage name>

Goal: <user's overall build goal>
Stage description: <stage description from build_plan>
Wiki path: <wiki path>
Test coverage expected: <test_coverage from build_plan>
Expected outcome: <expected_outcome from build_plan>

Task:
1. Read the wiki to understand the testing conventions and frameworks used
2. Read the stage description carefully
3. Read the files that the builder created/modified
4. Run the tests written for this stage
5. If no tests exist: write and run basic smoke tests
6. Evaluate: does the implementation match the expected outcome?
7. Record your findings in /tmp/tester-<stage-id>.txt:
   - What was tested (list each test)
   - What PASSED (with brief evidence)
   - What FAILED (with error messages, line numbers)
   - Overall test_status: "pass", "fail", or "not_run"
   - Any additional test coverage recommendations

Work in: <the actual working directory or worktree path>
---
```

#### E3.5.4 Wait for Both Agents

```
Wait for builder agent to complete:
  → Read /tmp/builder-<stage-id>.txt
  → Extract files created/modified, implementation notes

Wait for tester agent to complete:
  → Read /tmp/tester-<stage-id>.txt
  → Extract test results: what passed, what failed
```

**Why concurrent?** Builder and tester work on different concerns (implementation vs.
verification). They can run in parallel without conflicting. The tester reads the
builder's output, so the tester's work naturally follows — but spawning them
concurrently saves one round-trip of latency.

#### E3.5.5 Retry Logic (Builder Failure)

```
IF builder agent fails OR returns an error:
  1. Increment retry count (store in stage notes as "retry: N")
  2. IF retry count < 3:
       → Log: "Stage <N> builder failed (attempt N/3). Retrying..."
       → Re-execute E3.5.2 through E3.5.4
  3. IF retry count >= 3:
       → Mark stage status = "failed"
       → Mark test_status = "not_run"
       → Set status = "paused"
       → Add note: "Stage failed after 3 retries. Human intervention required."
       → Do NOT schedule next cycle
       → Announce to user (see E3.7)
       → WAIT for human response
```

**Tester failure does NOT block the build.** If the tester fails to run tests
(e.g., test environment issue), log the error but continue. The tester is meant
to inform, not gate. The human decides what to do about test failures.

### E3.6 Record Results

After both agents complete, update `state.json`:

```json
{
  "build_plan": [
    {
      "id": "stage-1",
      "name": "Stage name",
      "description": "What this stage does",
      "status": "completed",
      "test_status": "pass|fail|not_run",
      "test_notes": "<concatenated tester output>",
      "agents": ["builder-1", "tester-1"],
      "started_at": "<ISO timestamp>",
      "completed_at": "<ISO timestamp>",
      "notes": "<builder completion notes + any issues>"
    }
  ]
}
```

### E3.7 Report to Human (Status Box)

After each cycle, show the status box:

```
═══════════════════════════════════════════════════════════════
  BUILD LOOP — Continuous Build & Test
═══════════════════════════════════════════════════════════════
  Goal:      <user goal>
  Wiki:      <wiki path>
  Status:    <running|paused|waiting_confirm>
  Stage:     <N/M> — <stage name>
  Test:      <pass|fail|pending>
  Cycle:     <N>
  CronJob:   <ID or none>
  Interventions: <N> pending

  /build-status  → detailed status
  add topic:     → queue new task
  pause build-loop → pause
  stop build-loop  → stop
═══════════════════════════════════════════════════════════════
```

Also include a brief narrative:
- What was accomplished this cycle
- What the next stage is
- Any warnings or issues

### E3.8 Stage Transition Logic

```
IF stage test_status == "pass":
  → Mark stage status = "completed"
  → Advance current_stage_index to next stage
  → Log: "Stage <N> (<name>) completed and passed tests."
  → Proceed to E3.9 (schedule next cycle)

IF stage test_status == "fail":
  → Mark stage status = "failed"
  → Set status = "paused"
  → Do NOT advance stage index
  → Do NOT schedule next cycle
  → Show failure details to user:
    - What failed (test name + error)
    - What was built
    - Options: "retry", "skip stage", "stop build-loop"
  → WAIT for human response (see Human Intervention)

IF stage test_status == "not_run":
  → Mark stage status = "completed"
  → Advance current_stage_index
  → Log: "Stage <N> completed, tests not run."
  → Proceed to E3.9
```

### E3.9 Schedule Next Cycle

```
1. CronCreate with:
     cron: "*/5 * * * *"  (every 5 minutes — adjust based on typical stage duration)
     prompt: "Continue the claude-build-loop — run the /claude-build-loop skill.
              Read .claude-build-loop/state.json to understand current state.
              Resume from where you left off. Do NOT re-announce startup."
     recurring: true

2. Extract returned cron_job_id
3. Update state.json: "cron_job_id": "<ID>"
4. Update state.json: "last_cycle_at": "<ISO timestamp>"
5. Update state.json: "cycle_count": <N + 1>
```

**The cron job is what keeps the loop alive across Claude Code restarts.**

**If CronCreate fails:**
- Log a warning
- Fall back to: announce "Could not schedule next cycle. Say /claude-build-loop to continue."
- Do not lose state — state.json is still accurate

---

## State File

`.claude-build-loop/state.json`:

```json
{
  "started_at": "2026-04-18T10:00:00Z",
  "build_goal": "Build a purchase order approval workflow module",
  "wiki_path": "/Users/tri-mac/projects/acme-wiki",
  "status": "running",
  "current_stage_index": 2,
  "build_plan": [
    {
      "id": "stage-1",
      "name": "Create purchase.order model",
      "description": "Define the purchase.order model with order_line O2M, state field, and compute totals",
      "wiki_references": ["wiki/models/purchase-order.md", "wiki/conventions/fields.md"],
      "dependencies": [],
      "test_coverage": "Unit tests for compute method, constraints for required fields",
      "expected_outcome": "models/purchase_order.py with PurchaseOrder model",
      "status": "completed",
      "test_status": "pass",
      "test_notes": "test_compute_amount: PASS, test_required_vendor: PASS, test_required_date: PASS",
      "agents": ["builder-1", "tester-1"],
      "started_at": "2026-04-18T10:05:00Z",
      "completed_at": "2026-04-18T10:12:00Z",
      "notes": "Created PurchaseOrder and PurchaseOrderLine models. Computed amount correctly sums lines."
    },
    {
      "id": "stage-2",
      "name": "Create approval workflow",
      "description": "Implement state machine: draft → submitted → approved → done, with write restrictions",
      "wiki_references": ["wiki/workflows/state-machine.md", "wiki/models/purchase-order.md"],
      "dependencies": ["stage-1"],
      "test_coverage": "Test state transitions, test write restrictions per state",
      "expected_outcome": "models/purchase_order.py with workflow methods",
      "status": "in_progress",
      "test_status": "pending",
      "test_notes": "",
      "agents": ["builder-2", "tester-2"],
      "started_at": "2026-04-18T10:15:00Z",
      "completed_at": null,
      "notes": ""
    }
  ],
  "intervention_topics": [],
  "last_cycle_at": "2026-04-18T10:15:30Z",
  "cycle_count": 2,
  "cron_job_id": "cron_xyz789"
}
```

---

## Human Intervention

The human can intervene at any time, even mid-cycle.

### C2 — Check for Commands

Any time the human types something during the loop, check if it's a command:

| Command | Effect |
|---------|--------|
| `add topic: <description>` | Add to `intervention_topics` queue. Processed at next cycle start. |
| `skip stage` | Mark current stage as "skipped". Advance to next stage. |
| `pause build-loop` | Set status to "paused". Cancel cron job (CronList → CronDelete). |
| `stop build-loop` | Set status to "completed". Cancel cron job. Announce stop. |
| `resume build-loop` | Set status to "running". Re-schedule via CronCreate. Continue. |
| `/build-status` | Show detailed status (separate skill, see below) |
| `/build-plan` | Re-show the full build plan |
| `retry` | Retry current failed stage (after human saw failure) |
| `abort` | Stop everything, discard state |

### add topic: <description>

```
1. Read state.json
2. Append to intervention_topics array:
   {
     "added_at": "<ISO timestamp>",
     "description": "<user's topic description>"
   }
3. Write state.json
4. Announce: "Queued: <description>. Will be processed at start of next cycle."
```

Topics are processed FIFO at the beginning of each cycle (E3.2). The builder agent
is given the intervention topics as additional context when spawning.

### pause build-loop

```
1. Update state.json: "status": "paused"
2. CronList → find build-loop cron job ID → CronDelete <ID>
3. Update state.json: "cron_job_id": null
4. Announce: "Build loop paused. Stage <N>/<M> (<name>) is current.
              Say 'resume build-loop' to continue."
```

### resume build-loop

```
1. Update state.json: "status": "running"
2. Proceed to E3.9: re-schedule via CronCreate
3. Announce: "Build loop resumed from Stage <N>/<M> (<name>)."
```

### skip stage

```
1. Read current_stage_index from state.json
2. Find that stage in build_plan
3. Update: status = "skipped", completed_at = <timestamp>
4. Advance current_stage_index by 1
5. Announce: "Stage <N> (<name>) skipped. Moving to Stage <N+1>."
6. Proceed to E3.9
```

### stop build-loop

```
1. Update state.json: "status": "completed"
2. CronList → find build-loop cron job ID → CronDelete <ID>
3. Update state.json: "cron_job_id": null
4. Announce summary:
   - How many stages completed
   - Which stage was current when stopped
   - Any failures or skipped stages
5. Say: "Build loop stopped. Say /claude-build-loop to start fresh or resume."
```

---

## Agent Configuration

### Builder Agent

| Config | Value | Rationale |
|--------|-------|-----------|
| **model** | `sonnet` | Sufficient capability for code generation, good cost balance |
| **isolation** | `worktree` | Clean context per invocation, prevents cross-stage contamination |
| **background** | `true` | Non-blocking, allows tester to run concurrently |
| **tools** | `Read, Glob, Grep, Bash, WebSearch, WebFetch, Write, Edit, Agent` | Full filesystem + research + writing |
| **skills** | Domain-specific skills based on stage type (e.g., `odoo19-model-new` for models, `odoo19-view-form` for views) | Leverage existing domain knowledge |

**Spawn parameters passed to builder:**
```
Goal: <user's overall build goal>
Stage description: <stage description>
Wiki path: <wiki path>
Wiki references: <list>
Expected outcome: <files that should exist>
Test coverage expected: <what tests should exist>
```

### Tester Agent

| Config | Value | Rationale |
|--------|-------|-----------|
| **model** | `sonnet` | Sufficient for test writing and evaluation |
| **isolation** | `worktree` | Same clean context as builder |
| **background** | `true` | Non-blocking, runs concurrently with builder |
| **tools** | `Read, Glob, Grep, Bash, Write, Agent` | Read code + run tests + write results |

**Spawn parameters passed to tester:**
```
Stage description: <stage description>
Wiki path: <wiki path>
Test coverage expected: <what should be tested>
Expected outcome: <what files should exist>
```

### Why Concurrent Builder + Tester?

Running them sequentially would be safer (test after build) but slower.
Running them concurrently is acceptable because:
1. The tester reads the builder's output files — it naturally waits for the builder
2. If the builder fails, the tester will find nothing to test (test_status = "not_run")
3. The tester is informational, not a gate — builder failures are caught separately
4. The 5-10 second spawn latency of the tester is hidden behind builder execution

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Builder agent fails | Retry up to 3 times; after 3 failures, pause and ask human |
| Builder returns no output | Treat as failure, increment retry count |
| Tester agent fails | Log error, set test_status = "not_run", continue |
| Tester finds no files to test | Log warning, set test_status = "not_run", continue |
| Test failures found | Mark stage failed, pause, show failures to human, await response |
| CronCreate fails | Fall back to conversation scheduling, warn user |
| CronCreate job already exists | Skip (idempotent), do not create duplicate |
| state.json read fails | Log critical error, do not continue, ask human |
| state.json write fails | Log critical error, do not continue, ask human |
| Wiki path invalid | Abort with error: "Wiki not found at <path>. Please specify a valid wiki." |
| No stages in plan | This should not happen after Phase 1. Abort with error. |
| Human says "abort" | Stop everything, discard nothing (keep state), announce stop |
| Cycle exceeds 30 minutes | Force advance to next stage, log warning, continue |
| Worktree creation fails | Fall back to main working directory, warn user |

### State Write Safety

**CRITICAL:** Writing state.json must succeed before any agent is spawned or before
any user-visible action is taken. If state.json write fails:

```
1. Log: "CRITICAL: Failed to write state.json. Check disk space and permissions."
2. Do NOT proceed with any agents or state changes
3. Tell the user: "Could not write state file. Build loop cannot continue safely.
   Check disk space and permissions, then say 'resume build-loop'."
4. Set status = "paused" in memory (even if not persisted)
```

---

## /build-status Skill (Detailed Status)

Triggered by user saying `/build-status` or "show build status".

```
═══════════════════════════════════════════════════════════════
  BUILD LOOP STATUS
═══════════════════════════════════════════════════════════════
  Goal:      <build_goal>
  Wiki:      <wiki_path>
  Status:    <status>
  Cycle:     <cycle_count>
  Started:   <started_at>
  Last run:  <last_cycle_at>
  CronJob:   <cron_job_id or "none">

  STAGES (<N> total):
  ┌────────────────────────────────────────────────────────┐
  │ [<N>] <stage name>         — <status> / test: <test_status>
  │       <description>
  │       Notes: <notes or "none">
  │       Tests: <test_notes or "none">
  └────────────────────────────────────────────────────────┘

  Interventions queued: <N>
  <list intervention topics if any>
═══════════════════════════════════════════════════════════════
```

---

## /build-plan Skill (Re-show Plan)

Triggered by user saying `/build-plan` or "show build plan".

```
═══════════════════════════════════════════════════════════════
  BUILD PLAN — <build_goal>
═══════════════════════════════════════════════════════════════
  Wiki:   <wiki_path>
  Stages: <N> total | Current: <current_stage_index + 1>

  [1] <stage-1 name> .............. <status>
      <description>

  [2] <stage-2 name> .............. <status>
      <description>

  ...

  Progress: <completed_count>/<N> completed |
            <failed_count> failed |
            <skipped_count> skipped
═══════════════════════════════════════════════════════════════
```

---

## Related Skills

| Skill | Role |
|-------|------|
| `autoresearch` | Continuous knowledge compounding (complementary: build code vs. research docs) |
| `llm-wiki` | Wiki initialization and maintenance |
| `odoo-path-resolver` | Detect wiki path if user says "detect" |
| `odoo-debug-tdd` | TDD workflow for Odoo (referenced by tester agent) |
| `odoo-code-quality` | Code quality checks (referenced by tester agent) |

---

## Starting the Loop

```
/claude-build-loop
/build-loop
```

Or in conversation:
```
start the build loop
run the build-test loop for my Odoo module
keep building the purchase order workflow
```

The skill will ask for the build goal and wiki path if not provided, then enter
the PLANNING phase. The loop schedules itself via CronCreate after the user confirms.

Say `stop build-loop` to stop, `/build-status` to check progress, or `add topic:` to queue a task.

---

## State File Schema Reference

For reference when implementing, the complete state.json schema:

```json
{
  "started_at": "string (ISO 8601)",           // When the build started
  "build_goal": "string",                        // User's stated goal
  "wiki_path": "string (absolute path)",        // Wiki being referenced
  "status": "string",                           // planning|waiting_confirm|running|paused|completed|failed
  "current_stage_index": "integer",             // 0-based index into build_plan
  "build_plan": [
    {
      "id": "string",                           // "stage-1", "stage-2", etc.
      "name": "string",                         // Short display name
      "description": "string",                  // What this stage does
      "wiki_references": ["string"],            // Wiki files to read
      "dependencies": ["string"],               // Stage IDs that must complete first
      "test_coverage": "string",                // What tests should exist
      "expected_outcome": "string",             // Files that should exist
      "status": "string",                       // pending|in_progress|completed|failed|skipped
      "test_status": "string",                  // pending|pass|fail|not_run
      "test_notes": "string",                    // Tester's output
      "agents": ["string"],                     // Agent IDs for this stage
      "started_at": "string (ISO 8601|null)",
      "completed_at": "string (ISO 8601|null)",
      "notes": "string"                         // Builder notes + issues
    }
  ],
  "intervention_topics": [
    {
      "added_at": "string (ISO 8601)",
      "description": "string"
    }
  ],
  "last_cycle_at": "string (ISO 8601|null)",
  "cycle_count": "integer",
  "cron_job_id": "string|null"
}
```
