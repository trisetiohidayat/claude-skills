---
name: autoresearch
description: >
  Autonomous knowledge compounding loop. TRIGGER when user says "/autoresearch",
  "start research loop", "run autonomous research", "expand knowledge",
  "never stop researching", "keep researching", or asks to start the autonomous
  knowledge expansion loop.

  This skill runs indefinitely via CronCreate (auto-scheduled every N seconds).
  Human can set priorities, skip cycles, query status, or stop at any time.
  This is NOT the same as deepdive (which is one-shot session research).

  USE THIS when:
  - You want the agent to continuously expand the wiki without stopping
  - You want "never stop researching" behavior
  - You want knowledge compounding on autopilot

  DO NOT USE THIS when:
  - You want a one-time deep research session (use /deepdive instead)
  - You just want to ingest one source (use normal conversation)
---

# AutoResearch — Autonomous Knowledge Compounding Loop

## Core Philosophy

> "You are a completely autonomous researcher. If you run out of ideas, think harder. The loop runs until the human interrupts you, period."
> — adapted from [[karpathy-autoresearch]]

This skill implements an **indefinite research loop** that continuously expands the knowledge base. It schedules itself via CronCreate so cycles run automatically every N seconds — even across Claude Code restarts.

## Loop Architecture

```
┌──────────────────────────────────────────────────────────┐
│  AUTORESEARCH LOOP (CronCreate-scheduled)                 │
│                                                           │
│  SCHEDULED TRIGGER (every N seconds via CronCreate)       │
│     │                                                     │
│     ▼                                                     │
│  1. CHECK PRIORITIES ──→ Human set? → Reorder queue      │
│     │                                                     │
│     ▼                                                     │
│  2. ASSESS ───────────→ Coverage gaps? Stale pages?       │
│     │                                                     │
│     ▼                                                     │
│  3. RESEARCH ─────────→ Spawn researcher subagent(s)       │
│     │                                                     │
│     ▼                                                     │
│  4. INGEST ───────────→ Merge subagent results → wiki      │
│     │                                                     │
│     ▼                                                     │
│  5. SYNC ─────────────→ qmd update + qmd embed            │
│     │                                                     │
│     ▼                                                     │
│  6. REPORT ───────────→ Log results → Metric scores      │
│     │                                                     │
│     ▼                                                     │
│  SCHEDULE NEXT CYCLE ──→ CronCreate for in ~300s          │
│                                                           │
│  [Human can intervene at any time]                        │
└──────────────────────────────────────────────────────────┘
```

**Key difference from karpathy's program.md:** karpathy's agent runs in a tight loop (~5 min/experiment). This skill runs in a *scheduled* loop — CronCreate ensures cycles happen even if Claude Code restarts between cycles.

---

## Step 0 — Initialize

### 0.1 Detect Resume vs Fresh Start

```
IF .autoresearch/state.json exists:
  READ state
  IF status == "stopped" OR status == "paused":
    → Offer to resume (show summary)
  IF status == "force_stopped":
    → Offer to resume or start fresh
  IF status == "running":
    → Warn: loop may already be running via cron
ELSE:
  → Fresh start
```

### 0.2 Load Wiki Context

Read in this order:
1. `wiki/CLAUDE.md` — schema and conventions
2. `wiki/index.md` — current coverage map
3. `wiki/log.md` — recent activity (last 30 lines only)
4. `.autoresearch/state.json` — resume from previous state (if exists)

### 0.3 Load Configuration

Check for configuration in priority order:
1. **Frontmatter `config:`** in this skill file (highest priority)
2. **`wiki/.autoresearch/config.yaml`** — domain priorities, weights
3. **`wiki/.autoresearch/priorities.md`** — human-defined topics

Default configuration:
```yaml
config:
  domain: single
  priorities: []                    # empty = auto-detect gaps
  metric_weights:
    coverage: 0.4
    recency: 0.3
    coherence: 0.2
    novelty: 0.1
  max_sources_per_cycle: 5
  max_pages_per_cycle: 3
  cycle_pause_seconds: 300         # CronCreate interval
  stale_threshold_days: 7
  qmd_collections:
    - autoresearch-wiki
    - autoresearch-root
  use_subagent: true               # Spawn researcher subagent per gap
  subagent_parallel: true           # Spawn multiple subagents in parallel
  max_subagents_per_cycle: 3       # Max parallel subagents
```

### 0.4 Initialize State

Create `.autoresearch/state.json` if not exists:
```json
{
  "started_at": "<ISO timestamp>",
  "paused_at": null,
  "cycle": 0,
  "total_sources_processed": 0,
  "total_pages_created": 0,
  "total_pages_updated": 0,
  "coverage_score": 0.0,
  "recency_score": 0.0,
  "coherence_score": 0.0,
  "novelty_score": 0.0,
  "status": "running",
  "current_priorities": [],
  "pending_gaps": [],
  "last_cycle_at": null,
  "cycle_duration_seconds": 0,
  "errors_this_session": 0
}
```

### 0.5 Announce Start

```
════════════════════════════════════════════════════════════
  AUTORESEARCH — Autonomous Knowledge Compounding
════════════════════════════════════════════════════════════
  Started:      <timestamp>
  Wiki:         <real path>
  Domain:       <single/multi>
  Priorities:   <list or "auto-detect">
  Cycle Pause:  <N> seconds (via CronCreate)
  Subagent:     researcher.md (Sonnet, worktree, background)

  Metric Weights:
    Coverage:   <weight>
    Recency:    <weight>
    Coherence:  <weight>
    Novelty:    <weight>

  QMD Collections: <N> indexed
  QMD Total Docs: <N> total

  CronJob ID:  <cron job ID or "none">
  Resume from: <cycle N or "fresh start">

  "You may intervene at any time:
   set priority:, skip cycle, /autorestatus, /autorestop"
════════════════════════════════════════════════════════════
```

---

## Step 1 — Check Priorities

```
1. Read wiki/.autoresearch/priorities.md (if exists)
2. Check for human-set priorities in conversation context
3. Reorder research queue accordingly
```

**Priority levels:**
- **CRITICAL** — topics explicitly set by human (always first)
- **HIGH** — topics from priorities.md list
- **MEDIUM** — recently referenced but undocumented concepts
- **LOW** — auto-detected gaps from coverage analysis

---

## Step 2 — Assess

Run the assessment phase to identify what needs work.

**Assessment Output:**
```
ASSESSMENT CYCLE #N
  Coverage: <N entities>, <N concepts>, <N sources>
  Gaps:     <list of 3-5 priority gaps>
  Stale:    <N> pages need refresh
  Coherence: <N> orphaned/weakly-linked pages
```

### 2.1 Coverage Analysis (FAST — glob only)

```
1. Glob wiki/sources/*.md → count sources
2. Glob wiki/entities/*.md → count entities
3. Glob wiki/concepts/*.md → count concepts
4. Glob wiki/synthesis/*.md → count synthesis
5. Identify categories with < 3 pages (likely gaps)
6. Flag topics referenced in existing pages but missing pages
   → Use Grep for [[undocumented-concept]] patterns
```

### 2.2 Recency Analysis (FAST — glob + grep, NO read-all)

```
FOR each subdirectory (sources, entities, concepts, synthesis):
  glob *.md files
  grep "^date: " for frontmatter date
  No need to read full file content for date checking
```

Efficient command for staleness:
```bash
# Find pages older than stale_threshold_days WITHOUT reading all files
grep -r "^date: " wiki/sources/ wiki/entities/ wiki/concepts/ | \
  while read line; do
    date=$(echo "$line" | sed 's/.*date: //')
    days_old=$(($(date +%s) - $(date -j -f %Y-%m-%d "$date" +%s) ))
    if [ $days_old -gt $((stale_threshold_days * 86400)) ]; then
      echo "$line is stale"
    fi
  done
```

### 2.3 Coherence Analysis (FAST — grep wikilinks)

```
FOR each subdirectory:
  grep -l "\[\[" wiki/**/*.md | wc -l   # pages with wikilinks
  grep -c "\[\[" wiki/sources/*.md      # wikilinks per source page
  Flag pages with 0 wikilinks (orphans)
```

### 2.4 Gap Identification (QMD-powered)

```
1. Run QMD query: lex "undocumented concepts <domain>"
2. Run QMD query: hyde "A concept about X that is not yet in the wiki"
3. Check if any known entities (from existing wikilinks) are missing pages
4. Look for contradiction flags: grep -r "> \[!contradiction\]"
```

---

## Step 3 — Research (Subagent-Driven)

**This step now delegates to the `researcher` subagent instead of inline research.**

### 3.1 Spawn Researcher Subagent(s)

For each gap identified in Step 2 (up to `max_subagents_per_cycle`):

```
IF use_subagent == true:
  Spawn researcher subagent with:
    Topic: <gap name/description>
    Wiki path: <WIKI_PATH from config>
    QMD collection: <qmd_collections from config>
    Link style: kebab
    Tags: [autoresearch, <gap-category>]
    Effort: high
    Isolation: worktree
    Background: true

  → Subagent runs research pipeline independently
  → Subagent writes wiki pages directly
  → Subagent syncs QMD (if configured)
  → Subagent returns summary to parent

IF subagent_parallel == true AND gaps.length > 1:
  Spawn all subagents in parallel (max: max_subagents_per_cycle)
  Wait for all to complete

IF subagent_parallel == false:
  Spawn one at a time, wait for completion
```

**Spawn prompt template:**
```
Research and document: <GAP_DESCRIPTION>

Wiki configuration:
- Wiki path: /Users/tri-mac/claude-autoresearch/wiki/
- Conventions: Read wiki/CLAUDE.md for schema
- QMD collections: autoresearch-wiki, autoresearch-root
- Link style: kebab-case (e.g., [[sub-agents]], [[auto-memory]])
- Default tags: [autoresearch, <category>]

Task:
1. Conduct web research on this topic
2. Identify key entities, concepts, and claims
3. Write wiki pages following the schema
4. Update cross-references with existing pages
5. Sync QMD index
6. Return summary to parent

Quality gates:
- All wikilinks must be kebab-case
- All pages must have frontmatter (title, date, tags, links)
- Source pages must include source URL
- No duplicate pages (check index.md first)
```

### 3.2 Collect Subagent Results

```
FOR each spawned subagent:
  Wait for completion (if not background)
  Collect summary:
    - Sources processed
    - Pages created
    - Pages updated
    - Wikilinks added
    - QMD synced
    - New insights
    - Contradictions flagged

  Merge into cycle results
```

### 3.3 Fallback (Subagent Failure)

```
IF subagent fails or is unavailable:
  → Log warning: "Subagent unavailable, using inline research"
  → Fall back to inline research (Steps 3.1-3.4 below)
  → Continue cycle normally
```

### 3.4 Inline Research (Fallback Only)

```
FOR each gap (max 3 per cycle):
  1. WebSearch — try first
     → If API error (400): log, proceed to step 2
  2. curl — for specific URLs (GitHub API, docs)
  3. WebFetch — for HTML → Markdown conversion
  4. crawl4ai — last resort for JS-heavy/blocked sites
```

### 3.5 Deep Fetch (Fallback Only)

```
FOR each promising source (max 5 per cycle):
  1. Try curl (fastest, best for raw content)
  2. Try WebFetch (for HTML→Markdown conversion)
  3. Try crawl4ai (for JS-rendered content)
  4. Extract: key claims, entities, concepts, dates
  5. Check if already covered (avoid duplication)
```

### 3.6 Analysis (Fallback Only)

```
FOR each fetched source:
  1. Extract key takeaways (3-5 bullet points)
  2. Identify connections to existing wiki pages
  3. Flag contradictions: > [!contradiction] blockquote
  4. Note: what is genuinely NEW vs. confirming existing knowledge
```

### 3.7 Source Deduplication (Fallback Only)

```
- Check if source URL already in wiki/sources/
- Check if content overlaps > 80% with existing pages
- Skip if duplicate; process only genuinely new sources
```

---

## Step 4 — Ingest

### 4.1 From Subagent Results

```
IF using subagent (Step 3.1 succeeded):
  → Subagent already wrote pages directly
  → Verify pages exist via Glob
  → Update index.md if new pages added
  → Skip to Step 4.4 for cross-reference check
```

### 4.2 From Inline Research (Fallback)

```
FOR each new source:
  1. Create wiki/sources/<slug>.md
  2. Include: title, source URL, date, key takeaways, tags
  3. Add wikilinks to related existing pages
  4. Save raw content to raw/sources/ if not already there
```

### 4.3 Entity/Concept Pages (Inline Fallback)

```
FOR each new entity or concept discovered:
  1. Check if page already exists (glob)
  2. If exists: update with new information (Edit, not Write)
  3. If new: create at wiki/entities/<name>.md or wiki/concepts/<name>.md
  4. Add to index.md if new
```

### 4.4 Update Stale Pages

```
FOR each stale page identified:
  1. Read the page
  2. Add fresh insights from current research
  3. Update the date in frontmatter
  4. Add new wikilinks discovered during research
```

### 4.5 Cross-Reference Update

```
FOR each new or updated page:
  1. Check existing pages that should link to it
  2. Add bidirectional wikilinks
  3. Update index.md if new pages added
```

---

## Step 5 — Sync (CORRECTED Commands)

### 5.1 Update QMD

```
# CORRECT commands (not qmd collection update --all):
qmd update                           # Re-index all collections
qmd embed --max-batch-mb 100        # Refresh embeddings
```

**NOTE:** If any collection has a broken `update-cmd` (e.g., git pull with no remote), clear it first:
```
qmd collection update-cmd <name> ""   # Clear broken update command
```

### 5.2 Verify Index

```
1. Check that all new pages appear in index.md
2. Verify wikilinks are correctly formatted (kebab-case)
3. Report QMD status briefly
```

---

## Step 6 — Report (Accurate Metrics)

### 6.1 Calculate Metrics (FORMULA)

```
Coverage Score = min(entities_documented / 20, 1.0) * 0.4
              + min(concepts_documented / 50, 1.0) * 0.4
              + min(sources_processed / 30, 1.0) * 0.2

Recency Score = min(pages_updated_this_cycle / max(stale_pages, 1), 1.0) * 0.3
              + max(0, 1 - avg_days_since_update / 30) * 0.7

Coherence Score = min(avg_wikilinks_per_page / 3.0, 1.0)

Novelty Score = min(new_unique_insights / 5.0, 1.0)
              (HIGH if > 30% of insights are new, else MEDIUM/LOW)

Total Score = coverage * 0.4 + recency * 0.3 + coherence * 0.2 + novelty * 0.1
```

**Calculate these REAL numbers and save to state.json.**

### 6.2 Log Results

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] autoresearch | CYCLE N — <status>
- Coverage: <before> → <after> (<delta>)
- Sources: <N> processed | <N> new | <N> duplicates
- Pages: <N> created | <N> updated
- Subagents: <N> spawned | <N> succeeded | <N> failed
- Metrics: cov=<cov> rec=<rec> coh=<coh> nov=<nov> total=<total>
- Next priorities: <list>
- Status: running
```

Update `.autoresearch/state.json`:
```json
{
  "cycle": N,
  "total_sources_processed": <updated count>,
  "total_pages_created": <updated count>,
  "total_pages_updated": <updated count>,
  "coverage_score": <real calculated value>,
  "recency_score": <real calculated value>,
  "coherence_score": <real calculated value>,
  "novelty_score": <real calculated value>,
  "last_cycle_at": "<ISO timestamp>",
  "cycle_duration_seconds": <real elapsed seconds>,
  "status": "running",
  "subagents_this_cycle": {
    "spawned": N,
    "succeeded": N,
    "failed": N
  }
}
```

### 6.3 Console Report

```
═══════════════════════════════════════════════
  AUTORESEARCH CYCLE #<N> (<delta from prev>)
═══════════════════════════════════════════════
  Duration:     <X>m <Y>s
  Metric:       <score> (<+/-> <delta>)

  ASSESSMENT:
    Coverage:   <N entities>, <N concepts>, <N sources>
    Gaps:       <top 3 gaps>
    Stale:      <N> pages refreshed
    Coherence:  avg <N> wikilinks/page

  SUBAGENTS: <N> spawned | <N> succeeded | <N> failed
    [1] <GAP_1> → <pages created>
    [2] <GAP_2> → <pages created>
    [3] <GAP_3> → <no output>

  SOURCES: <N> processed (via fallback if subagent failed)
    [1] <title> (<type>)
    ...

  PAGES: <N> created | <N> updated
    <list>

  QMD: <N> docs indexed | <N> embedded this cycle

  CronJob: <ID or "none"> | Next: <in N seconds>

  Human commands:
    "set priority:" → reorder queue
    "skip cycle"   → jump to next
    /autorestatus  → detailed status
    /autorestop    → stop gracefully
═══════════════════════════════════════════════
```

---

## Step 7 — Schedule Next Cycle

**CRITICAL: Use CronCreate to ensure the loop survives Claude Code restarts.**

```
AFTER reporting (Step 6):
  CronCreate with:
    - cron: "*/N * * * *"  (every N minutes based on cycle_pause_seconds)
    - prompt: "Continue AutoResearch loop — run /autoresearch skill, do NOT re-announce startup"
    - recurring: true
    - Returns a cron job ID — SAVE this to state.json as "cron_job_id"
```

**The cron job is the "never stop" mechanism.** Without CronCreate, Claude Code restarts break the loop. With CronCreate, the loop resumes automatically.

**Alternative:** If CronCreate is not available in this context, fall back to:
```
Schedule next cycle in conversation via "wait N seconds then continue"
(less reliable — prefer CronCreate)
```

---

## Human Intervention (Expanded)

| Command | Effect |
|---------|--------|
| `set priority: <topic>` | Reorder queue, CRITICAL priority |
| `skip cycle` | Skip remaining steps, go straight to Step 7 (schedule next) |
| `/autorestatus` | Show detailed status (separate skill) |
| `/autorestop` | Stop gracefully (separate skill) |
| `/autorestart` | Resume or restart (separate skill) |
| `pause autoresearch` | Set status: paused, cancel cron job |
| `stop autoresearch` | Graceful stop |

**To cancel the cron job:**
```
CronList → find the AutoResearch job ID → CronDelete <ID>
```

---

## Context Compaction

After every 10 cycles, the conversation context grows significantly.

**Compaction strategy:**
```
IF cycle > 0 AND cycle % 10 == 0:
  1. Save current state to .autoresearch/state.json (done)
  2. Summarize recent cycles to wiki/log.md (done)
  3. Suggest to human: "Context growing. /autorestop then /autorestart to compact?"
  4. The next CronCreate trigger will start fresh context anyway
```

The CronCreate mechanism makes compaction safe — state is fully persisted between cycles.

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Subagent spawn fails | Log warning, fall back to inline research |
| Subagent times out | Mark as failed, log, continue with other gaps |
| Subagent write fails | Log error, increment errors_this_session, skip gap |
| WebSearch API error (400) | Log "WebSearch unavailable", try curl/WebFetch |
| curl fails | Try WebFetch, then crawl4ai, then skip |
| crawl4ai fails | Log "All fetch methods failed for [URL]", skip source |
| QMD update fails | Retry once; if still fails, skip sync, log warning |
| QMD embed fails | Skip embeddings, log "embed failed, BM25-only mode" |
| Wiki write fails | Check permissions; log error, increment errors_this_session |
| Cycle exceeds 15 minutes | Log warning; force move to next cycle |
| CronCreate fails | Fall back to conversation-based scheduling |
| state.json write fails | Log critical error; do not continue cycle |
| Human interrupts | Save state immediately; cancel cron job |

---

## State File

`.autoresearch/state.json`:
```json
{
  "started_at": "2026-04-14T10:00:00Z",
  "paused_at": null,
  "cycle": 42,
  "total_sources_processed": 156,
  "total_pages_created": 38,
  "total_pages_updated": 74,
  "coverage_score": 0.734,
  "recency_score": 0.82,
  "coherence_score": 0.91,
  "novelty_score": 0.65,
  "status": "running",
  "current_priorities": ["MCP", "skills-system"],
  "pending_gaps": ["subagent-memory", "llm-gateway"],
  "last_cycle_at": "2026-04-14T12:00:00Z",
  "cycle_duration_seconds": 180,
  "cron_job_id": "cron_abc123",
  "errors_this_session": 0,
  "subagents_this_cycle": {
    "spawned": 3,
    "succeeded": 3,
    "failed": 0
  }
}
```

---

## Subagent Configuration

**Researcher subagent:** `.claude/agents/researcher.md`

| Config | Value | Rationale |
|--------|-------|-----------|
| **model** | `sonnet` | Balance capability/cost |
| **tools** | Read, Glob, Grep, Bash, WebSearch, WebFetch, Write, Edit, Agent | Full research + write |
| **skills** | `deepdive`, `crawl4ai` | Deep research capabilities |
| **isolation** | `worktree` | Clean context per invocation |
| **background** | `true` | Non-blocking, parallel execution |
| **effort** | `high` | Thorough research |

**Spawn parameters passed:**
```yaml
Topic: <gap description>
Wiki path: /Users/tri-mac/claude-autoresearch/wiki/
QMD collection: autoresearch-wiki, autoresearch-root
Link style: kebab
Tags: [autoresearch, <category>]
```

---

## Related Skills

| Skill | Role |
|-------|------|
| `deepdive` | One-shot deep research session |
| `autorestatus` | Show current loop status |
| `autorestop` | Gracefully stop the loop |
| `autorestart` | Resume or paused/stopped state |
| `autorelog` | Show activity log |
| `llm-wiki` | Base wiki operations (ingest/query/lint) |

---

## Configuration Examples

### Minimal (Claude Code focused, this project)

```yaml
# .autoresearch/config.yaml
config:
  domain: single
  priorities:
    - Claude Code features
    - MCP servers
    - Skills system
  metric_weights:
    coverage: 0.5
    recency: 0.2
    coherence: 0.2
    novelty: 0.1
  cycle_pause_seconds: 300
  stale_threshold_days: 7
  max_sources_per_cycle: 5
  max_pages_per_cycle: 3
  qmd_collections:
    - autoresearch-wiki
    - autoresearch-root
  use_subagent: true
  subagent_parallel: true
  max_subagents_per_cycle: 3
```

### Extended (Multi-domain)

```yaml
config:
  domain: multi
  priorities: []
  cycle_pause_seconds: 900        # 15 min
  stale_threshold_days: 14
  max_sources_per_cycle: 8
  max_pages_per_cycle: 5
  qmd_collections:
    - autoresearch-wiki
    - general-knowledge
    - domain-specific-vaults
  use_subagent: true
  subagent_parallel: true
  max_subagents_per_cycle: 5
```

---

## Starting the Loop

```
/autoresearch
```

Or in conversation:
```
start the autoresearch loop
run autonomous research on this wiki
never stop researching
```

The skill will initialize, begin cycling, and **schedule itself via CronCreate** so cycles continue even after Claude Code restarts. Say `/autorestop` to stop.
