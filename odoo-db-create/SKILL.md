---
name: odoo-db-create
description: >
  Membuat database Odoo baru melalui method Odoo (RPC/service), BUKAN via psql langsung.
  Trigger ketika user meminta: "buatkan database odoo", "create odoo database",
  "install odoo database", "database baru odoo", "odoo db create", atau setiap
  kali user ingin membuat database Odoo tanpa menggunakan psql/createdb.
---

# Odoo DB Create Skill

## Purpose

Membuat database Odoo baru menggunakan **method RPC Odoo** (`exp_create_database`), bukan via
`psql` atau `createdb` langsung. Ini memastikan:
- User `db_user` dari `odoo.conf` digunakan, tidak perlu superuser postgres
- Schema base module terinstall otomatis
- Admin password, login, language di-set dengan benar
- Ekstensi PostgreSQL (`pg_trgm`, `unaccent`) dibuat otomatis

---

## Prerequisites

1. **Odoo sudah running** (minimal 1 instance aktif) — karena RPC butuh server yang berjalan
2. **Master password Odoo** (`admin_passwd` di `odoo.conf`) — diperlukan untuk RPC call
3. **File `odoo.conf`** project tersedia — untuk baca `db_user`, `db_password`, `db_host`, `db_port`
4. **Python venv Odoo aktif** — supaya bisa import modul `odoo`

---

## Method: RPC via `dispatch_rpc`

Gunakan `odoo.service.db.exp_create_database()` yang dipanggil via RPC dispatcher.
Ini cara yang sama persis seperti Odoo Database Manager di UI (`/web/database/create`).

### Step-by-step

**Step 1: Identifikasi Odoo instance dan config**

Dari `odoo.conf` project, baca:
- `db_host`, `db_port` (biasanya `localhost`, `5432`)
- `db_user`, `db_password`
- `admin_passwd` (master password, default `admin`)

**Step 2: Tentukan parameter database baru**

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `db_name` | — | **Required.** Nama database baru |
| `master_pwd` | dari `odoo.conf` | Master password Odoo |
| `demo` | `False` | Install demo data (`True`) atau tidak |
| `lang` | `'en_US'` | Language code |
| `password` | `'admin'` | Password untuk user admin |
| `login` | `'admin'` | Login untuk user admin |
| `country_code` | `None` | Kode negara (misal `'ID'` untuk Indonesia) |
| `phone` | `None` | Nomor telepon company |

**Step 3: Buat script Python untuk RPC call**

Ada 2 cara:

### Cara A: Langsung via Odoo shell (paling simpel)

```python
# Buat script: create_db.py
import odoo
from odoo import tools
from odoo.tools.config import config

# --- Konfigurasi (sesuaikan dengan project) ---
ODOO_CONF = '/path/to/odoo.conf'
DB_NAME = 'sawit_odoo'
MASTER_PWD = 'admin'         # dari odoo.conf: admin_passwd
ADMIN_PASSWORD = 'admin'       # password untuk user admin
ADMIN_LOGIN = 'admin'          # login untuk user admin
LANG = 'en_US'
DEMO = False
COUNTRY_CODE = None            # atau 'ID' untuk Indonesia
PHONE = None

# Load Odoo config
tools.config.parse_config(['-c', ODOO_CONF])

# Import service dan panggil
from odoo.service.db import exp_create_database

try:
    exp_create_database(
        db_name=DB_NAME,
        demo=DEMO,
        lang=LANG,
        user_password=ADMIN_PASSWORD,
        login=ADMIN_LOGIN,
        country_code=COUNTRY_CODE,
        phone=PHONE,
    )
    print(f"SUCCESS: Database '{DB_NAME}' created!")
except Exception as e:
    print(f"ERROR: {e}")
```

Jalankan:
```bash
source ~/sawit-odoo/venv/bin/activate
python /path/to/create_db.py
```

### Cara B: Via XML-RPC dari bahasa lain (Python, JS, dll)

```python
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'existing_db'           # database existing yang sudah ada
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'
MASTER_PWD = 'admin'               # master password dari odoo.conf

# 1. Login dulu untuk dapat UID
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

# 2. RPC ke service db
db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')

# 3. Buat database baru
result = db_service.create_database(
    MASTER_PWD,        # master password
    'sawit_odoo',      # nama database baru
    False,             # demo data
    'en_US',           # language
    'admin',           # admin password
    'admin',           # admin login
    None,              # country_code
    None,              # phone
)
print(f"Result: {result}")
```

> **Catatan:** XML-RPC Cara B butuh database existing untuk auth. Kalau tidak ada,
> gunakan Cara A (langsung via `exp_create_database`).

### Cara C: Via Odoo Shell Interaktif

```bash
source ~/sawit-odoo/venv/bin/activate
python ~/odoo/odoo19/odoo/odoo-bin shell -c ~/sawit-odoo/odoo.conf -d existing_db

# Di dalam shell Odoo:
from odoo.service.db import exp_create_database
exp_create_database('sawit_odoo', False, 'en_US', 'admin', 'admin', None, None)
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `AccessDenied()` | Master password salah | Cek `admin_passwd` di `odoo.conf` |
| `DatabaseExists` | Database sudah ada | Gunakan nama berbeda atau drop dulu |
| `list_db` disabled | `list_db = False` di config | Set `list_db = True` di `odoo.conf` |
| `Connection refused` | Odoo tidak running | Start Odoo dulu |
| `pg_trgm extension` warning | Extensions gagal dibuat | Biasanya tidak blocking, lanjut normal |

---

## Konvensi Naming Database

Odoo menggunakan regex `^[a-zA-Z0-9][a-zA-Z0-9_.-]+$`:
- ✅ `sawit_odoo`, `sawit-prod`, `SAWIT1`
- ❌ `sawit odoo` (spasi), `sawit@prod` (spesial char)

---

## Contoh Lengkap: Buat Database SAWIT_ODOO

**Kasus:** User ingin buat database baru dengan:
- Nama: `SAWIT_ODOO`
- Admin login: `admin`
- Admin password: `admin`
- Language: `en_US` (atau `id_ID`)
- Demo data: tidak
- Country: Indonesia (`ID`)

**Step 1:** Buat script
```python
# ~/sawit-odoo/create_db.py
import odoo
from odoo import tools
from odoo.tools.config import config

tools.config.parse_config(['-c', '/Users/tri-mac/sawit-odoo/odoo.conf'])

from odoo.service.db import exp_create_database

exp_create_database(
    db_name='SAWIT_ODOO',
    demo=False,
    lang='en_US',
    user_password='admin',
    login='admin',
    country_code=None,
    phone=None,
)
print("Database SAWIT_ODOO created successfully!")
```

**Step 2:** Jalankan
```bash
source ~/sawit-odoo/venv/bin/activate
python ~/sawit-odoo/create_db.py
```

**Step 3:** Update `odoo.conf` untuk gunakan database baru
```ini
db_name = SAWIT_ODOO
```

---

## Key Internals (for reference)

`exp_create_database()` di `odoo/service/db.py:177` melakukan 2 hal:

1. **`_create_empty_database(db_name)`** — connect ke PostgreSQL via
   `odoo.sql_db.db_connect('postgres')`, buat database dengan `CREATE DATABASE`,
   lalu install extensions (`pg_trgm`, `unaccent`)

2. **`_initialize_db(db_name, demo, lang, ...)`** — buat `Registry` baru,
   install semua modul base, set admin password/login/language, commit

Ini TIDAK menggunakan `psql` atau `createdb` CLI — murni lewat Python/psycopg2
melalui connection pool Odoo.
