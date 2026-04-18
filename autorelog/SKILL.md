---
name: autorelog
description: >
  Show AutoResearch activity log. TRIGGER when user says "/autorelog",
  "show research log", "show log", "activity log", or "research history".
---

# AutoResearch — Activity Log

## Trigger
`/autorelog [lines=50]` — Show recent activity log (default 50 lines)

## Options
- `lines=N` — Number of lines to show (default 50)
- `cycles=N` — Show last N cycles only

## Output

Reads from `wiki/log.md` and `.autoresearch/state.json`:

```
═══════════════════════════════════════════════════════
  AUTORESEARCH — ACTIVITY LOG
═══════════════════════════════════════════════════════
  Total cycles: <N>
  Sources processed: <N>
  Pages created: <N>
  Pages updated: <N>
  Status: <running|paused|stopped>
  Cron job: <cron_xxx or none>

  METRICS (from state.json)
  ─────────────────────────────────────────────────
  Coverage:    <score>
  Recency:     <score>
  Coherence:   <score>
  Novelty:    <score>
  TOTAL:      <weighted score>

  RECENT CYCLES
  ─────────────────────────────────────────────────

  ## [YYYY-MM-DD] autoresearch | CYCLE N — <status>
  - Sources: <N> processed | <N> new
  - Pages: <N> created | <N> updated
  - Metrics: cov=<cov> rec=<rec> coh=<coh> nov=<nov> total=<total>
  - Next: <topic>

  ## [YYYY-MM-DD] skill-fix | <description>
  ...

  ## [YYYY-MM-DD] ingest | <Source Title>
  ...

─────────────────────────────────────────────────────
  (showing last N lines from wiki/log.md)
═══════════════════════════════════════════════════════
```

## Filtering

- `/autorelog cycles:5` — show last 5 research cycles only
- `/autorelog ingest` — show only ingest events
- `/autorelog errors` — show only error events

## If No Log

If `wiki/log.md` doesn't exist or is empty:
```
No activity log found. Start the research loop with:

  /autoresearch

Or for a one-time research session:

  /deepdive
```
