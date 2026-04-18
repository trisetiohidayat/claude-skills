---
name: autorestop
description: >
  Stop AutoResearch running session gracefully. TRIGGER when user says
  "/autorestop", "stop research", "stop the research loop",
  "stop autoresearch", or "pause the knowledge expansion".
---

# AutoResearch — Stop

## Trigger
`/autorestop` — Stop the research loop gracefully

## Behavior

### Step 1 — Cancel Cron Job (CRITICAL)

```
1. CronList → find AutoResearch cron job ID
2. CronDelete <job_id>  ← cancel scheduled next cycle
3. Log: "Cron job cancelled"
```

### Step 2 — Complete Current State

```
1. Read .autoresearch/state.json
2. Update final values:
   - status: "stopped"
   - cycle: <current cycle>
   - coverage_score, recency_score, coherence_score, novelty_score
   - last_cycle_at: <current timestamp>
3. Write to .autoresearch/state.json
```

### Step 3 — Log Final Entry

```
Append to wiki/log.md:
## [YYYY-MM-DD] autoresearch | STOPPED at CYCLE N
- Final coverage: <score>
- Total sources: <N>
- Total pages created: <N>
- Total pages updated: <N>
- Status: gracefully stopped
- Resume with: /autoresearch or /autorestart
```

### Step 4 — QMD Final Sync

```
qmd update && qmd embed --max-batch-mb 100
```

## Output

```
═══════════════════════════════════════════════════════
  AUTORESEARCH — STOPPED
═══════════════════════════════════════════════════════
  Mode:        graceful
  Cycles:      <N> completed
  Pages:       <N> created | <N> updated
  Sources:     <N> processed
  Final Score: <total_score>

  METRICS
    Coverage:  <score>
    Recency:   <score>
    Coherence: <score>
    Novelty:   <score>

  Cron job:    cancelled

  State saved: .autoresearch/state.json
  Log entry:  wiki/log.md
  QMD sync:   done

  Resume:      /autoresearch or /autorestart
═══════════════════════════════════════════════════════

Stopping does NOT lose work.
All wiki pages and QMD index are persisted.
State preserves your position for resume.
```

## Resume vs Restart

On next `/autoresearch` invocation:
- If `state.status == "stopped"`: AutoResume from cycle N (no prompt)
- If `state.status == "force_stopped"`: Offer to resume or start fresh
- If no state file: Start fresh

## If Cron Job Already Gone

If CronList shows no AutoResearch cron job, just stop gracefully — the loop may have been stopped already or never started with cron.
