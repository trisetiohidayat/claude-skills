---
name: odoo-migration-findings
description: >
  Document findings during Odoo database migration analysis. TRIGGER when:
  - Analyzing migration issues between Odoo versions (v15→v16, v15→v19, etc.)
  - Comparing database schemas before/after upgrade
  - Finding data corruption or unexpected changes after migration
  - Checking upgrade.log for migration-related issues
  - Documenting root cause of migration bugs

  This skill creates structured finding documents in migration-specific folders.
---

# Odoo Migration Findings Documenter

## Purpose

Dokumentasikan temuan migrasi Odoo secara terstruktur untuk referensi future dan troubleshooting.

## Folder Structure

```
PROJECT_ROOT/
└── migration_findings/
    └── migration_findings_YYYYMMDD/     ← Based on backup/upgrade date
        ├── findings.md                   ← Main findings document
        ├── database_comparison.md        ← Schema/data comparison
        ├── sql_queries.md                ← SQL queries used
        └── attachments/                  ← Screenshots, exports
```

## Naming Convention

| Tanggal Backup | Folder Name | Contoh |
|---------------|-------------|--------|
| 2026-03-31 | `migration_findings_0331` | Source: Odoo 15, Target: Odoo 19 |
| 2026-04-01 | `migration_findings_0401` | Source: Odoo 16, Target: Odoo 17 |

## Finding Document Structure

```markdown
# Migration Findings - [Tanggal]

## Database Information
- **Source DB**: [Nama Database Source]
- **Source Version**: [Odoo Version, e.g., 15.0]
- **Target DB**: [Nama Database Target]
- **Target Version**: [Odoo Version, e.g., 19.0]
- **Backup Date**: [YYYY-MM-DD]
- **Upgrade Date**: [YYYY-MM-DD]

## Summary
[One paragraph executive summary of the migration issue]

## Findings

### Finding 1: [Title]
**Severity**: [Critical / High / Medium / Low]
**Model**: [affected Odoo model, e.g., res.partner.bank]
**Date Found**: [YYYY-MM-DD]

#### Description
[Detailed description of the issue]

#### Impact
[What data/functionality is affected]

#### Root Cause
[Why this happened - Odoo migration bug, schema change, etc.]

#### Evidence
```
[Any SQL queries, logs, or data showing the issue]
```

#### Resolution
- [ ] **Manual Fix Required**: [Description]
- [ ] **Data Import Needed**: [Excel file created]
- [ ] **Odoo Bug Report**: [Link if applicable]

---

### Finding 2: [Title]
[Same structure]
```

## Steps to Document Findings

### Step 1: Identify Database Versions

```bash
# Get source database info
PGPASSWORD=odoo psql -h localhost -U odoo -d SOURCE_DB -c "SELECT name FROM ir_module_module WHERE name='base' AND state='installed';"

# Get target database info
PGPASSWORD=odoo psql -h localhost -U odoo -d TARGET_DB -c "SELECT name FROM ir_module_module WHERE name='base' AND state='installed';"
```

### Step 2: Compare Table Schemas

```bash
# Compare table columns
PGPASSWORD=odoo psql -h localhost -U odoo -d SOURCE_DB -c "
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'TABLE_NAME'
ORDER BY ordinal_position;"

# Compare with target
PGPASSWORD=odoo psql -h localhost -U odoo -d TARGET_DB -c "
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'TABLE_NAME'
ORDER BY ordinal_position;"
```

### Step 3: Check Upgrade Logs

```bash
# Search for relevant migration issues
grep -i "ERROR\|WARNING\|migration\|duplicate" UPGRADE_LOG_PATH | head -50
```

### Step 4: Create Finding Document

Based on the project context:

**Roedl Project Database Config:**
| Version | Database | Port |
|---------|----------|------|
| Odoo 15 | `roedl_15_20260331` | 8115 |
| Odoo 19 | `roedl_upgraded_20260331` | 8119 |

**Upgrade Log Location:**
```
/Users/tri-mac/project/roedl/upgraded_migration_20260331/upgrade.log
```

**Backup Locations:**
```
/Users/tri-mac/project/roedl/arkanadigital-roedl-main-6002510_2026-03-31_110627_test_fs/  ← Before
/Users/tri-mac/project/roedl/upgraded_migration_20260331/upgraded_0331/                   ← After
```

### Step 5: Determine Folder Path

```python
# Example folder naming based on backup date
backup_date = "2026-03-31"  # From database name or context
folder_name = f"migration_findings_{backup_date[5:7]}{backup_date[8:10]}"
# Result: "migration_findings_0331"
```

## Example Finding Entry

Based on actual finding from Roedl migration:

```markdown
### Finding: company_id NULL after upgrade (res.partner.bank)

**Severity**: High
**Model**: res.partner.bank
**Date Found**: 2026-04-13

#### Description
Field `company_id` yang sebelumnya memiliki nilai di Odoo 15 menjadi NULL
setelah upgrade ke Odoo 19. Affects 61 records.

#### Root Cause
Di Odoo 16+, field `company_id` di `res.partner.bank` berubah dari stored field
menjadi related field (`related='partner_id.company_id'`). Partner yang merupakan
company (is_company=True) memiliki company_id=NULL secara design.

#### Resolution
- [x] **Data Import Script**: Created `import_res_partner_bank_fix.xlsx`
- [ ] Execute import setelah approval user
```

## Common Migration Issues to Document

1. **Field Type Changes**
   - Stored → Related field
   - Integer → Selection
   - Char → Text

2. **Missing Records**
   - Records di-delete oleh migration script
   - Records tidak ter-migrate

3. **Duplicate Key Issues**
   - Unique constraints berubah
   - Composite match tidak tersedia

4. **Partner/Contact Issues**
   - Partner di-merge atau de-duplicate
   - Commercial partner changes

5. **Module Compatibility**
   - Custom modules tidak installable
   - Deprecated features dihapus

## Output Checklist

When documenting a finding, always include:

- [ ] Database source & target versions
- [ ] Affected model/table
- [ ] Number of affected records
- [ ] SQL evidence (query + results)
- [ ] Upgrade log excerpt (if applicable)
- [ ] Recommended resolution
- [ ] Any Excel files or scripts created

## Quick Command Reference

```bash
# Export table to compare
PGPASSWORD=odoo psql -h localhost -U odoo -d DB_NAME -c "COPY (SELECT * FROM table_name) TO STDOUT WITH CSV HEADER" > export.csv

# Compare record counts
PGPASSWORD=odoo psql -h localhost -U odoo -d DB_OLD -c "SELECT COUNT(*) FROM table_name;"
PGPASSWORD=odoo psql -h localhost -U odoo -d DB_NEW -c "SELECT COUNT(*) FROM table_name;"

# Find duplicate values
PGPASSWORD=odoo psql -h localhost -U odoo -d DB_NAME -c "SELECT column, COUNT(*) FROM table_name GROUP BY column HAVING COUNT(*) > 1;"
```
