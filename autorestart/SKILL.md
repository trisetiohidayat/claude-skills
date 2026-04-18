---
name: autorestart
description: >
  Explicit AutoResearch restart manager. TRIGGER when user says "/autorestart",
  wants a fresh start ("start over", "reset research", "mulai ulang research"),
  or the loop was force-stopped/crashed. Do NOT trigger for simple "resume" or
  "continue" requests — those go to /autoresearch which auto-resumes from stopped state.
---

# AutoResearch — Restart / Resume

## Trigger
`/autorestart` — Resume from paused/stopped state, or start fresh
`/autorestart --fresh` — Start completely fresh (ignores existing state)

## Behavior

### Step 1 — Check State

```
IF .autoresearch/state.json exists:
  READ state
  IF status == "running":
    → "Loop is already running. Use /autorestatus to check, or /autorestop to stop first."
  IF status == "stopped":
    → Auto-resume (no prompt needed — graceful stop means safe to resume)
  IF status == "paused":
    → Show pause summary, offer resume
  IF status == "force_stopped":
    → OFFER: "Resume from cycle N or start fresh?"
ELSE:
  → Start fresh
```

### Step 2 — Resume (auto or confirmed)

```
1. Load state from .autoresearch/state.json
2. Restore: current_priorities, pending_gaps
3. Read: wiki/log.md (last 15 lines), wiki/index.md
4. Set status: "running"
5. Save state
6. CronCreate for next cycle
   → Save cron_job_id to state.json
7. Announce resume:
```

```
═══════════════════════════════════════════════════════
  AUTORESEARCH — RESUMED
═══════════════════════════════════════════════════════
  Resuming from: cycle <N>
  Previous:     <timestamp>
  Pages:        <N> created | <N> updated
  Sources:      <N> processed
  Final score:  <score>

  Priorities restored: <list>
  Pending gaps: <N>

  Cron job scheduled (ID: <cron_xxx>)
  Next cycle: <in N seconds>
═══════════════════════════════════════════════════════
```

### Step 3 — Fresh Start

```
1. Archive old state: mv .autoresearch/state.json .autoresearch/state.archive.json
2. Initialize new .autoresearch/state.json
3. Set status: "running"
4. CronCreate for next cycle
5. Announce fresh start
```

## Output

### Resume Summary (shown when stopped but not running)

```
═══════════════════════════════════════════════════════
  AUTORESEARCH — READY TO RESUME
═══════════════════════════════════════════════════════
  Previous session: <date>
  Cycles completed: <N>
  Pages created:   <N>
  Sources:        <N>
  Final score:    <score>

  Options:
    [1] Resume from cycle <N>  ← continues where we stopped
    [2] Start fresh           ← clear state, begin new
═══════════════════════════════════════════════════════
```

### Resume Confirmed

```
Resuming from cycle <N>...
Priorities restored: <list>
Pending gaps: <N>
Cron job scheduled.
Starting next cycle now.
```

## Relation to Other Skills

| Skill | Use |
|-------|-----|
| `/autoresearch` | Primary entry — auto-detects stopped state and resumes |
| `/autorestart` | Explicit resume/restart — useful when loop was force-stopped |
| `/autorestop` | Stop gracefully |
| `/autorestatus` | Check current state without acting |

**Usage note:** `/autoresearch` auto-resumes from graceful stops (status: "stopped") without prompting — use it for normal continuation. Use `/autorestart` explicitly for:
- Fresh start (`/autorestart --fresh`) — clear state, begin new
- Force-stopped/crashed state (status: "force_stopped") — offers resume vs fresh
- When you want to see the state summary before deciding what to do
