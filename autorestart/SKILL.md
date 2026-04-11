---
name: autorestart
description: |
  AutoResearch system for Odoo 19 vault documentation. TRIGGER when user says:
  - "Start research" or "Begin AutoResearch" or "/autorestart"
  - "Run research on [module]" or "Start /autorestart"
  - "Begin continuous documentation verification"
  - "Research stock module" or similar

  Also handles: /autorestop (stop), /autorestatus (status), /autorelog (logs), /autoverify (verify module)
commands:
  - /autorestart [options] - Start continuous research
  - /autorestop - Stop current research gracefully
  - /autorestop --force - Stop immediately
  - /autorestatus - Show current research status
  - /autorelog [lines=50] - Show recent activity log
  - /autoverify module=X [model=Y] [deep|quick] - Verify specific module
---

# AutoResearch - Start/Stop Autonomous Research

## Options
- `--modules=stock,sale,purchase` - Specific modules to research
- `--mode=deep` - deep (Level 4) | medium (Level 3) | quick (Level 2)
- `--limit=60m` - Time limit (m=minutes, h=hours), e.g. `--limit=60m` or `--limit=2h`
- `--checkpoint=10m` - Save checkpoint every N minutes

## Depth Levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Surface | Basic field/method names and signatures |
| L2 | Context | Field types, defaults, constraints, why it exists |
| L3 | Edge Cases | Cross-model relationships, workflow triggers, failure modes |
| L4 | Historical | Performance implications, overrides, version changes |

Mode mapping:
- `--mode=quick` → L2 (Surface + Context)
- `--mode=medium` → L3 (adds Edge Cases)
- `--mode=deep` → L4 (adds Historical)

## Behavior

### Starting Research (/autorestart)
1. Validate Odoo codebase path (`~/odoo/odoo19/odoo/addons/`)
2. Load backlog to understand pending gaps
3. Determine priority order (dependencies, usage frequency)
4. Initialize checkpoint with run_id and start time
5. Begin research loop on highest priority module

### Research Loop (per module)
For each model in module:
1. **Discover**: Scan code for fields/methods
2. **Verify + Depth (parallel)**:
   - Code vs Doc: Read source, confirm behavior, record line numbers
   - Depth Escalation: Explore L1-L4 questions
3. **Document**: Write verified + deep doc to vault
4. **Update Tracking**: Update verified-status.md, backlog.md
5. **Checkpoint**: If interval reached, save progress

### Stopping Research (/autorestop)
1. Complete current task gracefully
2. Save final checkpoint
3. Log all findings to activity log
4. Update status to "stopped"

### Force Stop (/autorestop --force)
1. Save checkpoint immediately
2. Mark current task as "incomplete"
3. Log "force stopped"
4. On next /autorestart, offer to resume or restart

### Checkpoint Logic
- Save every N minutes (default 10m)
- Save after each module completion
- Save before stop
- Include: run_id, current position, gaps found, verified count

### Resume Logic
- On new `/autorestart`, check for existing checkpoint
- If checkpoint exists with status="running", offer resume
- Load checkpoint and continue from current position

## Output
- Updates: Research-Log/backlog.md, Research-Log/verified-status.md
- Activity: Research-Log/active-run/log.md
- Insights: Research-Log/insights/depth-escalations.md

## Error Handling

| Error | Response |
|-------|----------|
| Odoo path invalid | Flag error, do not start research |
| Checkpoint corrupted | Offer to start fresh or delete checkpoint |
| No checkpoint on resume | Start new research session |
| Time limit parsed as hours | Support both `m` (minutes) and `h` (hours) |

## Verification (/autoverify)

`/autoverify module=stock [model=stock.quant] [deep|quick]`

1. Load module documentation
2. Compare with actual code using verification_engine.py
3. Report discrepancies
4. Update verification status
5. Flag outdated entries
6. Add to backlog if gaps found

## Status (/autorestatus)

Show:
- Is research running?
- Current module and model
- Current depth level
- Progress: X/608 modules completed
- Gaps found this session
- Verified entries count
- Time elapsed / time limit
- Last checkpoint time

## Activity Log (/autorelog)

Show recent activity from Research-Log/active-run/log.md:
- Timeline of research actions
- Findings at each checkpoint
- Errors encountered
- Gaps discovered
- Depth escalations completed