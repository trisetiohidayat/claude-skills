# Checkpoint & Resume System

Save and restore exact test execution state — current URL, form dirty state, selected rows, and action history — so interrupted test runs can resume without re-running passed tests.

---

## Why Checkpoints Matter

Every test run may be interrupted (network drop, Odoo server restart, manual stop). Without checkpointing, the only option is to restart from the beginning. Checkpoints let you resume from the last successful step.

---

## Checkpoint Strategy

### Save After Each Test Case

Save checkpoint **after** every test case completes (pass or fail), not during execution:

```
After TC-001 passes → save checkpoint
After TC-002 fails  → save checkpoint (with failure record)
Resume → picks up at TC-003
```

### Checkpoint File Format

```json
{
  "checkpoint_name": "sale-functional-test",
  "saved_at": "2026-04-18T10:35:00Z",
  "session_id": "odoo-test-abc123",
  "odoo_url": "http://localhost:8069",
  "credentials": {
    "login": "admin",
    "password": "admin"
  },
  "current_url": "http://localhost:8069/web#action=sale.action_quotations",
  "page_state": {
    "view_type": "kanban",
    "has_form_open": false,
    "selected_rows": [],
    "form_dirty": false,
    "active_modal": null
  },
  "test_progress": {
    "current_test": "TC-003",
    "next_test": "TC-PRIORITY-2-001",
    "completed": ["TC-001", "TC-002"],
    "failed": [{"id": "TC-003", "error": "element not found", "step": 4}],
    "test_script_version": "1.0"
  },
  "storage_state_file": "session_state.json"
}
```

### Save Checkpoint Commands

```bash
# Save full checkpoint (state + test progress)
playwright-cli run-code "async page => {
  const fs = require('fs');
  const state = await page.context().storageState();
  const checkpoint = {
    saved_at: new Date().toISOString(),
    current_url: page.url(),
    page_state: {
      view_type: document.querySelector('.o_kanban_view') ? 'kanban' :
                 document.querySelector('.o_list_view') ? 'list' :
                 document.querySelector('.o_form_view') ? 'form' : 'unknown',
      has_form_open: !!document.querySelector('.o_form_view'),
      selected_rows: [...document.querySelectorAll('tr.o_data_row input:checked')]
        .map(el => el.closest('tr').dataset.id),
      form_dirty: !!document.querySelector('.o_form_dirty'),
      active_modal: document.querySelector('.modal') ? 'modal' : null
    },
    storage_state: state
  };
  fs.writeFileSync('test_checkpoint.json', JSON.stringify(checkpoint, null, 2));
}"

# Save session storage state separately
playwright-cli state-save session_state.json
```

### Restore Checkpoint Commands

```bash
# Step 1: Restore storage state (cookies/session)
playwright-cli state-load session_state.json

# Step 2: Open Odoo
playwright-cli open http://localhost:8069/web

# Step 3: Restore page state from checkpoint
playwright-cli run-code "async page => {
  const fs = require('fs');
  const cp = JSON.parse(fs.readFileSync('test_checkpoint.json'));
  // Navigate to saved URL
  await page.goto(cp.current_url);
  // Restore selected rows if any
  for (const rowId of cp.page_state.selected_rows) {
    await page.click(\`tr.o_data_row[data-id=\"\${rowId}\"] .o_list_record_selector input\`);
  }
}"
```

---

## Checkpoint Naming Convention

Use consistent naming so the system can auto-detect:

| Purpose | Filename pattern | Example |
|---------|-----------------|---------|
| Storage state | `session_state.json` | `sale_session.json` |
| Checkpoint | `test_checkpoint.json` | `sale_checkpoint.json` |
| Test state | `test_state.json` | `sale_test_state.json` |
| Session profile | `*.profile/` | `sale_test.profile/` |

---

## Auto-Detection Pattern

The skill auto-detects checkpoints by checking for these files in the workspace:

```bash
# Auto-detect: check for existing checkpoint
if [ -f "test_checkpoint.json" ]; then
  echo "Checkpoint found — prompting user to resume"
elif [ -f "test_state.json" ]; then
  echo "Test state found — prompting user to resume"
else
  echo "No checkpoint — starting fresh"
fi
```

---

## Session Reconnection

When reconnecting to an existing session:

```bash
# Check if session is still alive
playwright-cli eval "() => typeof odoo !== 'undefined' && odoo.session_info ? 'alive' : 'dead'"

# If session is dead (timeout/logout), re-authenticate
playwright-cli goto http://localhost:8069/web/login
playwright-cli fill '[name="login"]' 'admin'
playwright-cli fill '[name="password"]' 'admin'
playwright-cli click 'button[type="submit"]'
playwright-cli wait-for-url "**/web#"

# Re-save storage state
playwright-cli state-save session_state.json
```

---

## Test Isolation with Named Sessions

For truly isolated test runs (each test gets a fresh browser):

```bash
# Run test suite with isolated session per module
playwright-cli open http://localhost:8069/web --session sale-test-001
# Execute tests...
playwright-cli state-save sale-test-session.json
playwright-cli close  # End session

# Next test run, fresh session
playwright-cli open http://localhost:8069/web --session sale-test-002
```

---

## Integration with Test State File

The `test_state.json` file (used by `odoo-functional-test` skill) complements this:

- **`test_checkpoint.json`** — browser/page state (playwright state)
- **`test_state.json`** — test execution state (test script state)

Both should be saved together after each test case:

```bash
# After each test case:
# 1. Save playwright checkpoint
playwright-cli state-save session_state.json
playwright-cli run-code save_checkpoint.js

# 2. Save test state (test script updates test_state.json)
# (handled by the test script itself)
```

---

## Common Pitfalls

| Pitfall | Why it fails | Fix |
|---------|-------------|-----|
| Saving during form edit | Page redirects on save, state is stale | Save AFTER each test case completes |
| Saving with modal open | Modal state interferes with next test | Close modal before saving |
| Using same session for multiple modules | Cookies clash, wrong user context | Use separate named sessions per module |
| Saving only storage state | Missing URL/page state for navigation | Save both storage state AND checkpoint JSON |
