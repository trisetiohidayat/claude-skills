# Odoo Module Migration Skill (Analyze + Write New)

## Invocation Patterns

- `/odoo-module-migration` - Start Odoo module migration workflow
- `/odoo-module-migrate` - Start Odoo module migration workflow
- "migrate module Odoo" - Trigger when user mentions module migration
- "port module Odoo" - Trigger when user mentions porting modules
- "module migration analyze write" - Trigger for new approach

## Description

Use this skill when user wants to migrate Odoo custom modules from one version to another using the analyze-then-write approach.

**Key Differences from Old Approach:**
1. **No file copying** - Modules are analyzed first, then new files are written
2. **Parallel subagents** - Each module analyzed by dedicated subagent
3. **Shared knowledge base** - Breaking changes shared across all subagents
4. **Dependency-aware** - Respects module dependencies and CE/EE deps

**This skill is for MODULE CODE migration only.** For database migration, use the `odoo-db-migration` skill.

## When to Use

- User wants to upgrade Odoo custom modules from version X to version Y
- User wants to port custom modules to newer Odoo version
- Need to migrate 5-10 modules with dependencies
- User prefers analyze-first approach (vs copy + modify)

**Note:** For database migration, use the separate `odoo-db-migration` skill.

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MIGRATION WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STEP 1: GATHER INPUTS                                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Edition type (CE or EE)                                     │  │
│  │ • CE old path, CE new path (if applicable)                   │  │
│  │ • EE old path, EE new path (if EE edition)                   │  │
│  │ • Source version (e.g., 15.0)                                 │  │
│  │ • Target version (e.g., 17.0)                                 │  │
│  │ • Custom modules path                                         │  │
│  │ • Modules to migrate                                          │  │
│  │ • [OPTIONAL] upgrade-report.html path from upgrade.odoo.com   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 1.5: PARSE UPGRADE REPORT (if available)                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Parse upgrade-report.html from upgrade.odoo.com (if exists) │  │
│  │ • Extract errors and categorize                               │  │
│  │ • Map errors to affected modules                               │  │
│  │ • Add to knowledge base as "known issues"                     │  │
│  │ • Output: ./module_migration/upgrade_errors.json              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 2: BUILD KNOWLEDGE BASE                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Run build_knowledge_base.py                                 │  │
│  │ • Load known breaking changes for version pair               │  │
│  │ • Output: ./module_migration/knowledge_base.json             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 3: RESOLVE DEPENDENCIES                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Run resolve_dependencies.py                                │  │
│  │ • Build dependency graph                                      │  │
│  │ • Topological sort for migration order                       │  │
│  │ • Output: ./module_migration/dependency_order.json           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 4: SPAWN PARALLEL SUBAGENTS (per module)                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ FOR EACH MODULE (in parallel):                                │  │
│  │   • Load agents/module_analyzer.md prompt                     │  │
│  │   • Provide: module path, knowledge base, deps               │  │
│  │   • Subagent analyzes and generates migration plan           │  │
│  │   • Output: ./module_migration/plans/<module>.json           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 5: WRITE MIGRATED FILES                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Load agents/write_agent.md prompt                           │  │
│  │ • Provide: all migration plans, dependency order             │  │
│  │ • Create new directory: ./migrated/                            │  │
│  │ • Write new files with modifications applied                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 6: GENERATE SUMMARY                                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Create ./migrated/MIGRATION_SUMMARY.md                      │  │
│  │ • List all changes per module                                  │  │
│  │ • Document any issues or manual reviews needed                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Gather Inputs

**Ask user for:**

```
1. Edition Type:
   - CE (Community Edition) or EE (Enterprise Edition)?

2. Odoo Source Paths (Optional - for deeper analysis):
   a) CE old path: /path/to/odoo-15.0/odoo
   b) CE new path: /path/to/odoo-17.0/odoo
   c) [EE only] EE old path: /path/to/enterprise-15.0
   d) [EE only] EE new path: /path/to/enterprise-17.0

3. Versions:
   - Source: 15.0
   - Target: 17.0

4. Custom Modules:
   - Path: /path/to/custom_modules
   - Modules: [module_a, module_b, module_c]

5. [OPTIONAL] Upgrade Report:
   - Path to upgrade-report.html from upgrade.odoo.com (if available)
   - This helps identify module-specific issues
```

---

## Step 1.5: Parse Upgrade Report (OPTIONAL but RECOMMENDED)

**If user has upgrade-report.html from upgrade.odoo.com, parse it first!**

This adds crucial context about database-level errors that occurred during migration.

```bash
SKILL_DIR=~/.claude/skills/odoo-module-migration
MODULE_MIGRATION_DIR=./module_migration

# Parse upgrade report
python3 $SKILL_DIR/scripts/parse_upgrade_report.py \
    /path/to/upgrade-report.html \
    -o $MODULE_MIGRATION_DIR/upgrade_errors.json \
    --map-modules \
    --modules-path /path/to/custom_modules
```

**What this does:**
1. Parses upgrade-report.html (JSON/HTML/text format)
2. Categorizes errors (missing_table, missing_column, broken_view, etc.)
3. Maps errors to affected modules
4. Outputs: `upgrade_errors.json`

**How to use the parsed errors:**

| Error Category | Module Impact | Action |
|---------------|---------------|--------|
| `missing_module` | Module not found | Check dependencies |
| `broken_view` | View inheritance issue | Fix XML view refs |
| `missing_xmlid` | External ID not found | Check module data |
| `missing_column` | Field not in DB | Skip or add field |
| `missing_table` | Table not in DB | Check model definition |

**Add to knowledge base:**
Merge upgrade errors into the main knowledge base:
```bash
# The errors are now in upgrade_errors.json
# These will guide module subagents to focus on problematic areas
```

---

## Step 2: Build Knowledge Base

```bash
SKILL_DIR=~/.claude/skills/odoo-module-migration
MODULE_MIGRATION_DIR=./module_migration

mkdir -p $MODULE_MIGRATION_DIR

python3 $SKILL_DIR/scripts/build_knowledge_base.py \
    --source 15.0 \
    --target 17.0 \
    --output $MODULE_MIGRATION_DIR/knowledge_base.json
```

**Note:** CE/EE paths are optional. Without them, the script uses built-in known deprecations.

---

## Step 3: Resolve Dependencies

```bash
python3 $SKILL_DIR/scripts/resolve_dependencies.py \
    /path/to/custom_modules \
    --output $MODULE_MIGRATION_DIR/dependency_order.json
```

This determines the migration order based on module dependencies.

---

## Step 4: Spawn Parallel Subagents

**For each module, use the Module Analyzer subagent:**

Read the agent prompt from: `agents/module_analyzer.md`

Spawn a subagent with:
- Module path: /path/to/custom_modules/module_name
- Knowledge base: ./module_migration/knowledge_base.json
- Dependency info: from dependency_order.json

**Run in parallel for all modules.** Each subagent generates a migration plan JSON file.

---

## Step 5: Write Migrated Files

**Use the Write Agent subagent:**

Read the agent prompt from: `agents/write_agent.md`

The Write Agent:
1. Creates `./migrated/` directory
2. Writes modules in dependency order
3. Applies all modifications from migration plans
4. Preserves model names and external IDs

---

## Step 6: Generate Summary

Create `./migrated/MIGRATION_SUMMARY.md`:

```markdown
# Migration Summary

## Modules Migrated
| Module | Status | Files Modified | Notes |
|--------|--------|----------------|-------|
| asb_base | ✅ DONE | 2 | No changes needed |
| asb_sale | ✅ DONE | 5 | Updated @api.multi → @api.model |
| asb_report | ⚠️ REVIEW | 3 | Manual review needed |

## Breaking Changes Applied
- @api.multi → @api.model (3 occurrences)
- fields.date.today → fields.Date.today() (2 occurrences)

## Dependency Order
asb_base → asb_sale → asb_report
```

---

## Output Structure

```
project/
├── custom_modules/          # Original (unchanged)
│   ├── module_a/
│   ├── module_b/
│   └── module_c/
├── module_migration/        # Working directory
│   ├── knowledge_base.json
│   ├── dependency_order.json
│   └── plans/
│       ├── module_a.json
│       ├── module_b.json
│       └── module_c.json
└── migrated/               # NEW - migrated modules
    ├── module_a/
    ├── module_b/
    ├── module_c/
    └── MIGRATION_SUMMARY.md
```

---

## Important Rules

1. **NEVER modify original files** - Always write new files in `migrated/` directory
2. **Preserve model names** - Don't change `_name` in models
3. **Preserve external IDs** - Keep xmlids unchanged
4. **Follow dependency order** - Migrate independent modules first
5. **Use knowledge base** - Apply all breaking changes from knowledge base
6. **This is SYNTAX migration only** - Database comes from upgrade.odoo.com

---

## Critical Checklist: Odoo 15 → 19 Specific Issues (from Roedl Analysis)

**Always check these for v15 → v19 migrations:**

### Module Dependencies - EE Only
| Module | Issue | Fix |
|--------|-------|-----|
| `hr_payroll` | Enterprise Only di Odoo 19 | Gunakan EE atau cari alternatif CE |
| `hr_work_entry_contract_enterprise` | Enterprise Only | Buang dari dependencies jika CE |

### Module Removals
| Module | Issue | Fix |
|--------|-------|-----|
| `hr_contract` | Tidak ada di Odoo 19 | Contract sudah di-merge ke hr module |
| `mail_wizard_invite` | Tidak ada | Gunakan `mail.followers.edit` |

### Method Changes
| Old | New | Notes |
|-----|-----|-------|
| `_onchange_price_subtotal()` | `_onchange_amount()` | Di account.move.line |

### Field Removals
| Model | Field | Alternative |
|-------|-------|-------------|
| `account.analytic.line` | `validated` | Cari field alternatif |

### View References to Check
- `hr_contract.hr_contract_view_form` → TIDAK ADA
- `hr_payroll.hr_salary_rule_form` → EE Only
- `mail.mail_wizard_invite_form` → `mail.mail_followers_edit_form`

### Ondelete Issues
- Many2one fields: Pastikan ondelete parameter ada (bisa dihapus saat migrasi)

### ⛔ ir.actions.act_window view_type (CRITICAL)
| Issue | Fix |
|-------|-----|
| `<field name="view_type">tree</field>` di act_window | HAPUS seluruh field ini di Odoo 17+ |
| Error: "View types not defined" | view_type dihapus dari model sejak Odoo 17 |

**Example Fix:**
```xml
<!-- SALAH - causes error di Odoo 17+ -->
<record id="action_xxx" model="ir.actions.act_window">
    <field name="view_type">tree</field>
    <field name="view_mode">tree,form</field>
</record>

<!-- BENAR -->
<record id="action_xxx" model="ir.actions.act_window">
    <field name="view_mode">list,form</field>
</record>
```

**Catatan:** Ini adalah issue CODE migration, bukan database. OpenUpgrade TIDAK menghandle ini.

---

## ⚠️ PENTING: Database Compatibility Rule

**Sebelum install/upgrade module ke database hasil upgrade:**

### ⛔ JANGAN Ubah _name Model

**_name harus tetap sama dengan versi lama, termasuk typo:**

```python
# SALAH - mengubah _name yang sudah ada di database
_name = 'asb.meeting.room'  # Salah jika asli 'asb.meeeting.room'

# BENAR - tetap sama dengan versi lama
_name = 'asb.meeeting.room'  # Tetap sama persis dengan typo
```

**Gunakan _table jika ingin pointing ke tabel lama:**
```python
_name = 'asb.meeting.room'  # Nama model baru
_table = 'asb_meeeting_room'  # Tapi gunakan tabel lama yang sudah ada
```

### Many2many Fields - Gunakan Kolom yang Sudah Ada

Jika module memiliki Many2many field dengan `relation` table yang sudah ada di database hasil upgrade:

```python
# SALAH - akan error karena kolom tidak cocok
job_ids = fields.Many2many(
    comodel_name='hr.job',
    relation='project_task_hr_job_rel',
    column1='task_id',      # Baru期望 - ERROR jika DB punya 'project_task_id'
    column2='job_id',       # Baru期望 - ERROR jika DB punya 'hr_job_id'
)

# BENAR - Gunakan nama kolom yang sudah ada di database
job_ids = fields.Many2many(
    comodel_name='hr.job',
    relation='project_task_hr_job_rel',
    column1='project_task_id',  # Sesuai database lama
    column2='hr_job_id',       # Sesuai database lama
)
```

**Cara cek kolom di database:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'project_task_hr_job_rel'
ORDER BY column_name;
```

### Model dengan Typo di Nama Tabel

Jika ada typo di nama model lama yang sudah ada di database:

```python
# Database punya tabel: asb_meeeting_room (dengan typo)
# Module baru: asb.meeting.room (nama benar)

# SOLUSI: Gunakan _table untuk pointing ke tabel lama
class MeetingRoomCalendar(models.Model):
    _name = 'asb.meeting.room'
    _table = 'asb_meeeting_room'  # Pakai nama tabel yang sudah ada
```

### Langkah Aman Sebelum Install Module

1. **Cek tabel yang sudah ada:**
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_name LIKE '%custom_%';
   ```

2. **Cek kolom di relation tables:**
   ```sql
   SELECT column_name FROM information_schema.columns
   WHERE table_name = 'relation_table_name';
   ```

3. **Cocokkan dengan module sebelum install:**
   - Many2many: samakan column1/column2
   - Model: gunakan _table jika nama berbeda

4. **JANGAN hapus data** - Migrasikan/pointing saja

---

## Scripts

### build_knowledge_base.py
Builds global knowledge base with breaking changes.

```bash
python3 scripts/build_knowledge_base.py \
    --source 15.0 --target 17.0 \
    --output knowledge_base.json
```

### resolve_dependencies.py
Resolves module dependencies and determines migration order.

```bash
python3 scripts/resolve_dependencies.py /path/to/modules --output deps.json
```

### generate_migration_plan.py
Generates migration plan for a single module (optional - subagents do this).

```bash
python3 scripts/generate_migration_plan.py \
    /path/to/module knowledge_base.json --output plan.json
```

### parse_upgrade_report.py
Parses upgrade report from upgrade.odoo.com to extract errors and map to modules.

```bash
# Basic parsing
python3 scripts/parse_upgrade_report.py /path/to/upgrade-report.html -o errors.json

# Map errors to custom modules
python3 scripts/parse_upgrade_report.py /path/to/upgrade-report.html \
    -o errors.json \
    --map-modules \
    --modules-path /path/to/custom_modules
```

**Output categories:**
- `missing_module` - Module not found
- `broken_view` - View inheritance issue
- `missing_xmlid` - External ID not found
- `missing_column` - Field not in database
- `missing_table` - Table not in database
- `constraint_failed` - Constraint validation failed

---

## Agent Prompts

### agents/module_analyzer.md
Subagent prompt for analyzing individual modules.

### agents/write_agent.md
Subagent prompt for writing migrated files.

---

## Requirements

- Python 3.8+
- Odoo source code (optional for deeper CE/EE analysis)
- Access to module source files
- **odoo-path-resolver** skill untuk dynamically resolve paths

---

## Examples

### Example 1: Basic Migration
User: "Migrate my custom modules from Odoo 15 to 17"

AI:
1. Gathers paths and versions
2. Builds knowledge base
3. Resolves dependencies
4. Spawns parallel subagents for each module
5. Writes migrated files
6. Generates summary

### Example 2: With EE Modules
User: "Port my enterprise modules from 16 to 19"

AI:
1. Gathers CE/EE paths
2. Builds knowledge base with EE differences
3. Resolves dependencies (including EE deps)
4. Spawns subagents with full CE/EE context
5. Writes migrated files

---

## Version Support

Tested for migrations:
- 15.0 → 16.0
- 15.0 → 17.0
- 16.0 → 17.0
- 15.0 → 18.0
- 15.0 → 19.0
- 17.0 → 18.0
- 18.0 → 19.0

---

## Post-Migration: Testing & Installation

**After module code migration, follow these steps:**

### Step 1: Install Modules in Odoo

```bash
# Using Odoo shell
python odoo-bin shell -d <database> --config=/path/to/odoo.conf

# In Odoo shell:
env['ir.module.module'].search([('name', '=', 'module_name')]).button_install()
```

### Step 2: Run TransactionCase Tests

```bash
# Get paths from odoo-path-resolver
from odoo_path_resolver import resolve
paths = resolve()

# Navigate to Odoo directory
cd paths['odoo']['base_path']

# Run tests
python paths['odoo']['bin'] -d paths['database']['name'] -u <module_name> --test-enable --stop-after-init \
    --addons-path="paths['addons']['custom'],paths['addons']['ce'],paths['addons']['ee']"
```

### Step 3: Run HttpCase Tests (Frontend)

```bash
# Get paths from odoo-path-resolver
from odoo_path_resolver import resolve
paths = resolve()

# Run tests
python paths['odoo']['bin'] -d paths['database']['name'] --test-tags=http --test-enable --stop-after-init \
    --addons-path="paths['addons']['custom'],paths['addons']['ce'],paths['addons']['ee']"
```

---

## Migration Results: Roedl Odoo 15 → 19

**Project:** custom_addons_19_new2/roedl
**Date:** 2026-03-11
**Status:** ✅ COMPLETE

### Modules Migrated (10/10)

| Module | Status | TransactionCase | HttpCase | Notes |
|--------|--------|-----------------|----------|-------|
| hr_course | ✅ Installed | 4 | 4 | |
| invoice_merging | ✅ Installed | 4 | 2 | |
| asb_project | ✅ Installed | 5 | 3 | |
| asb_calendar_feature | ✅ Installed | 6 | 2 | FK fix required |
| asft_employee_attribut | ✅ Installed | 15 | 3 | |
| asb_timesheets_invoice | ✅ Installed | 6 | 3 | |
| asb_setting_accounting | ✅ Installed | 7 | 3 | |
| asft_employee_payroll | ✅ Installed | 16 | 5 | EE-only |
| asb_account_reports | ✅ Installed | 4 | 2 | Custom account types disabled |
| asb_project_followers | ✅ Installed | 4 | 2 | Rewritten |

**Total:** 71 TransactionCase tests, all pass ✅

### Latest Test Run (migration_from_upgraded database)

| Test Type | Total | Pass | Error |
|-----------|-------|------|-------|
| TransactionCase | 71 | 71 | 0 |
| HttpCase | 29 | 0 | 29 (login failed) |

**HttpCase Error Cause:** Database has user 'main_user' instead of 'admin' - tests use hardcoded 'admin' credentials

### Key Fixes Applied

| Module | Issue | Fix |
|--------|-------|-----|
| asft_employee_payroll | EE-only deps | Changed to hr_payroll dependency |
| asft_employee_payroll | attrs deprecated | Changed to invisible |
| asft_employee_payroll | tree→list | All XML views converted |
| asb_project_followers | mail.wizard.invite not exist | Rewritten to use project.share.wizard |
| asb_account_reports | account.account.type not exist | Simplified module |
| asb_timesheets_invoice | validated field missing | Added custom field |
| asb_setting_accounting | _onchange_price_subtotal deprecated | Changed to _onchange_amount |

### Documentation Created

| File | Description |
|------|-------------|
| `docs/MIGRATION_TASKLIST.md` | Task list with test status |
| `docs/MIGRATION_ANALYSIS_REPORT.md` | Detailed analysis report |
| `docs/MIGRATION_SUMMARY.md` | Migration summary |
| `docs/TEST_DOCUMENTATION.md` | Test documentation |
| `docs/TEST_DOCUMENTATION_V2.md` | Updated test documentation (2026-03-11) |

### Test Execution Info

| Item | Value |
|------|-------|
| Odoo Version | 19.0 (Enterprise Edition) |
| Database | Use `paths['database']['name']` from odoo-path-resolver |
| Port | Use `paths['server']['http_port']` from odoo-path-resolver |
| Test Run Date | 2026-03-11 |

---

## Post-Upgrade: Manual Action Tasks

**SETELAH upgrade database selesai** (restore dari upgraded.zip), ada **10 kategori manual action tasks** yang perlu dilakukan karena tidak bisa di-handle oleh proses upgrade otomatis.

**Reference file:** `manual_action_task.md` (bundled reference — read when needed)

**Quick summary:**
1. Custom modules (7) — Migrasi atau disable
2. Disabled views (23) — Rekreasi atau hapus
3. Custom financial reports — Rekreasi manual
4. Partner/pricelist cross-company — Reassign
5. Time off allocations (2) — Re-create
6. ir.actions.server field renames — Update
7. Private address handling — Klik "Recycle"
8. Mail alias domain migration — Verify
9. Missing filestore files — Restore jika penting
10. Partner/commercial partner alignment — Evaluate

**IMPORTANT:** Jangan restore ke production sebelum semua manual action tasks selesai di staging!

---

## Common Odoo 19 View Issues (Post-Migration)

### 1. View Type `<tree>` Deprecated

```xml
<!-- OLD (Odoo 16 and below) -->
<tree string="Title">
    <field name="name"/>
</tree>

<!-- NEW (Odoo 17+) -->
<list string="Title">
    <field name="name"/>
</list>
```

### 2. `attrs` Deprecated

```xml
<!-- OLD -->
<field name="name" attrs="{'invisible': [('field', '=', True)]}"/>

<!-- NEW -->
<field name="name" invisible="field"/>
```

### 3. Button states Deprecated

```xml
<!-- OLD -->
<button string="Confirm" states="draft,confirm"/>

<!-- NEW -->
<button string="Confirm" invisible="state in ('done', 'cancel')"/>
```

### 4. view_mode Deprecated

```xml
<!-- OLD -->
<field name="view_mode">tree,form</field>

<!-- NEW -->
<field name="view_mode">list,form</field>
```
