---
name: odoo-password-update
description: |
  Update password for Odoo user menggunakan Odoo Shell method (bukan SQL manual).
  TRIGGER secara otomatis ketika user meminta:
    - "update password user X"
    - "set password untuk user Y"
    - "ubah password [login] di database [db]"
    - "change password [login]"
    - "reset password [user]"
    - Request lain yang jelas-jelas meminta untuk mengubah password user di Odoo

  METHOD: SELALU gunakan Odoo Shell (env['res.users'].write) - JANGAN gunakan SQL langsung
  dengan hash manual. Ini adalah security requirement.
---

# Odoo Password Update Skill

## Prinsip Keamanan

**WAJIB gunakan Odoo Shell method**, BUKAN SQL langsung dengan hash manual.

- ✅ **BENAR**: `env['res.users'].write({'password': 'plain_text'})` - Odoo auto-hash
- ❌ **SALAH**: `UPDATE res_users SET password = 'pbkdf2:sha256:...'` - Manual hash prone to error

## Workflow

### Step 1: Terima Input dari User

Pastikan mendapat:
- `login`: username/login Odoo (WAJIB)
- `password`: password baru (WAJIB)
- `database`: nama database (OPSIONAL, default: `upgraded_test`)

**Contoh request**:
```
"update password main_user di database roedl_upgraded_20260325 jadi 'admin'"
```
Parse jadi:
- login: `main_user`
- password: `admin`
- database: `roedl_upgraded_20260325`

### Step 2: Auto-Detect Environment

Deteksi Odoo project yang aktif berdasarkan CWD:

1. **Cek file config** (`*.conf`) di current directory atau parent directories
2. **Cek virtualenv** (`venv*/bin/activate`, `.venv*/bin/activate`)
3. **Cek CLAUDE.md** untuk project-specific settings

**Pattern detection**:
```
odoo19.conf          → config file
venv19/bin/activate  → Python venv
odoo19.0-roedl/odoo/odoo-bin → Odoo binary path
```

**Fallback**: Jika tidak ditemukan, tanya user untuk specify config dan venv.

### Step 3: Construct Command

Gunakan template:

```bash
source {venv_path}/bin/activate && echo "
user = env['res.users'].search([('login', '=', '{login}')])
if user:
    user.write({'password': '{password}'})
    env.cr.commit()
    print('SUCCESS - Password updated for:', user.login)
    print('User ID:', user.id)
    print('User Name:', user.name)
    print('User Email:', user.email)
    print('Active:', user.active)
    print('Database:', context.get('db_name', 'unknown'))
else:
    print('ERROR - User not found:', '{login}')
" | python {odoo_bin} shell -c {config_file} -d {database} 2>&1
```

Dimana:
- `{venv_path}`: `/Users/tri-mac/project/{project}/venv19` (auto-detect)
- `{odoo_bin}`: Path ke odoo-bin (auto-detect dari project structure)
- `{config_file}`: `{project}/odoo19.conf` atau `odoo.conf`
- `{database}`: dari input user
- `{login}`: dari input user
- `{password}`: dari input user

### Step 4: Execute & Parse Output

1. Jalankan command
2. Parse output untuk extract:
   - SUCCESS/ERROR status
   - User details (id, name, login, email, active)
3. Format output ke user

### Step 5: Format Response ke User

```
✅ SUCCESS - Password Updated

User Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID         : 5
Login      : main_user
Name       : Main User
Email      : main_user@roedl.com
Active     : True
Database   : roedl_upgraded_20260325
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Password untuk 'main_user' telah di-set ke: 'admin'
```

Jika error:
```
❌ ERROR - User Not Found

Login yang dicari: nonexistent_user
Database: roedl_upgraded_20260325

User dengan login 'nonexistent_user' tidak ditemukan di database.
```

## Auto-Detection Logic

### Config File Detection

Cari file `.conf` yang mengandung Odoo config:

```bash
# Pattern yang ditemukan:
# - odoo19.conf
# - odoo.conf
# - {project}.conf

grep -l "db_name\|addons_path" *.conf 2>/dev/null | head -1
```

### Venv Detection

```bash
# Pattern yang ditemukan:
ls -d venv*/ .venv*/ 2>/dev/null | head -1
```

### Odoo Binary Path

Dari project structure Odoo:
```
{project}/
├── odoo19.0-roedl/odoo/odoo-bin  (Odoo 19)
├── odoo15.0-roedl/odoo/odoo-bin  (Odoo 15)
└── venv19/bin/python              (Python interpreter)
```

## Project-Specific Patterns

### Roedl Project Structure

```
/Users/tri-mac/project/roedl/
├── odoo19.0-roedl/odoo/odoo-bin    → Odoo 19 binary
├── enterprise-roedl-19.0/           → EE modules
├── custom_addons_19_new2/roedl/    → Custom modules
├── odoo19.conf                     → Config file
└── venv19/bin/activate             → Python venv
```

### Known Databases

| Database | Project | Default |
|----------|---------|---------|
| `upgraded_test` | roedl | ✅ Default |
| `roedl_upgraded_20260325` | roedl | - |
| `roedl` | roedl | ❌ Jangan gunakan (schema incompatible) |

## Error Handling

| Scenario | Handling |
|----------|----------|
| User tidak ditemukan | Beri ERROR message dengan detail |
| Database tidak ada | Beri ERROR: "Database tidak ditemukan" |
| Config tidak ditemukan | Tanya user untuk specify manual |
| Venv tidak ditemukan | Tanya user untuk specify manual |
| Permission denied | ERROR: "Tidak ada akses ke database" |
| Odoo shell timeout | Retry sekali, kemudian ERROR |

## Complete Example

**User Request**:
```
"update password admin di database upgraded_test jadi 'Password123'"
```

**Auto-detected**:
- Config: `/Users/tri-mac/project/roedl/odoo19.conf`
- Venv: `/Users/tri-mac/project/roedl/venv19`
- Binary: `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo-bin`
- Database: `upgraded_test`

**Command**:
```bash
source /Users/tri-mac/project/roedl/venv19/bin/activate && echo "
user = env['res.users'].search([('login', '=', 'admin')])
if user:
    user.write({'password': 'Password123'})
    env.cr.commit()
    print('SUCCESS - Password updated for:', user.login)
    print('User ID:', user.id)
    print('User Name:', user.name)
    print('User Email:', user.email)
    print('Active:', user.active)
else:
    print('ERROR - User not found: admin')
" | python /Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo-bin shell -c /Users/tri-mac/project/roedl/odoo19.conf -d upgraded_test 2>&1
```

**Success Response**:
```
✅ SUCCESS - Password Updated

User Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID         : 1
Login      : admin
Name       : Administrator
Email      : admin@roedl.com
Active     : True
Database   : upgraded_test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Password untuk 'admin' telah di-set ke: 'Password123'
```
