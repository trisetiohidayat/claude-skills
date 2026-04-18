---
name: odoo-functional-test
description: >
  Comprehensive functional test skill for Odoo modules. Performs module scanning, generates
  prioritized test scripts, executes click-based functional tests with checkpoint/resume
  capability, and reports failures with root cause analysis. Always use this skill when
  the user asks to test an Odoo module functionally, run click tests on a module, create
  functional test scripts, test all features of a module, or resume interrupted tests.
  This skill depends on /playwright-cli-odoo for browser automation. Trigger phrases:
  "test module X", "functional test for [module]", "click test [module]", "jalankan functional test",
  "test semua fitur module", "generate test script for [module]", "lanjutkan test dari checkpoint".
triggers:
  - "test module"
  - "functional test"
  - "click test"
  - "functional testing"
  - "uji fungsional"
  - "jalankan functional test"
  - "generate test script"
  - "lanjutkan test"
  - "resume test"
  - "checkpoint test"
  - "uji semua fitur"
---

# Odoo Functional Test Skill

Comprehensive functional testing framework for Odoo modules. Scans module structure,
generates prioritized test scripts, executes browser-based click tests, and reports
failures with root cause analysis. Supports checkpoint/resume for interrupted test runs.

**Prerequisites:**
- Odoo server running (default: `http://localhost:8069`)
- Playwright CLI (`playwright-cli`) available
- Module path: provide either full path or module name (will search Odoo addons paths)
- Login credentials for Odoo

**Output structure:**
```
workspace/
├── module_scan.json       # Scanned module structure
├── test_script.json      # Generated test script with priorities
├── test_state.json       # Checkpoint state (for resume)
├── results/
│   ├── pass.log          # Passed test cases
│   ├── fail.log           # Failed test cases with details
│   └── summary.json       # Overall test summary
└── test_script.ts         # Generated Playwright test script
```

---

## Phase 1: Module Scanning

### 1.1 Locate Module

Accept module in two forms:

1. **Module name** (e.g., `sale`, `stock_account`, `custom_module`)
2. **Full path** (e.g., `/path/to/addons/sale`)

If module name provided, resolve via Odoo environment:
```bash
# Use odoo-path-resolver to find module path
odoo-path-resolver find <module_name>
```

### 1.2 Scan Module Structure

Read and analyze the module:

```bash
# List all files in the module
ls -la <module_path>/

# Read model files (.py)
find <module_path>/models -name "*.py" 2>/dev/null | head -20

# Read view files (.xml)
find <module_path>/views -name "*.xml" 2>/dev/null | head -30

# Read security files
ls <module_path>/security/ 2>/dev/null

# Read wizard files
find <module_path>/wizards -name "*.py" 2>/dev/null
```

### 1.3 Build Feature Inventory

From the scanned files, extract and catalog every testable feature:

**From Models (`models/*.py`):**
- All model names (e.g., `sale.order`, `stock.picking`)
- All fields with their types (char, int, float, bool, many2one, one2many, many2many, selection)
- Compute methods (`@api.depends`)
- Onchange methods (`@api.onchange`)
- Constrains (`@api.constrains`)
- Override methods (`def write`, `def create`, `def unlink`, `def copy`)
- States/stages defined in selection fields

**From Views (`views/*.xml`):**
- All view types present (form, tree, kanban, pivot, graph, calendar, search)
- All action IDs and names (`<act_window>`)
- All menu items (`<menuitem>`) with xmlid
- All buttons and their contexts (`<button>` tags)
- All field names used in views
- Smart buttons / dashboard widgets

**From Wizards (`wizards/*.py` and `wizards/*.xml`):**
- Wizard models (transient models)
- Wizard fields
- Wizard buttons and actions

**From Security (`security/ir.model.access.csv`):**
- Access control list entries
- Identified permission gaps

### 1.4 Generate Scan Report

Create `module_scan.json`:

```json
{
  "module_name": "sale",
  "module_path": "/path/to/addons/sale",
  "odoo_version": "19",
  "scanned_at": "2026-04-18T10:00:00Z",
  "models": [
    {
      "model_name": "sale.order",
      "model_file": "models/sale_order.py",
      "fields": [
        {"name": "name", "type": "char", "required": true},
        {"name": "partner_id", "type": "many2one", "relation": "res.partner"},
        {"name": "state", "type": "selection", "options": ["draft", "sent", "sale", "done", "cancel"]},
        {"name": "order_line", "type": "one2many", "relation": "sale.order.line"}
      ],
      "methods": ["action_confirm", "action_cancel", "_compute_amount_total"],
      "states": ["draft", "sent", "sale", "done", "cancel"]
    }
  ],
  "views": [
    {
      "view_type": "form",
      "view_id": "sale_order_view_form",
      "model": "sale.order",
      "action_xmlid": "sale.act_window_order_Sol/all_orders",
      "buttons": ["action_confirm", "action_cancel", "action_print"]
    }
  ],
  "menus": [
    {"name": "Sales", "xmlid": "sale.menu_sales", "action": "sale.action_orders"},
    {"name": " Quotations", "xmlid": "sale.menu_sale_quotations", "action": "sale.act_window_order_Sol/quotations"}
  ],
  "wizards": [
    {"model": "sale.order.cancel", "view": "sale.view_order_cancel_form", "fields": ["reason"]}
  ],
  "features": [
    {"feature": "create quotation", "model": "sale.order", "view": "form", "priority": 1},
    {"feature": "confirm quotation to sale order", "model": "sale.order", "action": "action_confirm", "priority": 1},
    {"feature": "cancel order", "model": "sale.order", "action": "action_cancel", "priority": 2},
    {"feature": "add order line product", "model": "sale.order.line", "view": "one2many", "priority": 1},
    {"feature": "set different delivery address", "model": "sale.order", "field": "warehouse_id", "priority": 3}
  ]
}
```

---

## Phase 2: Generate Test Script

### 2.1 Determine Test Priorities

Assign priority levels based on feature criticality:

| Priority | Level | Description | Coverage Target |
|----------|-------|-------------|-----------------|
| 1 | Critical | Core CRUD, main workflow, primary business logic | 100% |
| 2 | High | Secondary workflows, important features | 80% |
| 3 | Medium | Less common operations, edge cases | 60% |
| 4 | Low | Edge cases, advanced features | 40% |

**Priority 1 features always include:**
- Login + navigation to module
- Create new record (primary model)
- Read/edit existing record
- Delete record
- Primary workflow transitions (e.g., Confirm, Approve, Done)

**Priority 2 features include:**
- Search and filtering
- Bulk operations
- Export data
- Secondary workflow transitions
- Wizard interactions

**Priority 3+ features:**
- Inline editing
- Kanban-specific (drag-drop, color)
- Advanced filters, favorites
- Email composer, attachments
- Chatter/notes

### 2.2 Write Test Script JSON

Generate `test_script.json` with ordered test cases:

```json
{
  "module_name": "sale",
  "script_version": "1.0",
  "generated_at": "2026-04-18T10:30:00Z",
  "base_url": "http://localhost:8069",
  "credentials": {
    "login": "admin",
    "password": "admin"
  },
  "test_cases": [
    {
      "id": "TC-001",
      "priority": 1,
      "category": "navigation",
      "feature": "Login and navigate to Sales module",
      "test_steps": [
        {"step": 1, "action": "open", "target": "http://localhost:8069/web/login", "description": "Open Odoo login page"},
        {"step": 2, "action": "fill", "target": "[name=\"login\"]", "value": "admin", "description": "Enter username"},
        {"step": 3, "action": "fill", "target": "[name=\"password\"]", "value": "admin", "description": "Enter password"},
        {"step": 4, "action": "click", "target": "button[type=\"submit\"]", "description": "Click Log in"},
        {"step": 5, "action": "snapshot", "target": ".o_main_navbar", "description": "Verify dashboard loaded"},
        {"step": 6, "action": "click", "target": ".o_menu_toggle", "description": "Open app menu"},
        {"step": 7, "action": "click", "target": ".o_menu_item:has-text(\"Sales\")", "description": "Navigate to Sales"},
        {"step": 8, "action": "snapshot", "target": ".o_kanban_view, .o_list_view", "description": "Verify Sales view loaded"}
      ],
      "expected_result": "Dashboard loaded, Sales menu accessible, Sales view (kanban/list) visible",
      "selectors": {
        "menu_toggle": ".o_menu_toggle",
        "sales_menu": ".o_menu_item:has-text(\"Sales\")",
        "login_field": "[name=\"login\"]",
        "password_field": "[name=\"password\"]"
      }
    },
    {
      "id": "TC-002",
      "priority": 1,
      "category": "create",
      "feature": "Create new quotation",
      "test_steps": [
        {"step": 1, "action": "goto", "target": "http://localhost:8069/web#action=sale.action_quotations", "description": "Navigate to Quotations view"},
        {"step": 2, "action": "snapshot", "target": ".o_list_view, .o_kanban_view", "description": "Verify quotations list"},
        {"step": 3, "action": "click", "target": ".o_list_button_add, .o-kanban-button-new", "description": "Click Create button"},
        {"step": 4, "action": "snapshot", "target": ".o_form_view", "description": "Verify new form opened"},
        {"step": 5, "action": "fill", "target": "[name=\"partner_id\"] input", "value": "Agrolait", "description": "Select customer"},
        {"step": 6, "action": "click", "target": ".o-autocomplete--dropdown-item:has-text(\"Agrolait\")", "description": "Pick customer from dropdown"},
        {"step": 7, "action": "click", "target": ".o_field_one2many .o_list_button_add", "description": "Add order line"},
        {"step": 8, "action": "fill", "target": "[name=\"product_id\"] input", "value": "CPU", "description": "Select product"},
        {"step": 9, "action": "fill", "target": "[name=\"product_uom_qty\"] input", "value": "5", "description": "Enter quantity"},
        {"step": 10, "action": "click", "target": "[data-hotkey=\"s\"]", "description": "Save record"}
      ],
      "expected_result": "Quotation created successfully, record saved with customer and order line",
      "assertions": [
        {"type": "url", "pattern": "view_type=form", "description": "Form view opened after save"},
        {"type": "element", "target": ".o_form_view .o_form_dirty", "exists": false, "description": "Form is clean (saved)"},
        {"type": "text", "target": ".o_notification", "not_contains": "Error", "description": "No error notification"}
      ],
      "selectors": {
        "create_button": ".o_list_button_add",
        "customer_field": "[name=\"partner_id\"] input",
        "order_line_add": ".o_field_one2many .o_list_button_add"
      }
    },
    {
      "id": "TC-003",
      "priority": 1,
      "category": "workflow",
      "feature": "Confirm quotation to Sale Order",
      "depends_on": ["TC-002"],
      "test_steps": [
        {"step": 1, "action": "goto", "target": "http://localhost:8069/web#action=sale.action_quotations", "description": "Navigate to Quotations"},
        {"step": 2, "action": "click", "target": "tr.o_data_row[data-id], .o_kanban_record", "description": "Open existing quotation"},
        {"step": 3, "action": "snapshot", "target": ".o_form_statusbar", "description": "Verify status bar visible"},
        {"step": 4, "action": "click", "target": ".o_form_statusbar .dropdown-toggle", "description": "Open state dropdown"},
        {"step": 5, "action": "click", "target": ".o_dropdown_menu .o_menu_item:has-text(\"Confirm\")", "description": "Click Confirm"},
        {"step": 6, "action": "snapshot", "target": ".o_form_statusbar", "description": "Verify state changed to Sale Order"}
      ],
      "expected_result": "Quotation state changes from Quotation to Sale Order",
      "assertions": [
        {"type": "text", "target": ".o_form_statusbar .o_statusbar_status .active", "contains": "Sale Order", "description": "Status shows Sale Order"}
      ]
    },
    {
      "id": "TC-PRIORITY-2-001",
      "priority": 2,
      "category": "edit",
      "feature": "Edit existing quotation",
      "depends_on": ["TC-002"],
      "test_steps": [...],
      "expected_result": "Changes saved successfully"
    },
    {
      "id": "TC-PRIORITY-2-002",
      "priority": 2,
      "category": "search",
      "feature": "Search and filter quotations",
      "test_steps": [...],
      "expected_result": "Search returns relevant results"
    },
    {
      "id": "TC-PRIORITY-3-001",
      "priority": 3,
      "category": "wizard",
      "feature": "Cancel quotation via wizard",
      "test_steps": [...],
      "expected_result": "Wizard opens, cancellation completes, state changes"
    }
  ],
  "priority_order": [
    {"priority": 1, "label": "Critical", "count": 3},
    {"priority": 2, "label": "High", "count": 2},
    {"priority": 3, "label": "Medium", "count": 1}
  ]
}
```

### 2.3 Generate Playwright Test File

Also generate a `.ts` Playwright test file (`test_script.ts`) for direct execution:

```typescript
import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.ODOO_URL || 'http://localhost:8069';
const LOGIN = process.env.ODOO_LOGIN || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';

async function login(page: Page) {
  await page.goto(`${BASE_URL}/web/login`);
  await page.fill('[name="login"]', LOGIN);
  await page.fill('[name="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL(/.*web#/, { timeout: 10000 });
}

test.describe('Sale Module Functional Tests', () => {

  test('TC-001: Login and navigate to Sales module', async ({ page }) => {
    await login(page);
    await page.click('.o_menu_toggle');
    await page.click('.o_menu_item:has-text("Sales")');
    const view = page.locator('.o_kanban_view, .o_list_view');
    await expect(view).toBeVisible({ timeout: 5000 });
  });

  test('TC-002: Create new quotation', async ({ page }) => {
    await login(page);
    await page.goto(`${BASE_URL}/web#action=sale.action_quotations`);
    await page.click('.o_list_button_add, .o-kanban-button-new');
    await page.fill('[name="partner_id"] input', 'Agrolait');
    await page.click('.o-autocomplete--dropdown-item:has-text("Agrolait")');
    await page.click('.o_field_one2many .o_list_button_add');
    await page.fill('[name="product_id"] input', 'CPU');
    await page.click('[data-hotkey="s"]');
    // Assertions
    await expect(page).toHaveURL(/view_type=form/);
    const error = page.locator('.o_notification:has-text("Error")');
    await expect(error).not.toBeVisible();
  });

  test('TC-003: Confirm quotation to Sale Order', async ({ page }) => {
    await login(page);
    await page.goto(`${BASE_URL}/web#action=sale.action_quotations`);
    const firstRow = page.locator('tr.o_data_row').first();
    if (await firstRow.isVisible()) {
      await firstRow.click();
    } else {
      test.skip('No quotation available');
    }
    await page.click('.o_form_statusbar .dropdown-toggle');
    await page.click('.o_dropdown_menu .o_menu_item:has-text("Confirm")');
    await page.waitForTimeout(500);
    const status = page.locator('.o_form_statusbar .o_statusbar_status .active');
    await expect(status).toContainText('Sale Order');
  });

});
```

---

## Phase 3: Execute Tests (Staged by Priority)

### 3.1 Test Execution Order

Execute tests in strict priority order. Never skip Priority 1 tests even if they pass — always verify. Use checkpointing to save progress after each test case.

### 3.2 Checkpoint Mechanism

**Before executing ANY test:**
1. Check if `test_state.json` exists in the workspace
2. If exists, read `test_state.json` and resume from the last incomplete test case
3. If not exists, start from scratch

**State file format (`test_state.json`):**
```json
{
  "module_name": "sale",
  "test_script_version": "1.0",
  "session_id": "playwright-cli-<session-id>",
  "started_at": "2026-04-18T10:30:00Z",
  "current_test": {
    "id": "TC-003",
    "priority": 1,
    "status": "in_progress",
    "started_at": "2026-04-18T10:35:00Z"
  },
  "completed_tests": [
    {"id": "TC-001", "status": "pass", "finished_at": "2026-04-18T10:31:00Z", "duration_ms": 12400},
    {"id": "TC-002", "status": "pass", "finished_at": "2026-04-18T10:33:00Z", "duration_ms": 18500}
  ],
  "failed_tests": [
    {"id": "TC-003", "status": "fail", "error": "element .o_dropdown_menu not found", "step": 4, "finished_at": "2026-04-18T10:35:30Z"}
  ],
  "resume_from": "TC-004"
}
```

### 3.3 Test Execution Flow

For each test case, follow this exact sequence:

```
STEP 1: Read test case from test_script.json
STEP 2: Update test_state.json → set current_test, status="in_progress"
STEP 3: Login if not already logged in (check session)
STEP 4: Execute each step using playwright-cli
        - For each step, capture output
        - On failure: STOP immediately, go to STEP 5
STEP 5: If all steps passed:
          - Update test_state.json → status="pass"
          - Append to results/pass.log
          - Continue to next test case
        If any step failed:
          - Update test_state.json → status="fail", record error
          - Append to results/fail.log with full context
          - Perform FAILURE ANALYSIS
          - Log suggestion
          - Continue to next test case
STEP 6: Save test_state.json after EVERY test case
```

### 3.4 Failure Analysis

When a test fails, immediately perform root cause analysis:

**Step-level error capture:**
- Which step failed (number and description)
- What action was attempted
- What target/selector was used
- What error was returned

**Root cause classification:**

| Error Type | Cause | Suggestion |
|------------|-------|------------|
| Element not found | Wrong selector, element changed | Snapshot and identify correct selector |
| Element not clickable | Overlay, loading state | Wait for element, retry |
| Form validation error | Required field missing | Check field requirements, add step |
| State transition blocked | Precondition not met | Check model constraints, fix sequence |
| Permission denied | ACL restriction | Login as different user or check access |
| Page timeout | Server slow, large data | Increase wait time |
| JS error in Odoo | Bug in Odoo code | Report JS error, skip test |
| Element already gone | Race condition | Add explicit wait |

**Failure report format:**
```
FAILED TEST: TC-003 - Confirm quotation to Sale Order
Priority: 1 (Critical)
Category: workflow
Failed at: Step 4 - click on statusbar dropdown
Target: .o_form_statusbar .dropdown-toggle

ERROR DETAILS:
- Error message: "locator click: target .o_form_statusbar .dropdown-toggle not found"
- Page state: Form view loaded, status bar present but dropdown not visible
- Possible cause: Status bar state is already "Sale Order" (terminal state), dropdown may not be shown for confirmed orders
- Root cause: Test assumes status is "Quotation", but record may already be in "Sale Order" state

SUGGESTIONS:
1. Before clicking statusbar, verify current state via snapshot
2. Add conditional: if state is already "Sale Order", skip or use different action
3. Alternatively: create a new draft quotation first to ensure correct state

CONCLUSION: Test design issue - depends on record being in "Quotation" state
```

### 3.5 Test Execution Commands

Use `playwright-cli` for all browser interactions:

```bash
# Start a named session for the test run
playwright-cli open http://localhost:8069/web/login --session odoo-functional-test

# Login
playwright-cli fill '[name="login"]' 'admin'
playwright-cli fill '[name="password"]' 'admin'
playwright-cli click 'button[type="submit"]'

# Save session state for reuse
playwright-cli state-save ./workspace/session_state.json

# Navigate to module
playwright-cli goto 'http://localhost:8069/web#action=sale.action_quotations'

# Execute test step
playwright-cli click '.o_list_button_add'

# Snapshot on failure
playwright-cli snapshot

# Handle error - snapshot target area
playwright-cli snapshot --depth=3 '.o_form_statusbar'

# Take screenshot on failure (save to results/)
playwright-cli screenshot ./workspace/results/TC-003-step4.png

# Save state after each test case
playwright-cli state-save ./workspace/session_state.json

# Resume session on next test
playwright-cli state-load ./workspace/session_state.json
playwright-cli goto 'http://localhost:8069/web#action=sale.action_quotations'
```

---

## Phase 4: Report Generation

### 4.1 Per-Test Result Format

**PASS (`results/pass.log`):**
```
[PASS] TC-001 | Login and navigate to Sales | Priority: 1 | Duration: 12400ms
  ✓ All 8 steps completed successfully
  ✓ Form/dashboard loaded correctly
  ✓ No JS errors detected
```

**FAIL (`results/fail.log`):**
```
[FAIL] TC-003 | Confirm quotation to Sale Order | Priority: 1 | Duration: 3450ms
  ✗ Step 4 FAILED: Element .o_form_statusbar .dropdown-toggle not found
  Error: locator click: target not found after 5000ms

  ROOT CAUSE: Status bar state already "Sale Order" — dropdown not rendered for confirmed orders
  AT: Step 4 (click statusbar dropdown)
  WHY: Test assumes record is in "Quotation" state, but depends_on (TC-002) creates record that may auto-confirm or is already confirmed
  SUGGESTION: Add state check before action, or ensure record starts in correct state

  CONTEXT:
  - Page URL: http://localhost:8069/web#id=42&model=sale.order&view_type=form
  - Page title: Sale Order - Odoo
  - Snapshot available: results/snapshots/TC-003-step4.yml
```

### 4.2 Summary Report (`results/summary.json`)

```json
{
  "module_name": "sale",
  "test_script_version": "1.0",
  "tested_at": "2026-04-18T11:00:00Z",
  "total_tests": 6,
  "by_priority": {
    "1": {"total": 3, "passed": 3, "failed": 0, "skipped": 0},
    "2": {"total": 2, "passed": 1, "failed": 1, "skipped": 0},
    "3": {"total": 1, "passed": 0, "failed": 0, "skipped": 1}
  },
  "pass_rate": 0.67,
  "total_duration_ms": 94500,
  "tests": [
    {"id": "TC-001", "priority": 1, "status": "pass", "duration_ms": 12400},
    {"id": "TC-002", "priority": 1, "status": "pass", "duration_ms": 18500},
    {"id": "TC-003", "priority": 1, "status": "fail", "error": "element not found", "root_cause": "status already confirmed"},
    {"id": "TC-PRIORITY-2-001", "priority": 2, "status": "pass", "duration_ms": 8500},
    {"id": "TC-PRIORITY-2-002", "priority": 2, "status": "fail", "error": "search returned 0 results"},
    {"id": "TC-PRIORITY-3-001", "priority": 3, "status": "skipped", "reason": "prerequisite TC-003 failed"}
  ],
  "failure_summary": [
    {
      "test_id": "TC-003",
      "error_type": "element_not_found",
      "root_cause": "Test design issue — depends on record in draft state",
      "suggestion": "Add state check step before workflow action",
      "severity": "medium"
    },
    {
      "test_id": "TC-PRIORITY-2-002",
      "error_type": "no_results",
      "root_cause": "Search term too specific, no matching records",
      "suggestion": "Use a generic search term or ensure test data exists",
      "severity": "low"
    }
  ]
}
```

### 4.3 Human-Readable Summary

Also output a markdown report:

```markdown
# Functional Test Report: Sale Module

**Date:** 2026-04-18
**Odoo Version:** 19
**Total Tests:** 6 | **Passed:** 4 | **Failed:** 2 | **Pass Rate:** 67%

## Priority Summary

| Priority | Description | Total | Pass | Fail | Skip |
|----------|-------------|-------|------|------|------|
| 1 - Critical | Core CRUD & workflows | 3 | 2 | 1 | 0 |
| 2 - High | Secondary features | 2 | 1 | 1 | 0 |
| 3 - Medium | Edge cases | 1 | 0 | 0 | 1 |

## Failed Tests

### TC-003: Confirm quotation to Sale Order
- **Priority:** 1 (Critical)
- **Error at Step:** 4 — Click statusbar dropdown
- **Error Type:** Element not found
- **Root Cause:** Record already in "Sale Order" state — dropdown not rendered for confirmed orders
- **Suggestion:** Add state check step before workflow action
- **Recoverable:** YES — test can be fixed by checking state before action

### TC-PRIORITY-2-002: Search and filter quotations
- **Priority:** 2 (High)
- **Error at Step:** 2 — Enter search term
- **Error Type:** No results found
- **Root Cause:** Search term does not match any existing records
- **Suggestion:** Use more generic search term or ensure test data exists
- **Recoverable:** YES — use known test data values

## Recommendations

1. **Fix TC-003:** Add conditional state check before workflow transition
2. **Improve test data:** Ensure test fixtures are created before Priority 2+ tests run
3. **Add more Priority 1 coverage:** Test all state transitions for sale.order model

## Next Steps

- Fix failed tests and rerun
- Or resume from checkpoint TC-004 using: `odoo-functional-test resume --module sale`
```

---

## Checkpoint File (Persistence Convention)

The checkpoint file MUST be named `test_state.json` and placed in the workspace directory. This file is the single source of truth for test state.

**Detection logic:**
1. On skill invocation, check for `test_state.json` in the working directory
2. If `test_state.json` exists AND `resume_from` field is set, prompt user to resume or start fresh
3. If user says "resume", continue from `resume_from` test ID
4. If user says "start fresh", delete `test_state.json` and begin from TC-001

**Resume confirmation prompt:**
```
Found checkpoint from previous test run:
Module: sale | Script version: 1.0 | Last updated: 2026-04-18T10:35:00Z

Completed: 2/6 tests (TC-001, TC-002)
Failed: 1 test (TC-003 — element not found)
Resume from: TC-004 (Edit existing quotation)

Options:
1. Resume from TC-004 (continue from last checkpoint)
2. Retry failed tests only (TC-003)
3. Start fresh (delete checkpoint, restart from TC-001)
```

---

## Integration with playwright-cli-odoo

This skill uses `/playwright-cli-odoo` as the browser automation engine. Use its selector reference and workflow patterns:

- **Form selectors:** `[data-hotkey="s"]`, `[name="field_name"] input`, `.o_form_button_save`
- **List selectors:** `tr.o_data_row[data-id="N"]`, `.o_list_button_add`
- **Kanban selectors:** `.o_kanban_record[data-id="N"]`, `.o-kanban-button-new`
- **Navigation:** Use direct action URLs for speed (`web#action=module.action_id`)
- **Session management:** Save/restore auth state to avoid repeated logins

Refer to `/playwright-cli-odoo` skill for complete selector reference and workflow patterns.

---

## Suggestions for playwright-cli-odoo Improvement

Based on this skill's requirements, the following improvements would benefit both skills:

### 1. Built-in Checkpoint/Resume Support
Currently `playwright-cli` has no built-in checkpoint mechanism. Improvements:
- Add `playwright-cli checkpoint-save <name>` command to save execution state
- Add `playwright-cli checkpoint-load <name>` to restore state
- Store: current URL, page state, form dirty state, selected rows

### 2. Named Session Management with Auto-Reconnect
- Add `playwright-cli session-list` to show all active sessions
- Add `playwright-cli session-attach <name> --auto-reconnect` to auto-reconnect if session expired
- Current `state-save/state-load` works but requires manual handling

### 3. Odoo-Specific Assertions
Add Odoo-aware assertion commands:
- `playwright-cli odoo-assert-state <expected_state>` — verify state field value
- `playwright-cli odoo-assert-notification <type>` — verify notification appears
- `playwright-cli odoo-assert-readonly <field_name>` — verify field is readonly

### 4. Batch Step Execution
Add a mode to execute a sequence of steps from a JSON file:
```bash
playwright-cli run-steps test_steps.json
```
Where `test_steps.json` contains an array of `{action, target, value}` objects.

### 5. Screenshot on Every Step (Optional)
Add `--screenshot-each` flag to `playwright-cli` that automatically captures screenshots at each step, useful for generating visual test reports.

### 6. Odoo Version Auto-Detection
`playwright-cli` should auto-detect Odoo version from the login page or session info and adapt selectors accordingly (e.g., Odoo 15 vs 17/18 vs 19 differences).

### 7. Better Error Messages
Current error messages could be more specific:
- "element not found" → "element [target] not found within 5000ms. Current visible elements: [list]"
- Add "Did you mean: [suggested_selector]" hints based on partial matches