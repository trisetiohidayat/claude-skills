---
name: skill-autoresearch
description: >
  Autonomous skill improvement loop using the AutoResearch concept (inspired by karpathy/autoresearch).
  TRIGGER when user says "/skill-autoresearch", "improve this skill automatically",
  "run autonomous skill research", "skill never stop improving", "auto-improve skill",
  or asks to start the autonomous skill improvement loop on a specific skill.

  This skill takes ONE specific skill path and runs an INDEFINITE improvement loop:
  run evals → calculate score → modify skill → check improvement → repeat.
  Each cycle has a ~5 minute time budget (configurable). Results are logged to TSV
  and visualized in HTML. The loop runs until the human interrupts it.

  USE THIS when:
  - You want a skill to continuously improve via evals without stopping
  - You want evidence-based skill improvement (assertion pass rates, not vibes)
  - You want to find the best version of a skill's instructions
  - You want "never stop improving" behavior for a specific skill

  DO NOT USE THIS when:
  - You want to create a new skill from scratch (use /skill-creator instead)
  - You want to improve ALL skills at once (specify one skill path)
  - You just want a one-shot skill review (use /skill-creator manually)
---

# skill-autoresearch — Autonomous Skill Improvement Loop

## Core Philosophy

> "You are a completely autonomous skill researcher. If you run out of ideas, think harder.
> The loop runs until the human interrupts you, period."
> — adapted from karpathy/autoresearch

This skill applies the **AutoResearch loop** to skill improvement. Instead of training
a neural network, we train a **skill's instructions** via eval-driven experimentation.
The metric is `skill_eval_score`, the loop is time-budgeted, and improvements are kept
while regressions are discarded.

## Concept Comparison

| Aspect | karpathy/autoresearch | skill-autoresearch |
|--------|----------------------|-------------------|
| What improves | GPT model weights | Skill instructions (SKILL.md) |
| Training data | TinyStories text | Eval test cases + assertions |
| Loss metric | val_bpb (bits/byte) | skill_eval_score (0–2) |
| What changes | `train.py` | `SKILL.md` (+scripts/ refs/) |
| Evaluation | Fixed `evaluate_bpb()` | Custom eval harness per skill |
| Output | `results.tsv` | `results.tsv` + `report.html` |

---

## Step 0 — Setup

### 0.1 Get Skill Path

The skill path is passed by the human in one of these ways:

```
/skill-autoresearch odoo19-orm
/skill-autoresearch /path/to/my-skill
improve this skill automatically: my-skill
```

**Resolve the path:**
```
IF path is relative (no /):
  → Skill path = ~/.claude/skills/<path>/SKILL.md
IF path is absolute:
  → Skill path = <path>/SKILL.md
IF no path given:
  → Ask human: "Which skill should I improve? Provide the skill name or path."
```

**Validate skill exists:**
- Check `SKILL.md` exists at resolved path
- Check it has valid frontmatter (name, description)
- If invalid → error and stop

**Set workspace root:**
```
WORKSPACE = ~/.claude/skills/<skill-name>/autoresearch/
```
Each skill gets its own isolated workspace. This makes results portable and comparable.

### 0.2 Initialize Workspace

```
mkdir -p WORKSPACE
mkdir -p WORKSPACE/evals
mkdir -p WORKSPACE/logs
mkdir -p WORKSPACE/reports
```

### 0.3 Load or Initialize State

```
IF WORKSPACE/state.json exists:
  READ state
  IF status == "running":
    → Warn "Loop may already be running"
    → Offer to stop and restart
  IF status in ["paused", "stopped", "completed"]:
    → Offer to resume from cycle N
ELSE:
  → Fresh start
```

**Initialize state.json:**
```json
{
  "skill_path": "/path/to/skill",
  "skill_name": "my-skill",
  "started_at": "2026-04-18T10:00:00Z",
  "cycle": 0,
  "best_score": null,
  "best_commit": null,
  "baseline_score": null,
  "total_evals_run": 0,
  "improvements_kept": 0,
  "improvements_discarded": 0,
  "crashes": 0,
  "status": "running",
  "time_budget_seconds": 300,
  "last_cycle_at": null
}
```

### 0.4 Establish Baseline (Cycle 0)

```
BEFORE modifying anything:
1. Run baseline evals (see Step 2)
2. Calculate baseline skill_eval_score
3. Record in state.json as baseline_score
4. Save baseline state: git commit or cp SKILL.md → SKILL.md.baseline
5. Announce baseline, then begin Loop
```

**If no evals exist for this skill:**
```
→ Check WORKSPACE/evals/ for existing evals.json
→ If none found: create minimal evals.json from skill's instructions
  (extract examples, expected behaviors from SKILL.md)
→ Skill must have at least 1 eval to begin loop
→ If human refuses to create evals: offer to use skill without quantitative
  scoring (just manual review mode)
```

### 0.5 Announce Start

```
════════════════════════════════════════════════════════════
  SKILL-AUTORESEARCH — Autonomous Skill Improvement
════════════════════════════════════════════════════════════
  Skill:        <skill-name>
  Skill path:   <real path>
  Workspace:    <WORKSPACE>

  BASELINE (Cycle 0):
    skill_eval_score:  <score>
    assertion_pass_rate: <N%>
    assertion_coherence: <N%>

  Loop config:
    Time budget:  <N> seconds/cycle
    Max cycles:    unlimited (runs until stopped)

  Workspace:     <WORKSPACE>
  Status:        running

  "You may intervene at any time:
   /skill-autoresearch status  → detailed status
   /skill-autoresearch stop    → stop gracefully
   /skill-autoresearch skip     → skip this cycle
   /skill-autoresearch pause    → pause loop"
════════════════════════════════════════════════════════════
```

---

## Step 1 — Plan Experiment

### 1.1 Gather Information

Before modifying, read:
1. Current `SKILL.md` — full content
2. `WORKSPACE/evals/evals.json` — all test cases and assertions
3. `WORKSPACE/state.json` — current status and best score
4. `WORKSPACE/logs/` — recent cycles (last 5 lines each)
5. Q: Any previous failed assertions that hint at what to fix?

### 1.2 Analyze Failed Assertions

```
For each eval with failed assertions:
  - Read the failed assertion text
  - Read the skill instruction that should have prevented the failure
  - Identify the GAP: what the skill says vs. what it should say
  - Rank gaps by:
    severity = (assertion_weight or 1.0) * frequency
    fix_difficulty = easy/medium/hard (based on how structural the change is)
```

### 1.3 Generate Experiment Ideas

```
PRIORITY 1 — Fix obvious gaps (high severity, easy fix):
  - Missing instructions that directly caused a failed assertion
  - Ambiguous phrasing that caused wrong behavior
  - Missing output format requirements

PRIORITY 2 — Refine existing instructions (medium severity, medium fix):
  - Add examples for edge cases
  - Strengthen weak MUST/SHOULD statements
  - Add progressive disclosure layers

PRIORITY 3 — Structural improvements (low severity, hard fix):
  - Reorganize SKILL.md sections
  - Add bundled scripts to replace repeated work
  - Add references/ for domain-specific content
```

**Each cycle proposes 1-3 experiment ideas**, ranked by expected impact.
Pick the top idea as the experiment for this cycle.

### 1.4 Define Experiment Scope

```
EXPERIMENT TYPES (choose one per cycle):

A. INSTRUCTION_EDIT — Edit SKILL.md body/instructions
   → Change, add, remove, or reorganize markdown content
   → Most common experiment type

B. DESCRIPTION_TWEAK — Edit frontmatter description only
   → Small change, fast to test
   → Useful for fine-tuning triggering behavior

C. BUNDLED_ADD — Add bundled scripts/references
   → Add scripts/ or references/ files to the skill
   → Higher impact but riskier

D. RADICAL_REWRITE — Rewrite entire SKILL.md from scratch
   → Only when baseline is very poor
   → Needs strong justification

Record the experiment type and hypothesis in the cycle log.
```

---

## Step 2 — Execute Experiment

### 2.1 Save Current State (Checkpoint)

```
1. cp SKILL.md SKILL.md.cycle-<N>.backup
2. git add -A && git commit -m "cycle-<N> experiment:<description>" || (if no git: skip)
   → Use git if the skill repo is a git repo, otherwise use file backup
3. Record commit hash in state.json as current_commit
```

### 2.2 Apply Modification

```
Apply the experiment idea from Step 1:
- Read the relevant section of SKILL.md
- Make the targeted change
- Edit SKILL.md (DO NOT rewrite the entire file unless experiment type is RADICAL_REWRITE)
```

### 2.3 Run Evals

**How to run evals (manual subagent approach):**

For each eval in `WORKSPACE/evals/evals.json`:

```
1. Spawn a subagent with:
   - Skill path: <current WORKSPACE skill path>
   - Task: <eval.prompt>
   - Save outputs to: WORKSPACE/evals/cycle-<N>/eval-<id>/output/

2. The subagent follows the skill's instructions and produces outputs

3. Collect outputs
```

**Note:** If subagents are unavailable or too slow for the time budget,
fall back to inline eval — you (the agent) read the SKILL.md and the eval
prompt, then produce the expected output manually. This is less rigorous
but ensures the loop doesn't stall.

### 2.4 Grade Evals

For each eval output, run grading:

```
FOR each assertion in eval.assertions:
  1. Read the assertion text
  2. Read the eval output
  3. Evaluate: passed / failed / unknown
  4. Record evidence for the judgment
  5. For coherence: check if output follows the format/structure required
```

**Grading criteria:**

| Assertion type | How to grade |
|---------------|-------------|
| File exists | Check if output file path exists |
| Content match | Grep/read for expected substring |
| Format match | Check for required sections/structure |
| Tool called | Check subagent transcript for tool name |
| Output quality | Score 1-5, threshold at 3 |
| No crash | Check for error keywords in output |

**Coherence scoring:**
```
For each eval:
  coherence_score = (
    has_required_sections * 0.3 +
    follows_format * 0.3 +
    no_obvious_omissions * 0.4
  )
```

### 2.5 Calculate Cycle Score

```
skill_eval_score = mean(assertion_pass_rate) + mean(assertion_coherence)

Where:
  assertion_pass_rate = (num_passed_assertions / total_assertions) * 1.0
  assertion_coherence = mean(coherence_scores)  (each 0.0 - 1.0)

skill_eval_score range: 0.0 to 2.0
  0.0 = all assertions failed, no coherence
  2.0 = all assertions passed, perfect coherence
```

---

## Step 3 — Evaluate Result

### 3.1 Decision

```
IF skill_eval_score > best_score:
  → KEEP: "improved: <old> → <new>"
  → Update state.json best_score and best_commit
  → Increment improvements_kept
  → Continue to next cycle

IF skill_eval_score == best_score:
  → KEEP if experiment simplified the skill
  → DISCARD if experiment added complexity without improvement
  → Record decision reason

IF skill_eval_score < best_score:
  → DISCARD: "regressed: <old> → <new>"
  → Restore SKILL.md from backup
  → git reset --hard HEAD || cp SKILL.md.cycle-<N>.backup SKILL.md
  → Increment improvements_discarded

IF crash/error:
  → CRASH: skill_eval_score = 0.0
  → Restore SKILL.md from backup
  → Increment crashes
  → Log error details
```

### 3.2 Simplicity Check

```
After a KEEP decision:
  IF old_SKILL_md_lines > new_SKILL_md_lines:
    → Log "simplification win: -<N> lines"
    → This is a bonus positive signal

  IF old_SKILL_md_lines <= new_SKILL_md_lines AND skill_eval_score == best_score:
    → Revert to previous version (simpler is better at equal score)
    → Log "reverted: equal score but more complex"
```

---

## Step 4 — Log Results

### 4.1 Update results.tsv

```
Append to WORKSPACE/results.tsv:
<commit_hash>\t<skill_eval_score>\t<pass_rate>\t<coherence>\t<status>\t<description>\t<cycle>

Example:
a1b2c3d\t1.432\t0.857\t0.575\tkeep\tadd output format section\t12
b2c3d4e\t1.398\t0.800\t0.598\tdiscard\trewrite intro paragraph\t13
c3d4e5f\t0.000\t0.000\t0.000\tcrash\tremoved required frontmatter\t14
```

### 4.2 Update state.json

```json
{
  "cycle": <N>,
  "best_score": <score>,
  "best_commit": "<hash>",
  "total_evals_run": <count>,
  "improvements_kept": <count>,
  "improvements_discarded": <count>,
  "crashes": <count>,
  "last_cycle_at": "<ISO timestamp>",
  "status": "running"
}
```

### 4.3 Append to cycle log

```
## [YYYY-MM-DD HH:MM] CYCLE N — <status>
- Experiment: <type>: <description>
- Score: <score> (baseline: <baseline> | best: <best>)
- Pass rate: <N%> | Coherence: <N%>
- Decision: <keep/discard/crash>
- Reason: <1-2 sentence explanation>
```

---

## Step 5 — Generate HTML Report

### 5.1 Update HTML Report

After each cycle, update `WORKSPACE/reports/report.html`:

**The HTML must include:**

```html
<!-- Required sections -->
<h1>Skill-Autoresearch: <skill-name></h1>

<!-- Score chart (inline SVG or canvas.js) -->
<div id="score-chart">
  <!-- Line chart: skill_eval_score over cycles -->
  <!-- X axis: cycle number -->
  <!-- Y axis: skill_eval_score (0.0 - 2.0) -->
  <!-- Color coding: green=keep, red=discard, black=crash -->
</div>

<!-- Results table -->
<table>
  <thead>
    <tr><th>Cycle</th><th>Score</th><th>Pass%</th><th>Coh%</th><th>Status</th><th>Experiment</th></tr>
  </thead>
  <tbody>
    <!-- One row per cycle from results.tsv -->
  </tbody>
</table>

<!-- Diff viewer (collapsible per cycle) -->
<details>
  <summary>Cycle N: <experiment description></summary>
  <pre><!-- unified diff of SKILL.md changes this cycle --></pre>
</details>

<!-- Best skill_eval_score highlight -->
<div class="best-score">
  Best score: <score> (cycle <N>)
</div>

<!-- Stats summary -->
<div class="stats">
  Total cycles: N | Kept: N | Discarded: N | Crashes: N
  Time budget: <N>s/cycle
</div>
```

**How to generate:**
- Use Python script at `WORKSPACE/generate_report.py` (bundled, see below)
- Run: `python WORKSPACE/generate_report.py`
- Script reads `WORKSPACE/results.tsv` and `WORKSPACE/state.json`
- Outputs `WORKSPACE/reports/report.html`
- If Python unavailable: generate minimal HTML manually inline

**Report auto-refresh:**
Add `<meta http-equiv="refresh" content="30">` to enable 30-second auto-refresh
so human can monitor in browser while loop runs.

---

## Step 6 — Time Budget Check + Loop

### 6.1 Check Elapsed Time

```
IF elapsed_time > time_budget_seconds:
  → Log "cycle exceeded time budget (<elapsed>s > <budget>s), stopping cycle"
  → Restore SKILL.md from backup (incomplete experiment)
  → Continue to next cycle immediately
```

### 6.2 Loop Decision

```
IF status == "running":
  → Log "cycle complete, scheduling next"
  → GOTO Step 1 (Plan next experiment)

IF status in ["paused", "stopped"]:
  → Save state and exit loop

IF status == "force_stopped":
  → Log final summary and exit
```

---

## Human Intervention Commands

| Command | Effect |
|---------|--------|
| `/skill-autoresearch status` | Show detailed cycle stats, best score, recent log |
| `/skill-autoresearch stop` | Stop after current cycle completes |
| `/skill-autoresearch pause` | Pause loop, save state |
| `/skill-autoresearch resume` | Resume from paused state |
| `/skill-autoresearch skip` | Skip current cycle, start next |
| `set priority: <instruction_type>` | Set experiment focus (e.g., "description only") |
| `set time_budget: <N>` | Change time budget per cycle |

---

## Error Handling

| Situation | Response |
|-----------|----------|
| No evals/evals.json found | Create minimal evals.json from SKILL.md content, or ask human |
| Eval subagent fails | Fall back to inline eval (you evaluate manually) |
| SKILL.md write fails | Check permissions, log critical error, stop loop |
| results.tsv write fails | Retry once, then log warning and continue |
| HTML report generation fails | Generate minimal text report, log warning |
| Cycle exceeds time budget | Restore backup, log "incomplete", continue to next cycle |
| All assertions pass (score = 2.0) | Celebrate! Log "optimal reached", offer to stop or fine-tune |
| Human interrupts | Save state immediately, offer to resume later |

---

## Bundled Scripts

### `scripts/generate_report.py`

Generates `WORKSPACE/reports/report.html` from `results.tsv` and `state.json`.

**What it produces:**
- Line chart: `skill_eval_score` over cycles (green=keep, red=discard, orange=crash)
- Experiment log table with commit, score, pass%, coherence%, status, description
- Stats summary: total cycles, kept, discarded, crashes
- Best score highlight
- Auto-refresh every 30 seconds

**Run it:**
```bash
python ~/.claude/skills/skill-autoresearch/scripts/generate_report.py <WORKSPACE>
# e.g.:
python ~/.claude/skills/skill-autoresearch/scripts/generate_report.py ~/.claude/skills/odoo19-orm/autoresearch/
```

**Fallback:** If Python is unavailable, generate minimal HTML inline using Write tool.

---

## State File

`WORKSPACE/state.json`:
```json
{
  "skill_path": "/Users/tri-mac/.claude/skills/my-skill/SKILL.md",
  "skill_name": "my-skill",
  "started_at": "2026-04-18T10:00:00Z",
  "cycle": 12,
  "best_score": 1.432,
  "best_commit": "a1b2c3d",
  "baseline_score": 0.875,
  "total_evals_run": 48,
  "improvements_kept": 7,
  "improvements_discarded": 5,
  "crashes": 0,
  "status": "running",
  "time_budget_seconds": 300,
  "last_cycle_at": "2026-04-18T10:25:00Z"
}
```

---

## Output Files Summary

| File | Purpose |
|------|---------|
| `WORKSPACE/state.json` | Persistent state between cycles |
| `WORKSPACE/results.tsv` | Tab-separated experiment log |
| `WORKSPACE/reports/report.html` | Visual HTML report (auto-refresh) |
| `WORKSPACE/evals/evals.json` | Test cases and assertions |
| `WORKSPACE/logs/cycle-<N>.md` | Detailed per-cycle log |
| `SKILL.md.backup` | Backup before each experiment |

---

## Quick Start

```
/skill-autoresearch odoo19-orm
```

Then watch the HTML report at:
`~/.claude/skills/odoo19-orm/autoresearch/reports/report.html`

---

## Related Skills

| Skill | Role |
|-------|------|
| `skill-creator` | Create new skills, run manual eval iterations |
| `autoresearch` | General knowledge compounding loop |
| `deepdive` | One-shot research session |
