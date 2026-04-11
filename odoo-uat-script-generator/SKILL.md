---
name: odoo-uat-script-generator
description: Generate comprehensive UAT (User Acceptance Testing) scripts for Odoo modules. Use whenever user asks to create UAT test scenarios, test cases for Odoo, UAT guide, testing script for Odoo module, or anything related to UAT documentation. This skill discovers all menu items, sub-menus, and features directly from the running Odoo database, then generates structured test cases with proper step numbering, priorities, and pre-conditions. Works for any Odoo project — auto-detects database, version, installed modules, and menu structure.
---

# Odoo UAT Script Generator

## Overview

Generate comprehensive UAT (User Acceptance Testing) scripts for Odoo by discovering menu hierarchies directly from the running database, then writing structured test case files.

### What This Skill Does

1. **Detects environment** — finds Odoo config, database, version, running instance
2. **Discovers menus** — queries `ir.ui.menu` to get complete menu tree with all sub-items
3. **Generates test cases** — creates structured TC per menu item with numbered steps
4. **Writes section files** — outputs markdown files organized by Priority Testing Order
5. **Updates README/SIGN-OFF** — keeps documentation in sync with actual TC counts

### When to Use

**Use this skill when:**
- User asks to create UAT test cases for Odoo
- User asks to generate UAT guide, testing script, or test scenarios
- User wants to document all features of an Odoo module
- User asks to "test all menus" or "cek semua sub menu"
- User asks to create or update UAT-GUIDE files
- User mentions "test case", "UAT", "user acceptance testing" in context of Odoo

**Don't use for:**
- Writing actual Odoo test code (use `odoo-test-unit` or `odoo-testing-strategy` instead)
- Debugging Odoo errors (use `odoo-debug-tdd` instead)
- Code generation for Odoo modules (use appropriate `odoo19-*` skills)

---

## Environment Detection

### Step 1: Find Odoo Project

Check these locations in order:
1. Current working directory has `odoo*.conf` or `odoo-bin`
2. Subdirectories: `odoo19.0-*`, `odoo15.0-*`, `enterprise-*`
3. Ask user for path if not found

### Step 2: Detect Running Instance

Query MCP (rust-mcp) for running instances:
```
mcp__rust-mcp__odoo_list_models with instance
```
If no instance found, check MCP env file:
```bash
cat ~/.claude/projects/*/odoo-mcp.env 2>/dev/null | grep INSTANCE
```

### Step 3: Get Database Info

From project CLAUDE.md or odoo.conf:
- Database name
- Host/port
- Odoo version (determine from directory name: `odoo19.0-*` → v19, `odoo15.0-*` → v15)
- HTTP port (default: Odoo 19=8133, Odoo 15=8115)

---

## Menu Discovery

### Query ir.ui.menu

Use MCP to get all menu items with hierarchy:

```python
env['ir.ui.menu'].search_read(
    fields=['id', 'name', 'parent_path'],
    domain=[['parent_path', '!=', '']],
    order='parent_path'
)
```

### Build Menu Tree

From flat menu list, build tree structure:
1. Parse `parent_path` (format: `1/2/3/101/` where last ID is the menu itself)
2. Sort by parent_path to get correct hierarchy
3. Display as tree with indentation (`├──`, `│   └──`)

**Example output:**
```
Contacts (id:384)
├── Contacts (id:385)
│   └── [Contact] tabs: Contact, Internal Contact, Address...
└── Configuration (id:386)
    ├── Contact Tags (id:387)
    └── Industries (id:389)
```

### Map Menus to Sections

Organize by Priority Testing Order:

| Priority | Section | Module | Notes |
|----------|---------|--------|-------|
| 1 | S01 | Contacts | Fondasi semua modul |
| 2 | S02 | Employees | Fondasi HR |
| 3 | S03 | Time Off | Bergantung Employees |
| 4 | S04 | Payroll | Bergantung Employees |
| 5 | S05 | Project | Bergantung Employees, Contacts |
| 6 | S06 | Timesheets | Bergantung Project |
| 7 | S07 | Sales | Mid-level dependencies |
| 8 | S08 | Accounting | Paling dependent |

---

## Test Case Generation

### Test Case Template

Use this exact format for every test case:

```markdown
|TC-{PREFIX}-{NNN}|`{Menu Path}` |{Priority}|{Pre-condition}|1. {Step 1}<br>2. {Step 2}<br>3. {Step 3}|{Expected Result}| |☐ |
```

**Columns (in order):**
1. **TC** — ID format: `TC-{PREFIX}-{NNN}` (e.g., TC-CONT-001)
2. **Menu Path** — Backtick-wrapped menu path (e.g., `` `Contacts > Configuration > Contact Tags` ``)
3. **Priority** — High/Medium/Low
4. **Pre-condition** — What must exist before test
5. **Step** — Numbered steps with `<br>` separator (NO arrows, NO pipe separators in step text)
6. **Expected Result** — What should happen
7. **Actual Result** — Empty, filled by tester
8. **Status** — `☐` (checkbox)

### Step Formatting Rules

**CORRECT:**
```
1. Buka sidebar<br>2. Klik **Contacts**<br>3. Klik **Create**
```

**WRONG (NEVER use these):**
```
❌ 1. Buka sidebar → 2. Klik Contacts  (uses arrow)
❌ 1|2|3                                (uses pipe)
❌ 1. Buka sidebar
   2. Klik Contacts                     (uses newline without <br>)
```

### Priority Guidelines

- **High** — Core features: Create, Edit, Delete, View list
- **Medium** — Configuration, filters, exports, imports
- **Low** — Optional features, archive/unarchive, notes

### Test Case Count

Generate minimum **3-5 TCs per menu item**. For complex menus:
- Main menu action: 3-5 TCs (list, create, edit, delete, search)
- Each sub-menu: 2-3 TCs
- Configuration: 1-2 TCs per item
- Tabs/details: 1 TC each

### TC ID Format

| Module | Prefix | Example |
|--------|--------|---------|
| Contacts | CONT | TC-CONT-001 |
| Employees | EMP | TC-EMP-001 |
| Time Off | TOFF | TC-TOFF-001 |
| Payroll | PAY | TC-PAY-001 |
| Project | PROJ | TC-PROJ-001 |
| Timesheets | TIME | TC-TIME-001 |
| Sales | SALES | TC-SALES-001 |
| Accounting | ACC | TC-ACC-001 |

---

## File Structure

### Section File Template

```markdown
# UAT Test Scenarios - S{NN}: {Module Name}

**Menu Path:** `{Main Menu}`
**Database:** `{db_name}`
**URL:** `http://localhost:{port}`

---

## Sub-Menu Structure

```
{Menu Tree from ir.ui.menu query}
```

---

## Test Cases

| TC | Menu Path | Priority | Pre-condition | Step | Expected Result | Actual Result | Status |
|----|-----------|----------|---------------|------|-----------------|---------------|--------|
{Test Cases}
---

**Total: {NNN} Test Cases**
**Pass: ____ | Fail: ____**
```

### README Update

After generating sections, update README.md:
1. Update Ringkasan Menu Utama table with section mapping
2. Update Priority Testing Order with correct section names
3. Update Sign-Off Summary with correct TC counts
4. Update total: sum all section TCs

### SIGN-OFF Update

Update SIGN-OFF.md:
1. Ringkasan Hasil UAT table — correct section order and TC counts
2. Category Sign-Off sections — match new section order
3. Grand total — sum of all TCs

---

## Writing Files

### Output Directory

For Odoo project at `/Users/tri-mac/project/{project}/`:
```
UAT-GUIDE-2026/
├── README.md
├── SIGN-OFF.md
└── sections/
    ├── S01-CONTACTS.md
    ├── S02-EMPLOYEES.md
    ├── S03-TIME-OFF.md
    ├── S04-PAYROLL.md
    ├── S05-PROJECT.md
    ├── S06-TIMESHEETS.md
    ├── S07-SALES.md
    └── S08-ACCOUNTING.md
```

Create directory if not exists:
```bash
mkdir -p /path/to/UAT-GUIDE-2026/sections
```

### Git Workflow

After writing files:
1. `git add sections/ README.md SIGN-OFF.md`
2. `git commit -m "Descriptive commit message"`
3. Push using token workaround if gh auth fails:
   ```bash
   gh auth token | read token
   git push https://x-access-token:${token}@github.com/{user}/{repo}.git main
   ```

---

## Verification Checklist

Before declaring complete, verify:

- [ ] All ir.ui.menu items are covered (no sub-menu missing)
- [ ] TC IDs are sequential (001, 002, ... no gaps)
- [ ] Steps use numbered format with `<br>` (no arrows, no pipes)
- [ ] Table columns align with header (7 data columns + 1 for TC ID)
- [ ] README Priority Testing Order matches section filenames
- [ ] Section titles inside files match filenames
- [ ] SIGN-OFF section order matches Priority Testing Order
- [ ] Grand total TCs = sum of all section TCs
- [ ] Files committed and pushed to GitHub

---

## Example: Complete S01-Contacts

```markdown
# UAT Test Scenarios - S01: Contacts

**Menu Path:** `Contacts`
**Database:** `roedl_upgraded_20260331`
**URL:** `http://localhost:8133`

---

## Sub-Menu Structure

```
Contacts (id:384)
├── Contacts (id:385)
│   └── [Contact] tabs: Contact, Internal Contact, Address & Contact...
└── Configuration (id:386)
    ├── Contact Tags (id:387)
    ├── Industries (id:389)
    └── Localization (id:390)
        ├── Countries (id:391)
        ├── Country Group (id:392)
        └── Fed. States (id:393)
```

---

## Test Cases

| TC | Menu Path | Priority | Pre-condition | Step | Expected Result | Actual Result | Status |
|----|-----------|----------|---------------|------|-----------------|---------------|--------|
|TC-CONT-001|`Contacts > Contacts` |High |Login sebagai Admin |1. Buka sidebar<br>2. **Contacts** |List contacts tampil | |☐ |
|TC-CONT-002|`Contacts > Contacts > Create` |High |Login sebagai Admin |1. Buka `Contacts > Contacts`<br>2. Klik **Create**<br>3. Pilih **Individual**<br>4. Isi data<br>5. Klik **Save** |Contact terbuat | |☐ |
...

---

**Total: 35 Test Cases**
**Pass: ____ | Fail: ____**
```
