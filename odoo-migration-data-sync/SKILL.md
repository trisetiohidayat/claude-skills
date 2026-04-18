---
name: odoo-migration-data-sync
description: >
  Bandingkan dan sync data Odoo antara database lama (v15) dan baru (v19) setelah migrasi.
  Gunakan skill ini setiap kali user ingin:
  - Compare field antara database lama dan baru (misal: partner_id, company_id)
  - Deteksi discrepancies: record hilang, field berbeda, archived partner
  - Generate Excel template untuk fix data migrasi yang salah
  - Analisa pattern error migrasi (company→employee, archived vs active duplicate)
  - Sync ulang field tertentu setelah upgrade Odoo

  Trigger phrases: "compare v15 and v19", "sync data migrasi", "partner_id berbeda",
  "data tidak cocok", "fix migrasi", "archived partner", "missing record migrasi",
  "check migration data", "compare database", "data inconsistency after migration",
  "res.partner.bank", "res.partner"
---

# Odoo Migration Data Sync — Compare & Fix

## Purpose

Setelah migrasi Odoo (v15 → v19), data di database baru sering tidak cocok dengan
database lama. Skill ini membandingkan field tertentu antara kedua database, mendeteksi
discrepancies, dan menghasilkan Excel template untuk perbaikan.

## Core Problem Patterns (Yang Sering Terjadi)

| Pattern | Penjelasan | Contoh |
|---------|------------|--------|
| **Company→Employee** | Bank accounts company di-re-link ke employee contact | PT Rödl Consulting bank → Risna Yanti |
| **Archived→Active** | Partner archived di v19, duplicate active dibuat | Karina Kartika (pid=31 archived) → pid=2855 active |
| **Missing Record** | Record ada di v15, tidak ada di v19 | bank ID=24 tidak ada di v19 |
| **Different Partner** | Partner ID berubah karena duplicate creation | Tiffany Sanjaya pid=2931 → 2932 |

**Root cause utama:** Odoo migration melakukan archive partner lama + create new active
duplicate. Semua related records (bank accounts, addresses) perlu di-follow ke new ID.

## Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Export dari kedua database (v15 dan v19)                         │
│  → export_data() dari Odoo shell, atau SQL query langsung                │
│                                                                          │
│  STEP 2: Comparison Analysis                                              │
│  → Bandingkan field (misal partner_id) berdasarkan unique key           │
│  → Kategorikan: MATCH / DIFFERENT / MISSING_IN_NEW / MISSING_IN_OLD    │
│                                                                          │
│  STEP 3: Pattern Analysis                                                 │
│  → Archived vs Active partner duplicates                                  │
│  → Company vs Employee mislinks                                           │
│  → Identify correct target partner di database baru                       │
│                                                                          │
│  STEP 4: Generate Fix Template (Excel)                                    │
│  → Kolom: external_id, database_id, acc_number, current, target, action │
│  → Sheet 1: All records dengan fix info                                  │
│  → Sheet 2: Records yang perlu di-fix                                     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Export Data dari Kedua Database

### Menggunakan SQL Query (Recommended)

```bash
# Export dari v15 (source lama)
psql -h localhost -U odoo -d roedl_15_20260331 -c "
SELECT rpb.id, rpb.acc_number, rpb.partner_id, rp.name as partner_name
FROM res_partner_bank rpb
LEFT JOIN res_partner rp ON rpb.partner_id = rp.id
WHERE rpb.active = true
ORDER BY rpb.id" > /tmp/v15_partners.txt

# Export dari v19 (target baru)
psql -h localhost -U odoo -d roedl_upgraded_20260331 -c "
SELECT rpb.id, rpb.acc_number, rpb.partner_id, rp.name as partner_name, rp.active
FROM res_partner_bank rpb
LEFT JOIN res_partner rp ON rpb.partner_id = rp.id
WHERE rpb.active = true
ORDER BY rpb.id" > /tmp/v19_partners.txt
```

### Menggunakan Odoo Shell (untuk External ID)

```bash
source venv19/bin/activate
ODOO_BIN=odoo19.0-roedl/odoo/odoo-bin
ODOO_CONF=odoo19.conf

# Export dari v19
echo "
records = env['res.partner.bank'].search([])
# Step 1: create ir_model_data entries
records.export_data(['id'])
import time; time.sleep(0.1)
# Step 2: export with stable external IDs
result = records.export_data(['id', 'acc_number', 'partner_id/id', 'company_id/id'])
print('Total:', len(result['datas']))
for row in result['datas'][:5]:
    print(row)
" | python $ODOO_BIN shell -c $ODOO_CONF -d roedl_upgraded_20260331 2>/dev/null
```

### Menggunakan MCP Odoo

```python
# Get data from v19 via MCP
banks = mcp__rust-mcp__odoo_search_read(
    instance="roedl-odoo19",
    model="res.partner.bank",
    fields=["id", "acc_number", "partner_id", "company_id"],
    domain=[["active", "=", True]]
)
```

---

## Step 2: Comparison Analysis

Gunakan Python untuk comparing:

```python
import psycopg2

# Connect ke kedua database
conn_v15 = psycopg2.connect(
    host="localhost", port=5432,
    database="roedl_15_20260331",
    user="odoo", password="odoo"
)
conn_v19 = psycopg2.connect(
    host="localhost", port=5432,
    database="roedl_upgraded_20260331",
    user="odoo", password="odoo"
)

# Query untuk res.partner.bank
QUERY = """
SELECT rpb.id, rpb.acc_number, rpb.partner_id, rp.name as partner_name
FROM res_partner_bank rpb
LEFT JOIN res_partner rp ON rpb.partner_id = rp.id
WHERE rpb.active = true
ORDER BY rpb.id
"""

# Get data
def get_banks(conn):
    cr = conn.cursor()
    cr.execute(QUERY)
    return {r[0]: {'acc': r[1], 'pid': r[2], 'name': r[3]} for r in cr.fetchall()}

v15 = get_banks(conn_v15)
v19 = get_banks(conn_v19)
```

### Comparison Logic

```python
# Compare by bank_id (integer ID — ada di kedua DB)
results = {'match': [], 'diff': [], 'missing_v19': [], 'missing_v15': []}

for bank_id, v15_info in sorted(v15.items()):
    if bank_id not in v19:
        results['missing_v19'].append(bank_id)
    elif v15_info['pid'] != v19[bank_id]['pid']:
        results['diff'].append({
            'bank_id': bank_id,
            'acc': v15_info['acc'],
            'v15_pid': v15_info['pid'],
            'v15_name': v15_info['name'],
            'v19_pid': v19[bank_id]['pid'],
            'v19_name': v19[bank_id]['name'],
        })
    else:
        results['match'].append(bank_id)

for bank_id in sorted(v19.keys()):
    if bank_id not in v15:
        results['missing_v15'].append(bank_id)

print(f"MATCH: {len(results['match'])}")
print(f"DIFFERENT: {len(results['diff'])}")
print(f"MISSING in v19: {len(results['missing_v19'])}")
print(f"EXTRA in v19: {len(results['missing_v15'])}")
```

---

## Step 3: Pattern Analysis

### Kategori Issue

Setelah dapat list differences, kategorikan berdasarkan pattern:

```python
# Cek archived partner
def check_archived(conn, partner_id):
    cr = conn.cursor()
    cr.execute("SELECT name, active FROM res_partner WHERE id = %s", (partner_id,))
    r = cr.fetchone()
    return {'name': r[0], 'active': r[1]} if r else None

# Cek active duplicate
def find_active_duplicate(conn, partner_name):
    cr = conn.cursor()
    cr.execute("""
        SELECT id, name, active FROM res_partner
        WHERE name = %s ORDER BY id
    """, (partner_name,))
    return list(cr.fetchall())

# Cek company → employee pattern
def check_company_vs_employee(v19_pid, v19_name):
    # Jika bank company (partner=company entity) tapi di v19 ke employee
    company_keywords = ['PT ', 'Consulting', 'GmbH', 'AG', 'LLC', 'PTE']
    employee_keywords = ['Yanti', 'Nurmaharani', 'employee']
    is_company_name = any(k in v19_name for k in company_keywords)
    is_employee_name = any(k in v19_name for k in employee_keywords)
    return is_employee_name and not is_company_name
```

### Common Fix Strategy

| Pattern | Strategy |
|---------|----------|
| Archived partner, ada active duplicate | Link ke **active duplicate** (yang dibuat saat migrasi) |
| Company bank → Employee | Restore ke **company partner** |
| Archived, tidak ada duplicate | Link ke **archived partner** dengan external ID |
| Missing record | **CREATE** record baru di v19 |

---

## Step 4: Generate Fix Template

### Python Script untuk Generate Excel

```python
import psycopg2, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Styles
hdr_font = Font(bold=True, color='FFFFFF')
hdr_fill = PatternFill(start_color='2F5496', fill_type='solid')
err_fill  = PatternFill(start_color='FCE4D6', fill_type='solid')
ok_fill   = PatternFill(start_color='E2EFDA', fill_type='solid')
thin = Border(left=Side(style='thin'), right=Side(style='thin'),
              top=Side(style='thin'), bottom=Side(style='thin'))

wb = openpyxl.Workbook()

# ── SHEET 1: All Records ──────────────────────────────────────────────
ws1 = wb.active
ws1.title = "All Bank Accounts"
hdr(ws1, [
    'external_id', 'database_id', 'acc_number', 'company_id/id',
    'Account Holder', 'partner_id/id', 'partner_status',
    'target_partner', 'target_partner_id/id', 'action_needed'
])

# Lanjutkan dengan data dari comparison...
```

### Header Row Helper
```python
def hdr(ws, headers):
    for ci, h in enumerate(headers, 1):
        c = ws.cell(1, ci, h)
        c.font = hdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal='center', wrap_text=True)
        c.border = thin
    ws.row_dimensions[1].height = 22
```

### Data Row Helper
```python
def data_row(ws, ri, vals, fill=None):
    for ci, v in enumerate(vals, 1):
        c = ws.cell(ri, ci, v or '')
        c.border = thin
        if fill:
            c.fill = fill
```

### Recommended Columns

| # | Column | Source | Notes |
|---|--------|--------|-------|
| 1 | `external_id` | From v19 `ir_model_data` | Format: `__export__.res_partner_bank_X_hash` |
| 2 | `database_id` | `rpb.id` | Integer primary key |
| 3 | `acc_number` | `rpb.acc_number` | Unique key untuk matching |
| 4 | `company_id/id` | Company external ID | Kosongkan jika tidak perlu diubah |
| 5 | `Account Holder` | Partner name saat ini (v19) | Info kolom, bukan untuk import |
| 6 | `partner_id/id` | Partner external ID saat ini (v19) | Kolom untuk import/update |
| 7 | `partner_status` | `rp.active` | Active / ARCHIVED |
| 8 | `target_partner` | Partner name target fix | Info kolom |
| 9 | `target_partner_id/id` | Partner external ID target | Kolom untuk import/update |
| 10 | `action_needed` | Analysis result | NEEDS FIX / OK |

---

## External ID Resolution

### Get External IDs dari Database

```python
import psycopg2
conn = psycopg2.connect(host="localhost", port=5432,
                         database="roedl_upgraded_20260331",
                         user="odoo", password="odoo")
cr = conn.cursor()

# Partner external IDs
cr.execute("""
    SELECT res_id, module, name FROM ir_model_data
    WHERE model = 'res.partner' ORDER BY res_id
""")
partner_xid = {r[0]: f"{r[1]}.{r[2]}" for r in cr.fetchall()}

# Company external IDs
cr.execute("""
    SELECT res_id, module, name FROM ir_model_data
    WHERE model = 'res.company' ORDER BY res_id
""")
company_xid = {r[0]: f"{r[1]}.{r[2]}" for r in cr.fetchall()}

# Bank external IDs
cr.execute("""
    SELECT res_id, module, name FROM ir_model_data
    WHERE model = 'res.partner.bank' ORDER BY res_id
""")
bank_xid = {r[0]: f"{r[1]}.{r[2]}" for r in cr.fetchall()}

cr.close(); conn.close()
```

### Key External IDs (Roedl Project)

```
base.main_company         → company_id=1  (PT Rödl Consulting)
base.main_partner         → partner_id=1  (PT Rödl Consulting, ⚠️ archived)
__export__.res_partner_2839_* → partner_id=2839 (Roedl Tax Consulting, ✅ active)
__export__.res_partner_2855_* → partner_id=2855 (Karina Kartika, ✅ active)
__export__.res_partner_2932_* → partner_id=2932 (Tiffany Sanjaya, ✅ active)
```

---

## Special Considerations

### ⚠️ Archived Partner dengan Active Duplicate

Saat migrasi, Odoo often:
1. Archive old partner (active=False)
2. Create new active partner with same name
3. BUT: related records (bank accounts) stay linked to archived partner

**Contoh:**
- v15: Karina Kartika, pid=31, active=False (archived after migration)
- v19: Karina Kartika, pid=2855, active=True (new active duplicate)
- **Bank account** di v19 → linked to pid=2855 (active) ✅ **OR** pid=31 (archived) ❌

**Fix:** Depends on case:
- If bank already points to active duplicate → **NO ACTION** needed
- If bank still points to archived → **LINK to active duplicate**

### ⚠️ Company Bank Accounts

Bank accounts milik company (acc_holder_name = "PT Rödl Consulting") harus
ter-link ke **company contact** (partner dengan `company_id=None` atau partner
dari `res.company.partner_id`), BUKAN ke employee.

**Cek company → partner mapping:**
```sql
SELECT rc.id, rc.name, rc.partner_id, rp.name
FROM res_company rc
LEFT JOIN res_partner rp ON rc.partner_id = rp.id
ORDER BY rc.id
```

### ⚠️ acc_number Matching

Gunakan `acc_number` sebagai unique key untuk matching antara v15 dan v19,
BUKAN `bank_id` (integer primary key), karena:
- Bank IDs bisa berbeda antar database
- acc_number adalah business identifier yang stabil

---

## Database Configuration

| Project | Version | Database | Port |
|---------|---------|----------|------|
| roedl | Odoo 15 | `roedl_15_20260331` | 8115 |
| roedl | Odoo 19 | `roedl_upgraded_20260331` | 8133 |

**PostgreSQL:** `host=localhost port=5432 user=odoo password=odoo`

---

## Safety Rules

1. **Selalu export dulu** — simpan data kedua DB sebelum modifikasi
2. **Pahami root cause** — jangan hanya fix surface-level, cek patternnya
3. **Verify archived vs active** — archived partner masih bisa di-link, tapi pertimbangkan untuk link ke active duplicate
4. **Test import** — gunakan dry-run atau import ke database test dulu
5. **Backup** — selalu backup sebelum bulk import
