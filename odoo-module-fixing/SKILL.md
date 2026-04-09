---
name: odoo-module-fixing
description: |
  Manual skill - MUST be invoked with /odoo-module-fixing command.
  DO NOT auto-trigger. Only use when user explicitly requests /odoo-module-fixing.

  Fix issues in Odoo custom modules using a team of QA, Analyst, and Developer agents.
  Each agent runs on dedicated port: QA=8143, Analyst=8144, Developer=8145.
  Always confirm business process changes with Analyst before implementing.
  Use stop_after_init after module upgrade.
  CONTINUE ITERATING until no errors exist - testing must pass with ZERO failures.
---

# Odoo Module Fixing Skill

This skill orchestrates a team of 3 agents (QA, Analyst, Developer) to fix issues in Odoo custom modules. Each agent runs on its own dedicated port to avoid conflicts.

## CRITICAL: Error-Free Guarantee

**This skill does NOT stop until all errors are resolved.** The workflow continues in iterations:
- Each iteration: Developer fixes → QA tests → verify results
- If ANY error remains: repeat the iteration
- Maximum iterations: 10 (to prevent infinite loops)
- Success = Module upgrades without error AND all tests pass

## Team Composition

| Agent | Port | Role |
|-------|------|------|
| QA | 8143 | Test verification and validation |
| Analyst | 8144 | Business process analysis and confirmation |
| Developer | 8145 | Code implementation and fixes |

## Workflow

### Step 1: Gather Requirements

Before starting the team, confirm the following parameters:

1. **Module Name**: The custom module to fix (e.g., `roedl_sale_custom`)
2. **Database Target**: Target database (e.g., `roedl`)
3. **Config File**: Odoo config file (e.g., `odoo19.conf`)
4. **Issue Description**: What error or problem is occurring

If any parameter is missing, ask the user to provide it.

### Step 2: Initialize Agent Team

Create the team using TeamCreate with sequential execution:

```
Team Name: odoo-module-fixing-{module_name}
Description: Fixing issues in {module_name} module - CONTINUE UNTIL NO ERRORS
```

### Step 3: Execute Fixing Workflow (ITERATION LOOP)

**Repeat this loop until: Module upgrade passes + All tests pass + No errors**

#### Iteration 1-10:

1. **Start Analyst** (Port 8144)
   - Analyze the issue
   - Determine if business process is involved
   - If business process: get user confirmation
   - Provide guidance to Developer

2. **Start Developer** (Port 8145)
   - Investigate the root cause
   - Implement fixes in the custom module
   - Run module upgrade:
   ```bash
   ./odoo-bin -c {config_file} -d {database} -u {module_name} --stop-after-init
   ```
   - **CRITICAL**: If upgrade fails → analyze error → fix → retry upgrade
   - Report upgrade results

3. **Start QA** (Port 8143)
   - Run comprehensive tests on the module
   - Verify the fix works correctly
   - Test related functionality
   - **CRITICAL**: If ANY test fails → report failure → loop continues

4. **Evaluate Results**:
   - If upgrade failed → Go to next iteration (Developer fixes errors)
   - If tests failed → Go to next iteration (Developer fixes issues)
   - If upgrade passes AND all tests pass → SUCCESS - exit loop

### Step 4: Handle Business Process Confirmation

If the fix involves business processes:

1. Developer identifies the business impact
2. Developer pauses and notifies Analyst
3. Analyst presents the change to user:
   ```
   Business Process Change Detected:
   - [Description of change]

   Does this align with business requirements?
   Please confirm (yes/no) before proceeding.
   ```
4. Wait for user confirmation
5. If confirmed: Developer proceeds
6. If rejected: Report back to team, discuss alternative approaches

### Step 5: Finalize (Only when SUCCESS)

After fix is validated (upgrade passes + tests pass):

1. QA confirms all tests pass with ZERO failures
2. Developer summarizes ALL changes made
3. Analyst confirms business requirements are met
4. Report final summary to user

## Error Handling & Retry Logic

| Scenario | Action |
|----------|--------|
| Module upgrade fails | Developer analyzes error → fixes → retries upgrade |
| Tests fail | Developer identifies failing tests → fixes → QA re-tests |
| Business process rejected | Re-analyze with team → propose new approach |
| Max iterations (10) reached | Report partial progress → ask user for guidance |

## Success Criteria (ALL must be true)

```
✓ Module upgrade completes WITHOUT ERROR
✓ All unit tests pass (ZERO failures)
✓ All integration tests pass (ZERO failures)
✓ No JavaScript console errors
✓ No Python tracebacks in logs
✓ Business process changes confirmed (if applicable)
```

## Output Format

Report should include:
```
# Module Fix Report - FINAL

## Module: {module_name}
## Database: {database}
## Total Iterations: {X}

## Final Status: SUCCESS ✓
- Module upgrades: YES
- All tests pass: YES
- Business confirmed: {yes/no}

## Changes Made:
- [List of all changes across iterations]

## Iteration History:
- Iteration 1: [status] - [notes]
- Iteration 2: [status] - [notes]
...

## Test Results:
- Unit tests: [X] passed, [Y] failed
- Integration tests: [X] passed, [Y] failed
```

If FAILED after max iterations:
```
## Final Status: FAILED (after 10 iterations)
## Progress Made:
- [What was fixed]
- [What remains broken]

## Next Steps:
- Manual intervention required
- Consider different approach
```
