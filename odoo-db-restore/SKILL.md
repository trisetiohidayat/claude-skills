---
name: odoo-db-restore
description: |
  Restore Odoo database dari file backup zip. Gunakan skill ini setiap kali:

  - User meminta "restore database"
  - User meminta "restore dari file zip"
  - User meminta "load database dari backup"
  - User memberikan file .zip backup Odoo

  PENTING: Skill ini melakukan DUA hal:
  1. Restore database SQL menggunakan `odoo-bin db load`
  2. Extract filestore dari zip ke data_dir (ini KRUSIAL!)

## Path Resolution

GUNAKAN odoo-path-resolver untuk mendapatkan paths:
```bash
paths = resolve()
python = paths['odoo']['python']      # /path/to/venv/bin/python
odoo_bin = paths['odoo']['bin']       # /path/to/odoo-bin
odoo_dir = paths['odoo']['dir']       # /path/to/odoo-18.0/odoo
project_root = paths['project']['root'] # /path/to/project
config = paths['project']['config']    # /path/to/odoo.conf
data_dir = paths['project']['data_dir'] # /path/to/data_dir
```

---

# Odoo Database Restore

## Overview

Restore Odoo database dari file backup zip. Ada 2 komponen yang direstore:

1. **Database SQL** - direstore menggunakan `odoo-bin db load`
2. **Filestore** - WAJIB di-extract manual dari zip ke `data_dir/filestore/<db_name>/`

Tanpa filestore, attachment dan file akan error `FileNotFoundError`.

## Step 1: Find Backup File

Cari file backup zip:
```bash
find <project_root> -name "*.zip" 2>/dev/null
```

atau dari path yang diberikan user.

## Step 2: Determine Target Database Name

Tanya user jika tidak jelas:
- Default: nama file tanpa ekstensi
- Contoh: `maxxi_staging_2026-04-02.zip` → `maxxi_staging`

## Step 3: Extract DB Credentials

Cek `odoo.conf` untuk credentials:
```bash
grep -E "^db_" <odoo.conf>
```

Ambil:
- db_host (default: localhost)
- db_port (default: 5432)
- db_user
- db_password

## Step 4: Restore Database SQL

**Odoo 18 syntax (BENAR):**

```bash
cd <odoo_dir> && <python> <odoo_bin> db \
  -r <db_user> \
  -w <db_password> \
  --db_host <db_host> \
  --db_port <db_port> \
  load [-f] <target_db_name> <path_to_zip>
```

**Contoh lengkap:**
```bash
cd /Users/tri-mac/odoo/odoo18-tracon/odoo && \
/Users/tri-mac/other/pas/maxxi/venv18/bin/python odoo-bin db \
  -r odoo \
  -w odoo \
  --db_host localhost \
  --db_port 5432 \
  load -f maxxi_tani \
  /Users/tri-mac/other/pas/maxxi/backup.zip
```

**Opsi:**
- `-f, --force` - Drop existing database first, then restore

## Step 5: Extract Filestore (KRUSIAL!)

Odoo `db load` TIDAK restore filestore. Harus extract manual:

```bash
# 1. Buat temporary directory
mkdir -p /tmp/filestore_extract

# 2. Extract filestore dari zip
unzip -o <path_to_zip> "filestore/*" -d /tmp/filestore_extract/

# 3. Replace filestore directory
rm -rf <data_dir>/filestore/<target_db_name>
cp -r /tmp/filestore_extract/filestore <data_dir>/filestore/<target_db_name>

# 4. Verify
ls <data_dir>/filestore/<target_db_name>/
```

**Contoh:**
```bash
mkdir -p /tmp/filestore_extract
unzip -o /Users/tri-mac/other/pas/maxxi/backup.zip "filestore/*" -d /tmp/filestore_extract/
rm -rf /Users/tri-mac/other/pas/maxxi/data_dir/filestore/maxxi_tani
cp -r /tmp/filestore_extract/filestore /Users/tri-mac/other/pas/maxxi/data_dir/filestore/maxxi_tani
ls /Users/tri-mac/other/pas/maxxi/data_dir/filestore/maxxi_tani/
```

## Step 6: Verify Restore

### A. Check database exists
```bash
psql -h <db_host> -p <db_port> -U <db_user> -lqt | grep <db_name>
```

### B. Check filestore
```bash
ls <data_dir>/filestore/<db_name>/ | wc -l
# Should show number > 0
```

### C. Check for specific file that should exist
```bash
# Check attachment yang ada di backup
unzip -l <path_to_zip> | grep "d0/d0"
```

## Common Issues

### Error: "database already exists"
Gunakan `-f` flag untuk force replace:
```bash
odoo-bin db load -f <db_name> <zip_file>
```

### Error: "unrecognized arguments"
Pastikan syntax BENAR:
- ✅ `-r odoo -w odoo --db_host localhost`
- ❌ `-r=odoo -w=odoo --db_host=localhost`

### Error: FileNotFoundError untuk attachment
Filestore belum di-extract. Kembali ke Step 5.

### Error: "connection refused"
PostgreSQL tidak running atau credentials salah.
```bash
pg_isready -h localhost -p 5432
```

## Summary Checklist

- [ ] Find backup zip file
- [ ] Confirm target database name with user
- [ ] Extract credentials from odoo.conf
- [ ] Run `odoo-bin db load` with correct syntax
- [ ] **Extract filestore** to data_dir
- [ ] Verify database exists
- [ ] Verify filestore extracted
- [ ] Report to user

## Examples

### Example 1: Simple restore
```
User: "restore database dari backup.zip"

1. find backup.zip
2. Ask: "Database name?" → maxxi_prod
3. Extract credentials
4. Restore: cd <odoo_dir> && <python> <odoo_bin> db -r odoo -w odoo load maxxi_prod backup.zip
5. Extract filestore
6. Verify
```

### Example 2: Force replace existing database
```
User: "restore ke database yang sudah ada, overwrite"

1. Same steps...
2. Add -f flag: odoo-bin db load -f existing_db backup.zip
3. Extract filestore
4. Verify
```

### Example 3: Restore specific database from different name
```
User: "restore backup.zip ke database baru called 'testing_db'"

1. Same steps...
2. Use different name: odoo-bin db load testing_db backup.zip
3. Extract filestore to testing_db
4. Verify
```
