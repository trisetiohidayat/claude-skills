---
name: autorestatus
description: Show AutoResearch current status and progress. TRIGGER when user says "/autorestatus", "check research status", "research progress", or "autorestart status"
---

# AutoResearch - Status

## Trigger
`/autorestatus` - Show current research status

## Output

Shows:
- Is research running?
- Current module and model
- Current depth level
- Progress: X/608 modules completed
- Gaps found this session
- Verified entries count
- Time elapsed / time limit
- Last checkpoint time

Example output:
```
AutoResearch Status
===================
Running: Yes
Current: stock.picking (stock.quant completed)
Depth Level: 3/4
Progress: 23/608 modules
Gaps Found: 47 (Critical: 5, High: 12)
Verified: 156 entries
Elapsed: 45m / 60m
Last Checkpoint: 5 minutes ago
```