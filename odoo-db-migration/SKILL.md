# Odoo Database Migration Skill

## Invocation Patterns

- `/odoo-db-migration` - Start database migration workflow
- `/odoo-db-migrate` - Start database migration workflow
- "database migration Odoo" - Trigger when user mentions database migration
- "upgrade database" - Trigger when user mentions database upgrade
- "apply fix to database" - Trigger when user wants to apply SQL fixes
- "generate reusable fix script" - Trigger when user wants to create fix script for other databases

## Description

Odoo Database Migration skill for handling database upgrades via upgrade.odoo.com and applying proven SQL fixes to other databases.

**Core Capabilities:**
1. **Database Upgrade** - Run upgrade.odoo.com test/production commands
2. **Fix Script Generation** - Generate reusable bash scripts from proven fix_run001.sql
3. **Apply Fixes** - Apply SQL fixes to target databases with backup and verification

**Key Difference from Module Migration:**
- Module migration = migrate Python/XML code files
- Database migration = migrate data/schema via upgrade.odoo.com + apply proven SQL fixes

**This skill generates REUSABLE bash scripts** that can apply proven fixes to other databases, making migration more efficient for similar databases.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE MIGRATION WORKFLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STEP 1: PREPARE DUMP                                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Export database to .zip or .sql                             │  │
│  │ • Place in migration working directory                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 2: RUN UPGRADE                                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Run: ./odoo_upgrade.sh <dump> <target_version>              │  │
│  │ • Monitor upgrade.odoo.com status                             │  │
│  │ • Fix errors if needed                                       │  │
│  │ • Repeat until SUCCESS                                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 3: GENERATE REUSABLE FIX SCRIPT (ON SUCCESS)                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Run: generate_reusable_fix.sh                               │  │
│  │ • Input: fix_run001.sql (proven fix)                          │  │
│  │ • Output: apply_fix_<dbname>.sh (reusable script)             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                      │
│  STEP 4: APPLY TO OTHER DATABASES                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ • Run: ./apply_fix_<dbname>.sh <target_database>              │  │
│  │ • Script creates backup, applies fixes, verifies               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Prepare Dump

**Export database:**

```bash
# Method 1: Using Odoo shell
python3 /path/to/odoo-bin \
    --config /path/to/odoo.conf \
    -d db_name \
    -c "import requests; import zipfile; import io; \
        r = requests.get('http://localhost:8069/web/database/manager'); \
        print(r.text)" 2>/dev/null || echo "Use UI to export"

# Method 2: Using pg_dump directly
pg_dump -h localhost -U odoo -Fc db_name > dump_$(date +%Y%m%d).dump

# Method 3: Using Odoo UI
# 1. Go to Settings → Database Manager
# 2. Click "Backup" for desired database
# 3. Download as .zip file
```

**Verify dump:**

```bash
# Check if valid zip
unzip -l dump.zip | head -20

# Check if contains dump.sql
unzip -p dump.zip dump.sql | head -50

# If dump.sql not inside, extract directly
unzip dump.zip -d extracted_dump/
```

---

## Step 2: Run Upgrade

Use the `odoo_upgrade.sh` script from odoo-module-migration skill:

```bash
SKILL_DIR=~/.claude/skills/odoo-module-migration
cd /path/to/migration/working/directory

# Run upgrade
$SKILL_DIR/scripts/odoo_upgrade.sh dump.zip 19.0 .odoo_contract

# Monitor status
python <(curl -s https://upgrade.odoo.com/upgrade) status -t <TOKEN>
```

**If upgrade fails:**
1. Check upgrade.log in upgrade_logs/
2. Analyze errors
3. Apply fixes to database
4. Re-export and retry

**If upgrade succeeds:**
1. Download upgraded database from upgrade.odoo.com
2. Proceed to Step 3 to generate reusable fix script

---

## Step 3: Generate Reusable Fix Script (ON SUCCESS)

**When upgrade succeeds, generate a reusable bash script from the proven fix.sql!**

This is the KEY capability: transform a one-time fix into a reusable script for other databases.

### Usage

```bash
SKILL_DIR=~/.claude/skills/odoo-db-migration

# Basic usage
$SKILL_DIR/scripts/generate_reusable_fix.sh \
    --fix-sql ./migration_xxx/upgrade_logs/run_001/fix_run001.sql \
    --output ./apply_fix_roedl.sh \
    --db-prefix roedl_ \
    --description "Roedl migration v15 to v19"

# With custom database credentials
$SKILL_DIR/scripts/generate_reusable_fix.sh \
    --fix-sql ./fix_run001.sql \
    --output ./apply_fix.sh \
    --db-host localhost \
    --db-port 5432 \
    --db-user odoo \
    --db-password odoo \
    --db-prefix prod_

# With PostgreSQL connection string
$SKILL_DIR/scripts/generate_reusable_fix.sh \
    --fix-sql ./fix_run001.sql \
    --output ./apply_fix.sh \
    --db-conn "postgresql://user:pass@localhost:5432/" \
    --db-prefix test_
```

### Input: Proven fix.sql

The script reads a successful `fix_run001.sql` containing:

```sql
-- View fixes
UPDATE ir_ui_view SET active = false WHERE id IN (383, 514, 705, ...);

-- Module fixes
UPDATE ir_module_module SET state = 'to upgrade'
WHERE name IN ('asb_timesheets_invoice', ...);

-- Tracking tables
CREATE TABLE migration_modules_to_upgrade (...);
```

### Output: Reusable bash script

Generates `apply_fix_<dbname>.sh` that can:
- Accept target database name as argument
- Create automatic backup before applying fixes
- Apply SQL fixes with error handling
- Verify fixes were applied
- Provide detailed summary report

---

## Step 4: Apply to Other Databases

**Generated script usage:**

```bash
# Make executable
chmod +x apply_fix_roedl.sh

# Run with target database
./apply_fix_roedl.sh target_database

# Run with custom backup directory
./apply_fix_roedl.sh target_database --backup-dir /path/to/backups

# Dry-run mode (shows what would be done)
./apply_fix_roedl.sh target_database --dry-run

# Skip backup
./apply_fix_roedl.sh target_database --no-backup
```

**Generated script features:**
1. **Pre-flight checks** - Verify database exists and is accessible
2. **Automatic backup** - Creates timestamped backup before any changes
3. **Fix application** - Applies all SQL statements from fix_run001.sql
4. **Verification** - Confirms fixes were applied correctly
5. **Summary report** - Shows what was done with counts

---

## Generated Script Template

The generated script follows this pattern:

```bash
#!/bin/bash
# Generated by: odoo-db-migration skill
# Generated date: 2026-04-09
# Source fix: fix_run001.sql
# Description: Roedl migration v15 to v19

set -e

# Configuration (from --fix-sql analysis)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"
DB_PREFIX="${DB_PREFIX:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
backup_database() { ... }
apply_fixes() { ... }
verify_fixes() { ... }
generate_report() { ... }

# Main
main() {
    local target_db="$1"
    local dry_run=false
    local backup_dir="./backup"
    local skip_backup=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run) dry_run=true; shift ;;
            --backup-dir) backup_dir="$2"; shift 2 ;;
            --no-backup) skip_backup=true; shift ;;
            *) target_db="$1"; shift ;;
        esac
    done

    # Execute workflow
    preflight_check "$target_db"
    [[ "$skip_backup" == false ]] && backup_database "$target_db" "$backup_dir"
    apply_fixes "$target_db"
    verify_fixes "$target_db"
    generate_report "$target_db"
}

main "$@"
```

---

## Example: Generate Fix Script from Successful Migration

### Real-world scenario from Roedl migration:

```bash
# 1. After successful upgrade, the fix script exists
ls -la migration_20260409_130656/migration_*/upgrade_logs/run_001/fix_run001.sql

# 2. Generate reusable script
SKILL_DIR=~/.claude/skills/odoo-db-migration

$SKILL_DIR/scripts/generate_reusable_fix.sh \
    --fix-sql migration_20260409_130656/migration_*/upgrade_logs/run_001/fix_run001.sql \
    --output apply_fix_roedl.sh \
    --db-prefix "" \
    --description "Roedl v15 to v19 - Views disabled + Module state fixes"

# 3. Result
# Created: apply_fix_roedl.sh (executable)
# Size: ~15 KB
# Fixes included:
#   - 23 views disabled (ir_ui_view.active=false)
#   - 7 modules set to 'to upgrade'
#   - 2 tracking tables created

# 4. Apply to similar database
./apply_fix_roedl.sh similar_database
```

---

## Script Reference

### generate_reusable_fix.sh

**Location:** `~/.claude/skills/odoo-db-migration/scripts/generate_reusable_fix.sh`

**Purpose:** Parse fix_run001.sql and generate reusable bash script

**Parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `--fix-sql` | Path to successful fix_run001.sql | Required |
| `--output` | Output script path | Required |
| `--db-host` | PostgreSQL host | localhost |
| `--db-port` | PostgreSQL port | 5432 |
| `--db-user` | PostgreSQL user | odoo |
| `--db-password` | PostgreSQL password | odoo |
| `--db-prefix` | Database name prefix | (none) |
| `--description` | Description for script header | (none) |

**Output:** Executable bash script that applies fixes to any target database

---

## Fix Categories from Upgrade

The generator recognizes these fix types from fix_run001.sql:

### 1. View Disabling
```sql
UPDATE ir_ui_view SET active = false WHERE id IN (...);
```
**Impact:** Disables broken inherited views

### 2. Module State Changes
```sql
UPDATE ir_module_module SET state = 'to upgrade' WHERE name IN (...);
```
**Impact:** Marks custom modules for migration

### 3. Tracking Tables
```sql
CREATE TABLE migration_modules_to_upgrade (...);
INSERT INTO migration_modules_to_upgrade ...;
```
**Impact:** Records audit trail

### 4. Field Updates
```sql
UPDATE ir_model_data SET ...;
UPDATE ir_actions_server SET ...;
```
**Impact:** Fixes deprecated field references

---

## Best Practices

### 1. Always Backup First
```bash
# Generated scripts automatically backup, but you can do it manually
pg_dump -h localhost -U odoo -Fc target_db > backup_$(date +%Y%m%d).dump
```

### 2. Test on Similar Environment
```bash
# Clone production to staging
./odoo-db-management.sh clone production_db staging_db

# Apply fixes to staging first
./apply_fix.sh staging_db

# Verify in UI
# Then apply to production
```

### 3. Document Custom Fixes
```bash
# Add custom SQL before running generated script
cat >> custom_fixes.sql << 'EOF'
-- Add custom fixes here
UPDATE res_partner SET customer = true WHERE customer_rank > 0;
EOF

# Run combined
psql -h localhost -U odoo -d target_db -f custom_fixes.sql
./apply_fix.sh target_db
```

### 4. Verify After Apply
```bash
# Check view states
psql -h localhost -U odoo -d target_db -c "SELECT COUNT(*) FROM ir_ui_view WHERE active = false;"

# Check module states
psql -h localhost -U odoo -d target_db -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'asb_%';"
```

---

## Error Handling

**If script fails:**
1. Check error message
2. Restore from backup: `pg_restore -h localhost -U odoo -d target_db backup_xxx.dump`
3. Analyze error
4. Fix and retry

**Common errors:**
| Error | Cause | Solution |
|-------|-------|----------|
| `database does not exist` | Wrong database name | Check database name |
| `permission denied` | Wrong user | Use correct PostgreSQL user |
| `relation does not exist` | Table not in database | Check Odoo version |
| `duplicate key` | Fix already applied | Skip or use `--force` |

---

## Quick Reference

```bash
# === Complete Workflow ===

# 1. Prepare
pg_dump -h localhost -U odoo -Fc old_db -f dump.zip

# 2. Upgrade
~/.claude/skills/odoo-module-migration/scripts/odoo_upgrade.sh dump.zip 19.0 .odoo_contract

# 3. Generate (on success)
~/.claude/skills/odoo-db-migration/scripts/generate_reusable_fix.sh \
    --fix-sql ./upgrade_logs/run_001/fix_run001.sql \
    --output apply_fix.sh

# 4. Apply to other
chmod +x apply_fix.sh
./apply_fix.sh other_database
```

---

## Bundled Files

| File | Description |
|------|-------------|
| `scripts/generate_fix_pattern.sh` | Extract reusable SQL from proven fix.sql |
| `scripts/odoo_reusable_upgrade.sh` | Run upgrade with fix pattern |
| `manual_action_task.md` | Post-upgrade manual tasks checklist |
