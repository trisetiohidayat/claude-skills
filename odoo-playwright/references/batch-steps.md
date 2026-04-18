# Batch Step Execution

Execute a sequence of test steps from a JSON file — ideal for replaying recorded flows, running pre-authored test scripts, or automating long sequences without manual command entry.

---

## Command

```bash
playwright-cli run-steps <steps_file.json> [--screenshot-each=<dir>] [--stop-on-fail]
```

---

## Step File Format

```json
[
  {
    "id": "step-1",
    "action": "open",
    "target": "http://localhost:8069/web/login",
    "description": "Open Odoo login page"
  },
  {
    "id": "step-2",
    "action": "fill",
    "target": "[name=\"login\"]",
    "value": "admin",
    "description": "Enter username"
  },
  {
    "id": "step-3",
    "action": "fill",
    "target": "[name=\"password\"]",
    "value": "admin",
    "description": "Enter password"
  },
  {
    "id": "step-4",
    "action": "click",
    "target": "button[type=\"submit\"]",
    "description": "Submit login"
  },
  {
    "id": "step-5",
    "action": "wait-for-url",
    "target": "**/web#",
    "timeout": 10000,
    "description": "Wait for redirect"
  },
  {
    "id": "step-6",
    "action": "goto",
    "target": "http://localhost:8069/web#action=sale.action_quotations",
    "description": "Navigate to Quotations"
  },
  {
    "id": "step-7",
    "action": "snapshot",
    "target": ".o_list_view",
    "description": "Verify list view loaded"
  },
  {
    "id": "step-8",
    "action": "click",
    "target": ".o_list_button_add",
    "description": "Click Create button"
  }
]
```

---

## Supported Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| `open` | `target` (URL) | Navigate to URL, create new page |
| `goto` | `target` (URL) | Navigate to URL in current page |
| `fill` | `target`, `value` | Fill input field |
| `type` | `target`, `value` | Type text character by character |
| `click` | `target` | Click element |
| `dblclick` | `target` | Double-click element |
| `check` | `target` | Check checkbox |
| `uncheck` | `target` | Uncheck checkbox |
| `select` | `target`, `value` | Select option by value |
| `press` | `target`, `key` | Press keyboard key |
| `hover` | `target` | Hover over element |
| `drag` | `source`, `target` | Drag element to target |
| `upload` | `target`, `value` (filepath) | Upload file |
| `snapshot` | `target` (optional) | Take element/page snapshot |
| `screenshot` | `target` (optional, filepath) | Take screenshot |
| `wait-for-selector` | `target`, `timeout` | Wait for element |
| `wait-for-url` | `target`, `timeout` | Wait for URL pattern |
| `wait` | `ms` | Wait milliseconds |
| `eval` | `target` (optional), `script` | Run JS eval |
| `run-code` | `script` | Run async JS code block |
| `assert` | `type`, `expected` | Assert page state |
| `route` | `pattern`, `options` | Mock network route |
| `goto-if` | `condition`, `target` | Conditional goto |

---

## Conditional Steps

```json
[
  {
    "id": "step-1",
    "action": "goto",
    "target": "http://localhost:8069/web#action=sale.action_quotations",
    "description": "Navigate to Quotations"
  },
  {
    "id": "step-2",
    "action": "eval",
    "script": "() => document.querySelectorAll('tr.o_data_row').length > 0",
    "description": "Check if records exist"
  },
  {
    "id": "step-3",
    "action": "click",
    "target": "tr.o_data_row:first-child",
    "description": "Open first record",
    "if": "step-2 === true"
  },
  {
    "id": "step-4",
    "action": "click",
    "target": ".o_list_button_add",
    "description": "Create new if no records",
    "if": "step-2 === false"
  }
]
```

---

## Options

### `--screenshot-each=<dir>`

Capture a screenshot after every step. Useful for generating visual test reports or debugging failures:

```bash
playwright-cli run-steps test_steps.json --screenshot-each=./reports/screenshots/
```

Output: `step-001.png`, `step-002.png`, etc.

### `--stop-on-fail`

Stop execution immediately when a step fails:

```bash
playwright-cli run-steps test_steps.json --stop-on-fail
```

Output at failure point:
```
FAILED at step-5: click '.o_form_statusbar .dropdown-toggle'
Error: element not found after 5000ms
Snapshot saved: ./reports/screenshots/step-005-fail.yml
```

### `--resume-from=<step-id>`

Resume from a specific step (for checkpoint continuation):

```bash
playwright-cli run-steps test_steps.json --resume-from=step-6
```

### `--env-file=<file>`

Load environment variables for credentials and URLs:

```bash
# .env file
ODOO_URL=http://localhost:8069
ODOO_LOGIN=admin
ODOO_PASSWORD=admin

playwright-cli run-steps test_steps.json --env-file=.env
```

Steps can then use `$ODOO_LOGIN`, `$ODOO_PASSWORD`:
```json
[
  {"action": "fill", "target": "[name=\"login\"]", "value": "$ODOO_LOGIN"},
  {"action": "fill", "target": "[name=\"password\"]", "value": "$ODOO_PASSWORD"}
]
```

---

## Generating Steps from playwright-cli Session

While using `playwright-cli` interactively, every action is logged. Export the action log as a steps file:

```bash
# After a session, export actions to JSON
playwright-cli export-steps --output=test_steps.json
```

This creates a `test_steps.json` file ready for `run-steps`.

---

## Integration with odoo-functional-test

The `odoo-functional-test` skill generates `test_script.json` which can be converted to steps format:

```bash
# Convert test script to steps format
playwright-cli convert-steps test_script.json --output=test_steps.json

# Run the steps
playwright-cli run-steps test_steps.json --screenshot-each=./results/screenshots/ --stop-on-fail
```

---

## Output Log Format

```
playwright-cli run-steps test_steps.json

Starting step execution from: test_steps.json
Working directory: ./workspace
Screenshots: ./workspace/screenshots/
Stop on fail: true

[step-1/12] open http://localhost:8069/web/login ............... OK (1.2s)
[step-2/12] fill [name="login"] "admin" ...................... OK (0.3s)
[step-3/12] fill [name="password"] "admin" .................. OK (0.2s)
[step-4/12] click button[type="submit"] ..................... OK (2.1s)
[step-5/12] wait-for-url **/web# ............................ OK (2.0s)
[step-6/12] goto http://localhost:8069/web#action=sale... ... OK (1.8s)
[step-7/12] snapshot .o_list_view .......................... OK (0.4s)
[step-8/12] click .o_list_button_add ....................... OK (0.6s)

FAILED at step-9: fill [name="partner_id"] input "Agrolait"
Error: element [name="partner_id"] input not found after 5000ms
Reason: Field may be inside a One2many or requires focus-first pattern
Suggestion: Try clicking [name="partner_id"] .o_input first

Snapshot saved: ./workspace/screenshots/step-009-fail.yml
Checkpoint saved: ./workspace/test_checkpoint.json

Test run stopped. 8 passed, 1 failed, 3 pending.
```

---

## Step ID Convention

Step IDs are used for checkpoint/resume and conditional logic:

```
<action>-<number>-<descriptor>
login-01-open           → step 1
login-02-fill-user      → step 2
login-03-fill-pass      → step 3
create-01-click-add     → step 4
create-02-fill-customer → step 5
```

The checkpoint file stores `last_completed_step` and `last_failed_step` so `--resume-from` can pick up exactly where it left off.
