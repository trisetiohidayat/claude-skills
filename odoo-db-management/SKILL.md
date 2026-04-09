---
name: odoo-db-management
description: |
  Database management untuk Odoo - clone, backup, drop, create database. Gunakan skill ini ketika:
  - Clone/duplicate database untuk testing
  - Backup database sebelum upgrade
  - Drop test database setelah testing
  - Create database baru untuk development
  - Management operations lain terkait database

  Fokus pada PostgreSQL operations dan Odoo db command.

## Path Resolution
GUNAKAN odoo-path-resolver untuk mendapatkan paths. Contoh:
```python
# Load paths
paths = resolve()

# Get values
python = paths['odoo']['python']  # /path/to/python
odoo_bin = paths['odoo']['bin']  # /path/to/odoo-bin
config = paths['project']['config']  # /path/to/odoo.conf
project_root = paths['project']['root']  # /Users/tri-mac/project/roedl
database_name = paths['database']['name']  # 'roedl' (from config)
```

**Catatan untuk database:**
- `paths['database']['name']` mengembalikan nama database utama (misal: 'roedl')
- Untuk operasi yang membutuhkan nama database berbeda, gunakan variable user input seperti `{target_db}` atau `{source_db}`

---

# Odoo Database Management Skill

## Overview

Skill ini membantu melakukan database management operations untuk Odoo.

## Prerequisites

### Required Information

| Info | Source |
|------|--------|
| Odoo Version | From project (15/19) |
| Config File | odoo.conf / odoo19.conf |
| Database Credentials | From config |
| Python Path | venv/bin/python |
| Odoo Bin | odoo-bin path |

## Database Operations

### 1. Clone/Duplicate Database

#### Method A: Using Odoo Command (Recommended)

```bash
# Clone database using Odoo
python odoo-bin db -r odoo -w odoo duplicate -n source_db -m target_db \
  --db_host=localhost \
  --db_port=5432
```

#### Method B: Using pg_dump + createdb

```bash
# Step 1: Dump source database
pg_dump -h localhost -p 5432 -U odoo source_db > backup.sql

# Step 2: Create new database
createdb -h localhost -p 5432 -U odoo target_db

# Step 3: Restore to new database
psql -h localhost -p 5432 -U odoo -d target_db -f backup.sql
```

#### Clone for Testing

```bash
# Common workflow: clone production to test
python odoo-bin db -r odoo -w odoo duplicate -n roedl -m roedl_test_$(date +%Y%m%d) \
  --db_host=localhost \
  --db_port=5432
```

### 2. Backup Database

#### Using pg_dump

```bash
# Backup to file
pg_dump -h localhost -p 5432 -U odoo roedl > roedl_backup_$(date +%Y%m%d).sql

# Backup with compression
pg_dump -h localhost -p 5432 -U odoo roedl | gzip > roedl_backup_$(date +%Y%m%d).sql.gz

# Backup specific tables
pg_dump -h localhost -p 5432 -U odoo -t res_partner -t sale_order roedl > partial_backup.sql
```

#### Using Odoo

```bash
# Note: Odoo doesn't have direct backup command, use pg_dump
# This is for reference only
```

### 3. Drop Database

#### Using Odoo Command

```bash
# Drop database (must exist)
python odoo-bin db -r odoo -w odoo drop roedl_test \
  --db_host=localhost \
  --db_port=5432
```

#### Using psql

```bash
# Drop database
dropdb -h localhost -p 5432 -U odoo roedl_test

# With confirmation
dropdb -h localhost -p 5432 -U odoo --if-exists roedl_test
```

### 4. Create Database

#### Using createdb

```bash
# Create empty database
createdb -h localhost -p 5432 -U odoo new_database

# Create database with owner
createdb -h localhost -p 5432 -U odoo -O other_user new_database

# Create database with template
createdb -h localhost -p 5432 -U odoo -T template0 new_database
```

#### Using Odoo (auto-create on first run)

```bash
# Start Odoo with new database name - will auto-create
paths['odoo']['python'] paths['odoo']['bin'] -c paths['project']['config'] -d new_database
```

### 5. List Databases

```bash
# List all databases
psql -h localhost -p 5432 -U odoo -l

# Or with grep
psql -h localhost -p 5432 -U odoo -lqt | cut -d \| -f 1 | grep -w database_name
```

## Common Workflows

### Workflow 1: Test Database Setup

```
1. Clone production database to test
2. Verify clone success
3. Use for testing
4. Drop test database when done
```

```bash
# Step 1: Clone
python odoo-bin db -r odoo -w odoo duplicate -n roedl -m roedl_test_$(date +%Y%m%d) \
  --db_host=localhost --db_port=5432

# Step 2: Verify
psql -h localhost -p 5432 -U odoo -lqt | cut -d \| -f 1 | grep roedl_test

# Step 3: Use for testing
# ... run tests ...

# Step 4: Drop when done
python odoo-bin db -r odoo -w odoo drop roedl_test_$(date +%Y%m%d) \
  --db_host=localhost --db_port=5432
```

### Workflow 2: Backup Before Upgrade

```
1. Backup production database
2. Restore to test database
3. Run upgrade on test
4. Verify upgrade works
5. If success, upgrade production
```

```bash
# Step 1: Backup
pg_dump -h localhost -p 5432 -U odoo roedl > roedl_backup_$(date +%Y%m%d).sql

# Step 2: Restore to test
createdb -h localhost -p 5432 -U odoo roedl_upgrade
psql -h localhost -p 5432 -U odoo -d roedl_upgrade -f roedl_backup_$(date +%Y%M%d).sql

# Step 3-4: Test upgrade
paths['odoo']['python'] paths['odoo']['bin'] -c paths['project']['config'] -d roedl_upgrade -u module_name --stop-after-init

# Step 5: If successful, upgrade production
paths['odoo']['python'] paths['odoo']['bin'] -c paths['project']['config'] -d roedl -u module_name --stop-after-init
```

### Workflow 3: Fresh Development Database

```
1. Create new database
2. Load base data
3. Install required modules
```

```bash
# Step 1: Create database
createdb -h localhost -p 5432 -U odoo roedl_dev

# Step 2: Initialize (Odoo will create base tables on first run)
paths['odoo']['python'] paths['odoo']['bin'] -c paths['project']['config'] -d roedl_dev --stop-after-init

# Step 3: Install modules
paths['odoo']['python'] paths['odoo']['bin'] -c paths['project']['config'] -d roedl_dev -i base,sale,purchase --stop-after-init
```

## Database Naming Conventions

| Purpose | Convention | Example |
|---------|-----------|---------|
| Production | No suffix | `roedl` |
| Test | `_test` or `test_` | `roedl_test`, `test_roedl` |
| Development | `_dev` | `roedl_dev` |
| Staging | `_staging` | `roedl_staging` |
| Backup | `_backup` or timestamp | `roedl_backup_20240315` |

## Security Considerations

### DO

- ✅ Always backup before destructive operations
- ✅ Use test databases with `test_` or `_test` prefix
- ✅ Verify database name before drop
- ✅ Use proper credentials

### DON'T

- ❌ Never drop production database without backup
- ❌ Never modify production directly
- ❌ Never use production database for testing
- ❌ Never ignore naming conventions

## Troubleshooting

### Error: "database already exists"

```bash
# Solution 1: Drop first
dropdb -h localhost -p 5432 -U odoo target_db

# Solution 2: Use --force with Odoo
python odoo-bin db -r odoo -w odoo duplicate -n source -m target --force
```

### Error: "database does not exist"

```bash
# Solution 1: Create first
createdb -h localhost -p 5432 -U odoo target_db

# Solution 2: Restore from backup
psql -h localhost -p 5432 -U odoo -d target_db -f backup.sql
```

### Error: "permission denied"

```bash
# Check user permissions
psql -h localhost -p 5432 -U odoo -c "\du"

# Grant permissions if needed
psql -h localhost -p 5432 -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE target_db TO odoo;"
```

### Error: "connection refused"

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check pg_hba.conf for authentication
```

## Quick Reference Commands

```bash
# List databases
psql -h localhost -p 5432 -U odoo -lqt | cut -d \| -f 1

# Clone database
python odoo-bin db -r odoo -w odoo duplicate -n source -m target

# Backup database
pg_dump -h localhost -p 5432 -U odoo db_name > backup.sql

# Restore database
psql -h localhost -p 5432 -U odoo -d db_name -f backup.sql

# Drop database
dropdb -h localhost -p 5432 -U odoo db_name

# Create database
createdb -h localhost -p 5432 -U odoo db_name
```

## Related Skills

- `odoo-db-restore`: Restore from Odoo backup zip
- `odoo-module-install`: Install/upgrade modules
- `odoo-environment`: Check environment config
