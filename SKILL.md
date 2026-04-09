# Odoo Module Migration Skill

## Invocation Patterns

- `/odoo-module-migration` - Start Odoo module migration workflow
- `/odoo-module-migrate` - Start Odoo module migration workflow
- "migrate module Odoo" - Trigger when user mentions module migration
- "port module Odoo" - Trigger when user mentions porting modules
- "upgrade module Odoo" - Trigger when user mentions module upgrade
- "adjust migration based on upgrade report" - Trigger when user has upgrade results
- "module migration from upgrade.odoo.com" - Trigger when using upgrade.com results

## Description

Use this skill when user wants to migrate Odoo custom modules from one version to another. This skill performs:
1. **Version Comparison** - Analyze old vs new Odoo/Enterprise code to identify breaking changes
2. **Automated Migration** - Use OCA odoo-module-migrator (SYNTAX only)
3. **Knowledge Base Generation** - Generate comprehensive breaking changes documentation
4. **Manual Review Guide** - Create checklist for business process changes

**IMPORTANT: This is SYNTAX migration, not SEMANTIC migration**
- The database comes from upgrade.odoo.com (already migrated)
- Only migrate code SYNTAX to be compatible with new Odoo version
- DO NOT change model names, external IDs, or database structure
- The upgraded database is the source of truth

## When to Use

- User wants to upgrade Odoo custom modules from version X to version Y
- User wants to port custom modules to newer Odoo version (to use with upgraded database)
- User needs to understand how default Odoo behaviors changed between versions

**NOTE**: For database migration, use the `odoo-db-migration` skill instead. This skill focuses only on module code migration.

---

## Database Migration Reference

For database upgrade, use the separate `odoo-db-migration` skill:
- Trigger: `/odoo-db-migration` or "migrate database Odoo"
- This skill handles: dump analysis, upgrade.odoo.com integration, SQL fixes

This skill (`odoo-module-migration`) handles only the module code migration.

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ODOO MODULE MIGRATION WORKFLOW                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 0: CHECK DATABASE MIGRATION STATUS (CRITICAL - ASK FIRST)  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Apakah upgrade.odoo.com sudah dijalankan?                   │  │
│  │ • Path ke hasil upgrade (migration folder)                   │  │
│  │ • Ada upgrade-report.html?                                    │  │
│  │ • Issue apa yang ditemukan?                                   │  │
│  │  → Ini informs module migration                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 1: GATHER INPUT (from user)                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • CE or EE Edition?                                          │  │
│  │ • CE Core + EE paths (if EE)                                 │  │
│  │ • Source version (e.g., 15.0)                                │  │
│  │ • Target version (e.g., 17.0)                                │  │
│  │ • Path ke custom modules                                      │  │
│  │ • List modules to migrate                                     │  │
│  │ • EE dependencies?                                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 1.5: MODEL REPLACEMENT DETECTION (WAJIB - see Section 1.5)   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Parse upgrade.log untuk model yang dihapus                  │  │
│  │ • Cari module yang depend ke model tersebut                  │  │
│  │ • Generate model_migration_checklist.md                       │  │
│  │ • Update _inherit di Python files jika perlu                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 2: VERSION COMPARISON (AI analyzes Odoo code)               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • CE Core + EE code (jika applicable)                        │  │
│  │ • Bandingkan models, fields, methods, workflows             │  │
│  │ • Identifikasi breaking changes                               │  │
│  │ • Generate knowledge base                                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 2B: BUSINESS CONTEXT ANALYSIS (NEW)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Identify custom components (models, fields, methods)      │  │
│  │ • Generate Business Context Questionnaire per module         │  │
│  │ • Document critical business logic                            │  │
│  │ • Create risk assessment matrix                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 3: PER-MODULE MIGRATION (Iterate for each module)           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ FOR EACH MODULE:                                               │  │
│  │   3.1 Analyze module dependencies                            │  │
│  │   3.2 Run odoo-module-migrator for this module                │  │
│  │   3.3 Check for breaking changes                              │  │
│  │   3.4 Generate module-specific fixes                           │  │
│  │   3.5 Create module review checklist                          │  │
│  │   3.6 Mark module as: COMPLETED / NEEDS REVIEW / FAILED      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 4: GENERATE COMPREHENSIVE OUTPUT                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • CLAUDE.md dengan breaking changes spesifik                  │  │
│  │ • Per-module review checklists                                │  │
│  │ • Migration summary (success/failed per module)              │  │
│  │ • Pre/post migration tasks per module                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 5: DATABASE MIGRATION (Use odoo-db-migration skill)          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • For database migration, use /odoo-db-migration skill         │  │
│  │ • Run after all modules are migrated                           │  │
│  │ • This skill handles module code only                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Gather Information (ALWAYS DO THIS FIRST)

**IMPORTANT: Ask user for all required paths BEFORE proceeding. Do not assume paths.**

### CRITICAL: Check Upgrade.odoo.com Results FIRST

**Before asking about CE/EE paths or modules, you MUST ask:**

```
0. Database Migration Status (VERY IMPORTANT - MUST ASK THIS FIRST):
   a) Apakah Anda sudah menjalankan upgrade.odoo.com?
      - Jika BELUM: Saranankan jalankan dulu untuk dapat database upgraded
      - Jika SUDAH: Lanjut ke pertanyaan berikutnya

   b) Path ke hasil upgrade (migration folder):
      - Contoh: /path/to/migration_20260307_113115/
      - Atau: ~/project/porting/migration_20260307_113115/

   c) Apakah ada upgrade-report.html?
      - Jika YA: Kita akan analisis error patterns dari laporan ini
      - Jika TIDAK: Kita akan tetap lakukan migration berdasarkan versi Odoo

   d) Issue apa saja yang ditemukan di database migration?
      - Contoh: Module errors, View errors, External ID errors
      - Ini akan informasikan module migration kita
```

**Why this is critical:**
- Module code migration depends on knowing what database issues exist
- If upgrade.odoo.com has errors, module migration may need adjustments
- Knowing database issues first informs what fields/models changed

---

After confirming upgrade status, then ask:

```
1. Edition Type:
   - CE (Community Edition) or EE (Enterprise Edition)?
   - Jika EE: Apakah menggunakan bundle CE + EE atau full EE?

2. Path Versions (Pisahkan jika CE dan EE berbeda):
   a) Odoo CE Core versi LAMA (mis: /path/to/odoo-15.0/odoo)
   b) Odoo CE Core versi BARU (mis: /path/to/odoo-17.0/odoo)
   c) [JIKA EE] Enterprise addons versi LAMA (mis: /path/to/enterprise-15.0)
   d) [JIKA EE] Enterprise addons versi BARU (mis: /path/to/enterprise-17.0)

3. Source version (mis: 15.0)
4. Target version (mis: 17.0)

5. Custom Modules:
   - Path ke custom modules (mis: /path/to/my_custom_modules)
   - List modules to migrate (e.g., module_a, module_b, module_c)
   - Apakah ada dependency ke Enterprise modules?

6. **TEST TYPE SELECTION (PENTING - TANYAKAN SEBELUM MULAI):**
   ```
   Pilih jenis test yang ingin dijalankan setelah migration:

   a) Syntax Validation (RECOMMENDED - selalu aman)
      - Command: python -m py_compile
      - Hanya cek Python syntax
      - Tidak perlu Odoo running
      - Cocok untuk: Initial check, CI/CD

   b) Module Load Test
      - Command: python -c "import odoo; from odoo import module"
      - Cek apakah module bisa di-import di Odoo environment
      - Memerlukan: Odoo terinstall
      - Cocok untuk: Verifikasi module loadable

   c) Integration Test (FULL TEST)
      - Command: odoo-bin -d <database> -u <module> --test-enable
      - Install/update module di database test
      - Memerlukan: Running Odoo server + test database
      - Cocok untuk: Pre-production verification

   NOTE: bisa pilih lebih dari 1 (a, b, c) atau pilih salah satu
   ```

NOTE: For database migration, use the odoo-db-migration skill after module migration is complete.
```

### CE vs EE Path Clarification

**Community Edition (CE) Only:**
- Satu path saja untuk Odoo core
- Semua addons berasal dari Odoo Community

**Enterprise Edition (EE) - Two Options:**

| Option | CE Path | EE Path |
|--------|---------|---------|
| CE + EE | `/odoo-17.0/odoo` | `/enterprise-17.0` |
| Full EE | (tidak ada) | `/ee-17.0` (semua dalam satu folder) |

**Important:**
- Jika custom module depends pada module EE (seperti `account_enterprise`, `hr_enterprise`), wajib ada path ke EE
- CE dan EE punya struktur direktori berbeda
- Beberapa field/method hanya ada di EE

### Validate Paths Exist

Before proceeding, verify all paths exist:
```bash
ls -la <path_odoo_lama>
ls -la <path_odoo_baru>
ls -la <path_custom_modules>
```

---

### 1.5: Model Replacement Detection (WAJIB - JALANKAN SETIAP KALI)

**CRITICAL: Step ini WAJIB dijalankan untuk setiap migrasi!**

```bash
# AUTO-DETECT: Cari upgrade.log di direktori kerja saat ini
UPGRADE_LOG=$(find . -maxdepth 3 -name "upgrade.log" -type f 2>/dev/null | head -1)

# AUTO-DETECT: Cari custom modules (cek common patterns)
CUSTOM_MODULES=$(find . -maxdepth 4 -type d -name "migrated" -exec dirname {} \; 2>/dev/null | head -1)

# Fallback: gunakan path default jika tidak ketemu
if [ -z "$UPGRADE_LOG" ]; then
    UPGRADE_LOG="./upgrade.log"
fi

if [ -z "$CUSTOM_MODULES" ]; then
    CUSTOM_MODULES="./module_migration/roedl"
fi

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../skills/odoo-module-migration/scripts"

echo "=== Model Replacement Detection ==="
echo "Upgrade Log: $UPGRADE_LOG"
echo "Custom Modules: $CUSTOM_MODULES"

# 1. Parse upgrade.log untuk model yang dihapus
python3 "$SKILL_DIR/parse_upgrade_removals.py" \
    "$UPGRADE_LOG" \
    --modules "$CUSTOM_MODULES" \
    --output /tmp/removed_models.json

# 2. Generate checklist
python3 "$SKILL_DIR/generate_model_checklist.py" \
    --removed-models /tmp/removed_models.json \
    --output ./module_migration/model_migration_checklist.md

echo "=== Model Replacement Detection Selesai ==="
echo "Checklist: ./module_migration/model_migration_checklist.md"
```

**KENAPA INI PENTING:**
- Menemukan model yang dihapus/ditiadakan di versi baru
- Module yang inherit ke model tersebut perlu diupdate
- Include hasil di MIGRATION_STATUS.md bagian "Model Replacement Analysis"

**Jika module meng-inherit model yang sudah dihapus:**
- Cari replacement dari known_deprecations.py
- Update _inherit di Python files
- Update model di XML views

---

## Step 2: Version Comparison

**CRITICAL: Know your CE vs EE paths first!**

Based on Step 1 input, determine which paths to analyze:

| Edition | Old Paths | New Paths |
|---------|-----------|----------|
| CE Only | `/odoo-15.0/odoo` | `/odoo-17.0/odoo` |
| CE + EE | `/odoo-15.0/odoo` + `/enterprise-15.0` | `/odoo-17.0/odoo` + `/enterprise-17.0` |

### 2.1 Analyze Old Version Odoo Code

Read and analyze key files from old Odoo version:

**Community Edition (CE):**
- `odoo/odoo/models.py` - Base models
- `odoo/addons/*/models/*.py` - Module models
- `odoo/addons/*/views/*.xml` - Views
- `odoo/addons/*/security/*.xml` - Security

**Enterprise Edition (EE) - additionally:**
- `enterprise-15.0/*/models/*.py` - EE module models
- `enterprise-15.0/*/views/*.xml` - EE views

### 2.2 Analyze New Version Odoo Code

Read and analyze corresponding files from new Odoo version:
- CE core + EE addons (jika applicable)
- Perhatikan perubahan di EE yang tidak ada di CE

### 2.3 Identify Breaking Changes

Compare and document:
- **Deprecated APIs**: Methods/fields yang sudah tidak ada
- **Renamed modules**: Module yang di-rename di versi baru
- **Changed behaviors**: Default logic yang berubah
- **New requirements**:强制性的 fields/settings di versi baru
- **Removed features**: Fitur yang dihapus

Use script `scripts/compare_odoo_versions.py` for structured comparison:
```bash
python3 scripts/compare_odoo_versions.py <old_odoo_path> <new_odoo_path> <source_ver> <target_ver>
```

---

## Step 2B: Business Context Analysis

**Why this step is critical:**
Many Odoo modules contain **business logic** that cannot be automatically detected and may cause bugs if misunderstood. This step ensures we understand:
- What the module actually does
- Which fields are critical for business
- What custom workflows exist
- What integrations are in place
- What data-specific logic exists

### 2B.1 Identify Custom Components

For each module, analyze and document:

#### 1. Custom Models
- Read all `models/*.py` files
- Identify models with `_inherit` (inherited) or new models (no _inherit)
- Note: model name, fields, methods

#### 2. Custom Fields
- Identify custom fields (fields not from inherited models)
- Note: field types, ondelete behaviors, default values

#### 3. Custom Methods
- Identify methods with decorators:
  - `@api.model` - Model-level methods
  - `@api.depends` - Computed fields
  - `@api.constrains` - Validation constraints
- Note: business logic performed

#### 4. Custom Views
- Read `views/*.xml` files
- Note: custom fields in views, inherited views

#### 5. Custom Wizards
- Read `wizards/*.py` and `wizards/*.xml`
- Note: wizard flows that might be affected

### 2B.2 Generate Business Context Questionnaire

For each module, generate questions for the user/developer:

```
## Module: <module_name>

### Questions for Developer:

1. **Purpose**: What is the main purpose of this module?
   Answer: _______________

2. **Critical Fields**: Which fields are critical for business operations?
   - Field: ______ | Reason: ___________

3. **Custom Logic**: Which methods contain important business logic?
   - Method: ______ | Purpose: ___________

4. **Integrations**: Does this module connect to third-party services?
   - API: ______ | Purpose: ___________

5. **Data Dependencies**: Are there specific data that must be migrated?
   - Data: ______ | Notes: ___________

6. **Workflow Changes**: Are there workflows that need manual review?
   - Workflow: ______ | Notes: ___________
```

### 2B.3 Document Business Context

Create `business_context.md` per module:

```markdown
# Business Context: <module_name>

## Overview
[User input: Module purpose]

## Critical Components

| Component | Type | Business Impact |
|-----------|------|----------------|
| model_name | Model | Description |
| field_name | Field | Why it's critical |

## Breaking Changes Risk

| Item | Risk Level | Notes |
|------|------------|-------|
| custom_method | HIGH | Specific business logic |
| custom_field | MEDIUM | Check behavior after migration |

## Migration Checklist

- [ ] Verify field X behavior
- [ ] Test method Y after migration
- [ ] Review integration Z
```

### 2B.4 Risk Assessment Matrix

Generate automatic risk assessment:

| Business Area | Risk | Mitigation |
|---------------|------|------------|
| Custom fields | MEDIUM | Review checklist |
| Business methods | HIGH | Manual testing required |
| Third-party API | HIGH | Verify after migration |
| Reports | MEDIUM | Test output |
| Wizards | MEDIUM | Test workflow |

### 2B.5 Integration with Live Database Analysis

**Optional: Use odoo-business-process skill when:**
- User has live database access
- Need to understand actual data flows
- Want to compare old vs new behavior
- Need to identify which records use custom fields

Use command: `/odoo-business-process` - Understand and analyze Odoo business processes thoroughly

### 2B.6 Analyzing upgrade.odoo.com Results (Adaptive Approach)

Instead of specific SQL fixes, learn to analyze upgrade logs to identify patterns:

#### Error Categories to Look For

From real upgrade logs, these categories typically appear:

| Category | How to Detect | Where Found |
|----------|---------------|-------------|
| **Module Errors** | "modules are not loaded" or "dependencies or manifest may be missing" | upgrade.log |
| **View Errors** | "Element cannot be located in parent view" or XPath errors | upgrade.log |
| **External ID Errors** | "External ID not found" or "Missing model" | upgrade.log |
| **Database Errors** | "UniqueViolation" or constraint errors | upgrade.log |
| **Filestore Errors** | "FileNotFoundError" for filestore | upgrade.log |

#### Adaptive Analysis Steps

**1. Parse upgrade.log for ERROR patterns:**
```
grep -E "ERROR|Error" upgrade.log | head -50
```

**2. Identify View IDs with XPath errors:**
```
grep "cannot be located in parent view" upgrade.log
```
→ Extract view IDs → Deactivate or fix views

**3. Find missing modules:**
```
grep "modules are not loaded" upgrade.log
```
→ Extract module names → Mark for uninstall or migration

**4. Find broken External IDs:**
```
grep "External ID not found" upgrade.log
```
→ Check ir_model_data → NULL references or remove XMLID

#### Key Sections in upgrade-report.html

The HTML report contains structured information:

1. **Partners** - Partner/company assignments changed
2. **Pricelists** - Pricelist assignments unassigned
3. **Merged Records** - Groups merged
4. **Disabled views** - Custom views disabled (NEEDS MANUAL REVIEW)
5. **Overridden views** - Standard views restored
6. **Fields renamed** - Fields that need updates in custom code
7. **Private Addresses Removal** - Data moved to hr.employee

#### Version-Specific Field Changes

| Target Version | Field Changes |
|----------------|---------------|
| Odoo 16→17 | `type` → `detailed_type`, `ref` → `memo`, `phone` → `private_phone` |
| Odoo 17→18 | Similar patterns continue |
| Odoo 18→19 | `phone` → `user_id.phone` |

#### Reference Files Location

Example files to study patterns (NOT to copy):

```
migration_YYYYMMDD_HHMMSS/
├── upgrade.log              # Detailed error log - ANALYZE THIS
├── upgrade-report.html      # HTML report with summary
├── upgrade_logs/run_001/
│   ├── upgrade.log         # Per-attempt log
│   └── changes.md         # Summary of changes
├── fix_*.sql              # Generated fixes (study patterns only)
└── dump_*.sql            # Database dumps
```

**How to use:**
1. Run upgrade.odoo.com on test mode
2. Analyze `upgrade.log` for ERROR patterns
3. Categorize errors using the table above
4. Create adaptive fixes based on error categories
5. Apply fixes and re-run

---

## Step 3: Per-Module Migration

**IMPORTANT**: Process each module independently. For each module, complete all sub-steps before moving to the next module.

### 3.0: Generate MIGRATION_STATUS.md (AUTO - WAJIB)

**SEBELUM memulai migration, wajib generate MIGRATION_STATUS.md:**

```bash
# Generate initial MIGRATION_STATUS.md
python3 scripts/generate_migration_status.py \
    --source-version 15.0 \
    --target-version 17.0 \
    --modules module_a,module_b,module_c \
    --test-type syntax,load,integration \
    --output ./module_migration/MIGRATION_STATUS.md
```

**Script ini akan:**
1. Create `MIGRATION_STATUS.md` dengan template lengkap
2. Calculate dependency levels untuk setiap module
3. Generate urutan migration berdasarkan dependencies
4. Siapkan template untuk tracking progress

**SETELAH setap module selesai, UPDATE MIGRATION_STATUS.md:**
```bash
python3 scripts/generate_migration_status.py \
    --update \
    --module module_a \
    --status DONE \
    --changes "models: 2 files, views: 1 file" \
    --test-result PASSED \
    --output ./module_migration/MIGRATION_STATUS.md
```

### CRITICAL: Don't Change Custom Model Names

**This is the most important rule in module code migration:**

When migrating custom modules to be used with the upgraded database from upgrade.odoo.com:

1. **DO NOT change `_name` of custom models** - The database already has records using these model names
2. **DO NOT change database table names** - Data already exists in these tables
3. **Only migrate SYNTAX, not SEMANTICS** - Update API calls, decorators, field definitions to new Odoo syntax
4. **Preserve External IDs** - Keep module names and external IDs unchanged

**Why:**
- The upgraded database from upgrade.odoo.com already contains all custom model definitions
- Changing model names would break the link between code and database data
- Only update the code syntax to be compatible with the new Odoo version

**What to migrate:**
- `@api.multi` → `@api.model` (if needed)
- `fields.` → new field definitions
- Old API → New API
- XML view architecture updates

**What NOT to change:**
- `_name` values
- Model inheritance that defines the actual model
- External IDs (xmlids)

### Maintaining Module Context (IMPORTANT)

**Agent Context Management Strategy:**

During migration, the agent must maintain **separate context per module** to avoid confusion:

#### 1. Module Isolation Principle

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT: module_a (FOCUS ONLY ON THIS)                         │
│  - Read files for module_a only                                │
│  - Check dependencies: module_a depends on base, sale          │
│  - Track changes: what was modified in module_a                 │
│  - Generate output: changes.md for module_a                    │
│  - THEN move to next module                                     │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. Dependency Tracking

For each module, explicitly track:

```markdown
## Current Module Context: <module_name>

### Dependencies (MUST resolve first)
- Direct: [list of modules this depends on]
- Indirect: [modules that depend on this]

### Files in Scope
- models/<module_name>.py
- views/<module_name>.xml
- [etc]

### Changes Made
- [specific changes for THIS module only]

### What NOT in Scope
- Other modules' code
- Modules that depend on this (handle later)
```

#### 3. Migration Order

**Process modules in dependency order:**
```
Level 0: No dependencies on custom modules (base, sale, etc)
   ↓
Level 1: Depends on Level 0
   ↓
Level 2: Depends on Level 1
   ↓
...
```

**Example:**
| Level | Module | Dependencies |
|-------|--------|-------------|
| 0 | asb_base | - |
| 1 | asb_sale | asb_base |
| 2 | asb_report | asb_sale |

#### 4. Context Switch Protocol

When switching between modules:

1. **Complete** current module first (generate changes.md)
2. **Save** current module context
3. **Load** next module context
4. **Verify** dependency resolution

#### 5. What to Record Per Module

In `changes.md` for each module:
- Files modified
- Breaking changes found
- Dependencies on other custom modules
- Custom modules that depend on this
- Testing requirements
- Issues found and resolutions

### 3.1 Identify Module Dependencies

For each module to migrate:
1. Read `__manifest__.py` (or `__openerp__.py`) to get dependencies
2. Identify which modules need to be migrated first
3. Create migration order (dependencies first)

### 3.2 Migrate One Module at a Time

For each module in dependency order:

```
┌─────────────────────────────────────────────────────────────────┐
│ MODULE: <module_name>                                          │
├─────────────────────────────────────────────────────────────────┤
│ 3.2.1 Analyze module structure                                 │
│     - Read models/*.py                                         │
│     - Read views/*.xml                                         │
│     - Read security/*.xml                                       │
│     - Read wizards/                                             │
├─────────────────────────────────────────────────────────────────┤
│ 3.2.2 Run odoo-module-migrator for this module                 │
│     - cd <module_path>                                          │
│     - odoo-module-migrate -d ./ --init-version-name <source>   │
│                                                                  │
│     If single module migration fails, try manual approach:     │
│     - Use odoo19-migrate-model skill for model migration        │
│     - Use odoo19-migrate-view skill for view migration         │
├─────────────────────────────────────────────────────────────────┤
│ 3.2.3 Check for breaking changes                               │
│     - Compare with Odoo version comparison from Step 2          │
│     - Identify deprecated APIs used in this module             │
│     - Note fields that need manual migration                   │
├─────────────────────────────────────────────────────────────────┤
│ 3.2.4 Generate module-specific fixes                           │
│     - Fix deprecated @api.multi → @api.model                  │
│     - Fix renamed fields                                        │
│     - Fix removed methods                                       │
│     - Update __manifest__.py for new version                   │
├─────────────────────────────────────────────────────────────────┤
│ 3.2.5 Create module review checklist                           │
│     - Document fields requiring manual review                  │
│     - Document business logic changes needed                    │
│     - Document views needing update                             │
│     - Document tests needing review                             │
├─────────────────────────────────────────────────────────────────┤
│ 3.2.6 Mark module status                                        │
│     - COMPLETED: Migration successful, no manual changes      │
│     - NEEDS REVIEW: Migration done, manual review required     │
│     - FAILED: Migration failed, needs investigation             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Migration Progress Tracking

**IMPORTANT: Create a tracking file for each migration session**

Create `MIGRATION_STATUS.md` to track progress:

```markdown
# Migration Status: <project_name>
- **Source Version:** Odoo <X.0>
- **Target Version:** Odoo <Y.0>
- **Date Started:** YYYY-MM-DD
- **Current Module:** [module_name - focus only on this]

## Dependency Graph (Level-based)

```
Level 0 (no custom deps): [module_a, module_b]
Level 1 (depends on L0):  [module_c, module_d]
Level 2 (depends on L1):  [module_e]
...
```

## Progress

| # | Module | Level | Dependencies | Custom Deps | Status | Changes | Testing |
|---|--------|-------|-------------|-------------|--------|---------|---------|
| 1 | module_a | 0 | base | - | ✅ DONE | views, models | ⏳ |
| 2 | module_b | 0 | base | - | ✅ DONE | models only | ⏳ |
| 3 | module_c | 1 | base,module_a | module_a | 🔄 IN PROGRESS | - | - |
| 4 | module_d | 1 | base,module_b | module_b | ⏳ PENDING | - | - |
| 5 | module_e | 2 | module_c | module_c | ⏳ PENDING | - | - |

## Current Context: module_c

### Focus (ONLY this module):
- Files: models/module_c.py, views/module_c.xml
- Dependencies to resolve: base, module_a
- Must wait: module_d, module_e

### module_c Status: IN PROGRESS
- **Depends On:** [base, module_a] - MUST be done first
- **Depended By:** [module_e] - handle later
- **Files Changed:** X files
  - models/module_c.py: [specific changes]
  - views/module_c.xml: [specific changes]
- **Breaking Changes:** [list]
- **Testing Required:**
  - [ ] Test X
  - [ ] Test Y

## Module Details (Completed)

### module_a (DONE - Level 0)
- **Depends On:** [base]
- **Depended By:** [module_c]
- **Files Changed:** 3 files
- **Summary:** [brief summary]

### module_b (DONE - Level 0)
- **Depends On:** [base]
- **Depended By:** [module_d]
- **Files Changed:** 1 file
- **Summary:** [brief summary]

## Issues Log

| Module | Issue | Status | Resolution |
|--------|-------|--------|------------|
| module_c | View XPath error | ✅ FIXED | Deactivated broken view |

## Next Steps

- [ ] Complete module_c
- [ ] Run full testing
- [ ] Generate final CLAUDE.md
```

**Per-module output structure:**
```
module_migration/
├── MIGRATION_STATUS.md      # Main tracking file
├── module_a/
│   ├── migrated/           # Migrated code
│   ├── changes.md         # Changes made to this module
│   └── test_checklist.md  # Testing checklist
├── module_b/
│   ├── migrated/
│   ├── changes.md
│   └── test_checklist.md
└── ...
```

### Per-Module Testing Checklist Template

For each module, create `test_checklist.md`:

```markdown
# Test Checklist: <module_name>

## Migration Info
- **Source Version:** Odoo X.0
- **Target Version:** Odoo Y.0
- **Migrated By:** [Name]
- **Date:** YYYY-MM-DD

## Changes Summary
- Files modified: X files
- Breaking changes: X items
- Custom fields affected: X fields

## Pre-Deployment Testing

### Basic Tests
- [ ] Module installs without errors
- [ ] All models load correctly
- [ ] No missing dependencies

### Model Tests
- [ ] Can create new records
- [ ] Can edit existing records
- [ ] Can delete records (if allowed)
- [ ] Computed fields calculate correctly
- [ ] Related fields work properly

### View Tests
- [ ] Form view loads
- [ ] List view loads
- [ ] Search view works
- [ ] Kanban view works (if applicable)

### Business Logic Tests
- [ ] @api.depends methods fire correctly
- [ ] @api.constrains validation works
- [ ] @api.onchange methods work
- [ ] Workflow transitions work

### Integration Tests
- [ ] Related modules work together
- [ ] API endpoints respond correctly
- [ ] Cron jobs execute (if any)

### Data Tests
- [ ] Existing data loads correctly
- [ ] No data loss after migration
- [ ] Field values preserved

## Sign-Off
| Test | Status | Tester | Notes |
|------|--------|--------|-------|
| Basic | ⏳ | | |
| Model | ⏳ | | |
| View | ⏳ | | |
| Business Logic | ⏳ | | |
| Integration | ⏳ | | |
| Data | ⏳ | | |

## Issues Found
| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | | | |
```

### 3.3.1 Run Tests After Each Module Migration (AUTO)

**SETELAH menyelesaikan migration per module, WAJIB jalankan test:**

```bash
# Run tests based on user selection in Step 1
python3 scripts/run_module_tests.py \
    --module module_name \
    --test-type syntax,load,integration \
    --odoo-path /path/to/odoo-17.0 \
    --output ./module_migration/module_name/test_results.md
```

**Test Types:**

| Type | Command | Description | When to Use |
|------|---------|-------------|-------------|
| **syntax** | `python -m py_compile <file.py>` | Validasi Python syntax | Always (default) |
| **load** | `python -c "import odoo; import module"` | Test module import | After syntax passes |
| **integration** | `odoo-bin -u module -d test_db` | Full module install | Pre-production |

**Test Results Format:**
```markdown
# Test Results: module_name

## Syntax Validation
- ✅ PASS: models/module.py
- ✅ PASS: wizards/module_wizard.py
- ⏭️ SKIP: tests/ (no test files)

## Module Load Test
- ✅ PASS: Module can be imported
- ⏭️ SKIP: Requires Odoo environment

## Integration Test
- ⏭️ SKIP: Requires running Odoo server
- Run manually: odoo-bin -u module_name -d test_db --test-enable
```

**IMPORTANT:**
- Jika test FAILED, STOP dan fix issues sebelum lanjut ke module berikutnya
- Update MIGRATION_STATUS.md dengan test results
- Jangan pernah skip test jika diminta oleh user

### 3.4 Use Subagents for Parallel Module Processing

For multiple independent modules, use subagent-driven-development:
```
Use superpowers:subagent-driven-development skill to process
multiple modules in parallel when they have no dependencies
on each other.
```

---

## Step 4: Generate Comprehensive Output

### 4.1 Generate CLAUDE.md

Create comprehensive CLAUDE.md with:
- Migration info
- Version-specific breaking changes (from Step 2)
- Per-module manual review checklist
- Pre/post migration tasks

### 4.2 Generate Manual Review Guide

For each custom module, create review checklist:
- Fields yang perlu dicek manual
- Business logic yang mungkin affected
- Views yang perlu direview
- Workflows yang perlu diverifikasi

---

## Scripts

### scripts/compare_odoo_versions.py
Compare old and new Odoo versions to identify breaking changes:
```bash
python3 scripts/compare_odoo_versions.py /path/to/odoo-15.0 /path/to/odoo-17.0 15.0 17.0
```

### scripts/validate_versions.py
Validate if migration path is supported:
```bash
python3 scripts/validate_versions.py 15.0 17.0
```

### scripts/generate_context.py
Generate CLAUDE.md for migration:
```bash
python3 scripts/generate_context.py 15.0 17.0 module_a module_b
```

### scripts/pre_migration_checklist.py
Run pre-migration checks:
```bash
python3 scripts/pre_migration_checklist.py <custom_modules_path> <target_version>
```

### scripts/analyze_business_context.py
Analyze module structure and generate Business Context Questionnaire:
```bash
python3 scripts/analyze_business_context.py <module_path>
```

This script:
- Identifies custom models, fields, and methods
- Generates questionnaire for developer input
- Creates risk assessment matrix
- Outputs `business_context.md`

### scripts/generate_migration_status.py
Generate dan update MIGRATION_STATUS.md automatically:

```bash
# Generate initial status file
python3 scripts/generate_migration_status.py \
    --source-version 15.0 \
    --target-version 17.0 \
    --modules module_a,module_b,module_c \
    --test-type syntax,load,integration \
    --output ./module_migration/MIGRATION_STATUS.md

# Update after each module
python3 scripts/generate_migration_status.py \
    --update \
    --module module_a \
    --status DONE \
    --changes "models: 2 files, views: 1 file" \
    --test-result PASSED \
    --output ./module_migration/MIGRATION_STATUS.md
```

This script:
- Creates MIGRATION_STATUS.md dengan template lengkap
- Calculates dependency levels automatically
- Updates progress table setelah each module
- Logs issues dan resolutions

### scripts/run_module_tests.py
Run tests after each module migration:

```bash
# Run all enabled tests
python3 scripts/run_module_tests.py \
    --module module_name \
    --test-type syntax,load,integration \
    --odoo-path /path/to/odoo-17.0 \
    --output ./module_migration/module_name/test_results.md

# Run specific test only
python3 scripts/run_module_tests.py \
    --module module_name \
    --test-type syntax
```

This script:
- **Syntax Test**: Validates Python files dengan py_compile
- **Load Test**: Tests module import dalam Odoo environment
- **Integration Test**: Runs full module install/update test
- Generates test_results.md dengan detailed output

---

## Database Migration (Use Separate Skill)

**For database migration, use the `odoo-db-migration` skill instead.**

This skill handles module code migration only. For database migration:
1. First migrate all modules using this skill
2. Then use `/odoo-db-migration` to handle database upgrade

The `odoo-db-migration` skill handles:
- Database dump analysis
- upgrade.odoo.com integration
- SQL error fixing
- Data migration

---

## Requirements

- odoo-module-migrator: `pip3 install odoo-module-migrator`
- Git (for cloning repositories)
- Python 3.8+
- Access to both old and new Odoo/Enterprise source code

---

## Examples

### Full Module Migration
User: "Migrate my custom modules from Odoo 15 to 17. I have old Odoo 15 code at /path/odoo15 and new Odoo 17 at /path/odoo17"

AI will:
1. **FIRST: Check upgrade.odoo.com results**
   - Ask if upgrade.odoo.com has been run
   - Get path to migration results
   - Ask what issues were found
2. Ask for all paths (old Odoo, new Odoo, custom modules)
3. Ask for list of modules to migrate
4. Compare Odoo 15 vs Odoo 17 code to identify breaking changes
5. For each module (in dependency order):
   - Analyze module structure
   - Run odoo-module-migrator
   - Check for breaking changes
   - Generate fixes
   - Create module review checklist
6. Generate CLAUDE.md with version-specific breaking changes
7. After module migration is complete, recommend odoo-db-migration skill for database

### Multiple Modules with Dependencies
User: "Migrate my modules: module_a, module_b, module_c from Odoo 15 to 17"

AI will:
1. Analyze dependencies from __manifest__.py
2. Determine migration order: module_a (no deps), module_b (depends on a), module_c (depends on b)
3. Migrate each module in order, tracking status
4. Generate per-module review checklist
5. Provide migration summary

### Module Migration with Upgrade Report Integration
User: "After running database migration, I got errors. Here's the upgrade report: /path/to/upgrade_report.json. Adjust my module migration accordingly."

AI will:
1. Parse the upgrade report JSON
2. Extract errors and categorize by type
3. Map errors to affected modules
4. Generate adjustment plan (add missing fields, fix views, etc.)
5. Apply adjustments to module code
6. Re-run module migration with fixes

---

## File Structure

```
project/
├── CLAUDE.md                 # Migration context (generated)
├── migration_knowledge/      # Breaking changes (generated)
│   └── breaking_changes_*.md
├── module_migration/         # Per-module migration results
│   ├── module_a/
│   │   ├── migrated/        # Migrated code
│   │   ├── review_checklist.md
│   │   ├── business_context.md    # Business context questionnaire
│   │   └── test_checklist.md     # Testing checklist
│   └── module_b/
│       ├── migrated/
│       ├── review_checklist.md
│       └── business_context.md
└── scripts/
    ├── compare_odoo_versions.py       # Version comparison
    ├── validate_versions.py           # Version validation
    ├── generate_context.py            # CLAUDE.md generator
    ├── pre_migration_checklist.py    # Pre-migration checks
    └── analyze_business_context.py   # Business context analyzer

odoo-15.0/                   # Old Odoo source (provided by user)
odoo-17.0/                   # New Odoo source (provided by user)
custom_modules/              # Modules to migrate
migration_YYYYMMDD_HHMMSS/  # Database migration outputs
├── upgrade-report.html       # Upgrade.odoo.com report
├── fix_*.sql               # SQL fixes applied
└── upgrade_logs/           # Detailed upgrade logs
```

---

## Troubleshooting

### "odoo-module-migrate command not found"
```bash
pip3 install odoo-module-migrator
```

### "Module migration failed"
1. Check source version format (use 15.0, not 15)
2. Verify all dependencies are available
3. Check for circular dependencies
4. Use odoo19-migrate-model or odoo19-migrate-view skills for manual migration

### "Dependency issues"
1. Check __manifest__.py dependencies
2. Verify required modules exist in target version
3. Reorder migration to process dependencies first
