---
name: autorestatus
description: >
  Show AutoResearch current status and progress. TRIGGER when user says
  "/autorestatus", "check research status", "research progress",
  "autoresearch status", or "is the research loop running?"
---

# AutoResearch — Status

## Trigger
`/autorestatus` — Show current research loop status

## How It Works

Reads from the wiki's state file and log, then runs QMD status:

1. Read `.autoresearch/state.json` — current loop state
2. Read `wiki/log.md` — recent activity (last 15 lines)
3. Read `wiki/index.md` — current coverage (count only, don't read all)
4. Run `qmd status` — search index health
5. Run `CronList` — check if cron job is scheduled

## CRITICAL: Cross-Validate Cron Job Status

The `cron_job_id` in state.json may be stale (expired cron, old session).
ALWAYS verify against CronList:

```
1. Read cron_job_id from state.json
2. Run CronList → get list of active job IDs
3. IF cron_job_id in state.json is found in CronList:
     → Display: "Job ID: <cron_xxx> | Next run: <timestamp>"
   IF NOT found in CronList (or CronList is empty):
     → Display: "Job ID: none — not scheduled"
     → DO NOT show the stale cron_job_id from state.json
4. If CronList fails or returns empty, treat as no cron job
```

## Output Format

```
═══════════════════════════════════════════════════════
  AUTORESEARCH STATUS
═══════════════════════════════════════════════════════
  Loop:        <running|paused|stopped>
  Started:     <timestamp>
  Last cycle:  <timestamp> (<N> seconds ago)
  Cycles:      <N> completed
  Duration:    <avg Xm Ys per cycle>

  COVERAGE (<real calculated scores>)
  ─────────────────────────────────────────────────
  Sources:     <N> (from state.json)
  Pages:       <N> created, <N> updated
  Entities:    <N> (from index.md)
  Concepts:    <N> (from index.md)

  METRIC SCORES (from state.json)
  ─────────────────────────────────────────────────
  Coverage:    <score>  (<trend: improving/stable/declining>)
  Recency:     <score>
  Coherence:   <score>
  Novelty:     <score>
  TOTAL:       <weighted score>

  CRON JOB
  ─────────────────────────────────────────────────
  Job ID:      <cron_xxx (VERIFIED) or "none — not scheduled">
  Next run:    <timestamp or "N/A">
  Note:        "Verified against CronList — stale IDs excluded"

  RECENT ACTIVITY (last 3 cycles from log.md)
  ─────────────────────────────────────────────────
  <last 3 log entries>

  NEXT CYCLE
  ─────────────────────────────────────────────────
  Priorities:  <current priority list>
  Pending:    <N> gaps queued
  QMD sync:   <auto via watch paths>

  Human commands available:
    "set priority: <topic>" — reorder queue
    "skip cycle"            — jump to next cycle
    /autorestop             — stop gracefully
═══════════════════════════════════════════════════════
```

## If No State File

```
No active research loop found.

Start one with: /autoresearch

Or for one-time research: /deepdive
```

## If Loop is Running

Show that the loop is CronCreate-scheduled and when the next cycle fires.

## Metric Trend Calculation

```
IF cycle >= 3:
  prev_scores = [score at cycle N-2, N-1]
  curr_score = score at cycle N
  IF curr > avg(prev) * 1.05: trend = "improving"
  IF curr < avg(prev) * 0.95: trend = "declining"
  ELSE: trend = "stable"
```
