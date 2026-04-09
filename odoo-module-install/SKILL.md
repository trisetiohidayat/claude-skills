---
name: odoo-module-install
description: |
  Install, upgrade, atau uninstall Odoo modules melalui command line. Gunakan skill ini kapanpun:
  - User ingin menginstall module Odoo baru
  - User ingin upgrade/update module yang sudah ada
  - User ingin uninstall module Odoo
  - User menanyakan cara install module via CLI
  - User mengalami error saat install/uninstall module
  - User butuh validasi module sebelum install
  - User ingin restart Odoo setelah install

  Skill ini mendukung Odoo 15, 16, 17, 18, dan 19.
---

# Odoo Module Install Skill

## Overview

Skill ini membantu install, upgrade, dan uninstall Odoo modules melalui command line (CLI). Ini adalah cara yang lebih reliable dibanding via UI karena:
- Tidak perlu restart Odoo berkali-kali
- Error lebih jelas terlihat
- Bisa batch install multiple modules
-过程 lebih terkontrol

## Prerequisites

Pastikan kamu memiliki:
1. **Odoo configuration** - Cek `odoo.conf` atau settings untuk dapat:
   - Odoo config file path
   - HTTP port
   - Database name
   - Admin password

2. **Akses terminal** - Untuk menjalankan command

3. **Module path** - Lokasi module yang akan diinstall

---

## Module Installation Workflow

### Step 1: Identify Odoo Version dan Configuration

**Tanya user atau cari configuration:**

1. **Cek Odoo version:**
   - Lihat di `odoo/__init__.py` atau `odoo/version.py`
   - Atau cek di database: `SELECT * FROM ir_config_parameter WHERE key = 'database.version'`

2. **Cek Odoo config file:**
   - Odoo 15: `odoo.conf` di project root
   - Odoo 19: `odoo19.conf` di project root (sesuai CLAUDE.md)

3. **Get configuration values:**
   - `--config` - Path ke config file
   - `--database` atau `-d` - Nama database
   - `--stop-after-init` - Stop setelah init (untuk scripting)
   - `--no-http` - Tidak start HTTP server

**Dari CLAUDE.md (kalau ada):**
- Odoo 19: Port 8133, Database: roedl, Config: odoo19.conf

### Step 2: Validate Module Structure

**Sebelum install, wajib validasi module:**

1. **Cek manifest file (`__manifest__.py` atau `__openerp__.py`):**
   ```python
   # Contoh __manifest__.py minimal
   {
       'name': "Module Name",
       'version': '1.0',
       'category': 'Category',
       'depends': ['base'],
       'data': [
           'views/views.xml',
           'security/ir.model.access.csv',
       ],
   }
   ```

2. **Cek common issues:**
   - [ ] Nama folder sama dengan `_name` di manifest
   - [ ] Ada `__init__.py` di root folder
   - [ ] Semua dependencies tersedia
   - [ ] Syntax Python valid (`python -m py_compile`)

3. **Cek module di addons path:**
   - Module harus di dalam folder yang ada di `addons_path` di odoo.conf

### Step 3: Determine Action Type

| Action | Kapan Digunakan |
|--------|-----------------|
| **Install** | Module baru, belum pernah diinstall |
| **Upgrade** | Mengupdate kode module yang sudah ada |
| **Uninstall** | Mau remove module dari database |

### Step 4: Execute Installation Command

#### Untuk Odoo 15

```bash
# Install module
python odoo-bin -c odoo.conf -d roedl -i module_name --stop-after-init

# Upgrade module
python odoo-bin -c odoo.conf -d roedl -u module_name --stop-after-init

# Uninstall module (Perlu hati-hati!)
python odoo-bin -c odoo.conf -d roedl -u module_name --uninstall --stop-after-init
```

#### Untuk Odoo 16-19

```bash
# Install module
python odoo-bin -c odoo19.conf -d roedl -i module_name --stop-after-init

# Upgrade module
python odoo-bin -c odoo19.conf -d roedl -u module_name --stop-after-init
```

**Catatan:**
- `-i` = install
- `-u` = update/upgrade
- `--stop-after-init` = stop Odoo setelah proses selesai
- Untuk multiple modules, pisahkan dengan koma: `-i module1,module2`

### Step 5: Restart Odoo Service

**Setelah install/upgrade:**

1. **Jika pakai systemd:**
   ```bash
   sudo systemctl restart odoo
   # atau
   sudo systemctl restart odoo19
   ```

2. **Jika manual/development:**
   ```bash
   # Kill existing Odoo process
   pkill -f "odoo-bin"

   # Start Odoo
   ./odoo-bin -c odoo19.conf -d roedl
   ```

3. **Via MCP (kalau tersedia):**
   Gunakan `odoo-restart` atau similar MCP command

### Step 6: Verify Installation

**Cek apakah module sudah terinstall:**

```python
# Via MCP
mcp__odoo-nok__odoo_execute_kw(
    instance="roedl-odoo19",
    model="ir.module.module",
    method="search_read",
    kwargs={
        "domain": [["name", "=", "module_name"]],
        "fields": ["name", "state", "installed_version"]
    }
)
```

**atau via SQL:**
```sql
SELECT name, state, installed_version
FROM ir_module_module
WHERE name = 'module_name';
```

**State values:**
- `uninstalled` - Belum diinstall
- `installed` - Sudah diinstall
- `to upgrade` - Perlu diupgrade
- `to install` - Menunggu install

---

## Troubleshooting

### Error: "Module not found"

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Module tidak di addons_path | Tambah path ke `addons_path` di odoo.conf |
| Salah ketik nama | Cek nama folder sama persis |
| Tidak ada `__init__.py` | Tambah `__init__.py` di folder module |

### Error: "Missing dependency"

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Dependency belum terinstall | Install dependency dulu |
| Salah nama dependency | Cek nama module yang benar |
| Circular dependency | Pertimbangkan untuk install bersamaan |

**Cek dependencies:**
```python
# Via MCP
mcp__odoo-nok__odoo_execute_kw(
    instance="roedl-odoo19",
    model="ir.module.module",
    method="search_read",
    kwargs={
        "domain": [["name", "=", "base"]],
        "fields": ["name", "state", "dependencies"]
    }
)
```

### Error: "Invalid Manifest"

**Cek manifest file:**
```python
# Validasi manifest dengan Python
import ast

with open('__manifest__.py', 'r') as f:
    manifest = ast.literal_eval(f.read())

# Wajib ada:
assert 'name' in manifest
assert 'version' in manifest
assert 'depends' in manifest
```

### Error: "Access Error"

**Solution:**
- Pastikan running sebagai user yang punya akses
- Untuk install, butuh admin access
- Cek `ir.model.access.csv` jika ada

### Error: "Database locked"

**Solution:**
```bash
# Kill semua Odoo processes
pkill -f odoo-bin
# Atau
ps aux | grep odoo
kill -9 <PID>
```

### Error: "FATAL: database does not exist"

**Solution:**
```bash
# Buat database dulu
createdb -U odoo roedl
# Atau via Odoo
python odoo-bin -c odoo19.conf -d roedl --db-filter=roedl
```

---

## Best Practices

1. **Always backup database** sebelum install/upgrade major
   ```bash
   pg_dump -U odoo roedl > backup_$(date +%Y%m%d).sql
   ```

2. **Test di dev environment** dulu sebelum production

3. **Upgrade base module dulu** (base, web, portal) sebelum custom modules

4. **Install dependencies first** - Urutan matters!

5. **Use `-u` (upgrade) bukan `-i` (install)** untuk mengupdate kode yang sudah ada

6. **Clear cache** setelah install:
   ```bash
   # Hapus filestore cache
   rm -rf ~/.local/share/Odoo/filestore/<db_name>/
   ```

7. **Log semua actions** untuk troubleshooting

---

## Quick Reference Command

```bash
# Full command template
python odoo-bin \
  -c odoo19.conf \           # Config file
  -d roedl \                  # Database
  -i module_name \            # Install (ganti -u untuk upgrade)
  --stop-after-init \        # Stop setelah selesai
  --log-level=debug          # Log level (info, debug, warning, error)
```

**Dengan Multi-database:**
```bash
python odoo-bin -c odoo19.conf -d db1,db2 -i module_name --stop-after-init
```

---

## Contoh Penggunaan

### Contoh 1: Install module baru

User: "Install module custom_roedl ke Odoo 19"

```bash
# Step 1: Validate module structure
# Step 2: Execute install
python odoo-bin -c odoo19.conf -d roedl -i custom_roedl --stop-after-init

# Step 3: Verify
# Cek state = 'installed'
```

### Contoh 2: Upgrade module yang sudah ada

User: "Update module roedl_sales karena ada perubahan kode"

```bash
python odoo-bin -c odoo19.conf -d roedl -u roedl_sales --stop-after-init
```

### Contoh 3: Multiple modules

User: "Install module A dan B beserta dependencies"

```bash
python odoo-bin -c odoo19.conf -d roedl -i module_a,module_b --stop-after-init
```
