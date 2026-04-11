---
name: autorestop
description: Stop AutoResearch running session. TRIGGER when user says "/autorestop", "stop research", "stop autorestart", or "stop the research process"
---

# AutoResearch - Stop

## Trigger
`/autorestop` - Stop current research gracefully
`/autorestop --force` - Stop immediately without saving

## Behavior

### Graceful Stop
1. Complete current model research
2. Save final checkpoint with `stop_requested: true`
3. Log all findings to current run log
4. Update backlog with any new gaps found
5. Update verified-status with new verifications
6. Mark run as "completed" in status.json

### Force Stop
1. Save checkpoint immediately
2. Mark current task as "incomplete"
3. Log "force stopped"
4. On next /autorestart, offer to resume or restart

## Output
- Final checkpoint saved
- Activity log closed
- Status: "stopped" or "force_stopped"