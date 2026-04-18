---
name: odoo-orm-sync
description: >
  Sync Odoo data antar database menggunakan ORM native Odoo (export_data / load).
  Gunakan skill ini setiap kali user ingin:
  - Export data Odoo ke Excel/CSV menggunakan method ORM `export_data()`
  - Import data dari Excel/CSV ke Odoo menggunakan method ORM `load()`
  - Migrasi data antar Odoo versi berbeda (v15 → v19, dll)
  - Sync field tertentu saja tanpa perlu export semua kolom
  - Generate External ID dengan format `__export__.model_dbID_hash` via Odoo ORM

  Trigger phrases: "export data odoo", "import data odoo", "sync data odoo",
  "export model ke csv", "import csv ke odoo", "odoo export import",
  "dump data odoo", "restore data odoo", "generate external id odoo",
  "export dengan external id", "import sesuai field"
---

# Odoo ORM Data Sync

## Purpose

Export dan import data Odoo menggunakan **ORM native Odoo** — `export_data()` dan `load()`.
Ini lebih akurat dibanding SQL langsung karena:
- ORM resolve External ID secara otomatis
- ORM trigger onchange, computed fields, override `write()`/`create()`
- Many2one fields accept External ID format (`module.name`) langsung

---

## Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: Export dari Source DB (Odoo ORM export_data)             │
│  → Dapat Excel dengan External ID otomatis dari Odoo             │
│                                                                  │
│  STEP 2: Edit di Excel sesuai kebutuhan (hapus kolom/baris)       │
│                                                                  │
│  STEP 3: Import ke Target DB (Odoo ORM load)                     │
│  → Odoo ORM resolve External ID → DB ID secara otomatis         │
│  → Many2one fields pakai format: partner_id/id: base.res_partner_1│
└──────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Database Connection
Setiap project punya konfigurasi berbeda. Cek dulu:

| Project | HTTP Port | Database | Config |
|---------|-----------|----------|---------|
| roedl | 8133 | roedl_upgraded_20260331 | odoo19.conf |
| nok | 8170 | nok | odoo.conf |
| suqma | 8171 | suqma | odoo.conf |

### Credential
Default: `user=admin`, `password` sesuai project. Untuk execute, butuh login yang punya akses export/import.

---

## Step 1: Export (export_data ORM)

Gunakan Odoo shell atau RPC untuk export:

### Odoo Shell (direkomendasikan)
```bash
cd /path/to/odoo-source
source venv/bin/activate
python odoo-bin shell -c odoo.conf -d DATABASE -d db1 --no-interactive << 'EOF'
    # Export specific fields with external IDs
    records = env['model.name'].search([])
    result = records.export_data(['id', 'field1', 'partner_id/id', 'company_id/id'])
    print(result)
EOF
```

### Python RPC
```python
import odoorpc

# Connect to source DB
odoo = odoorpc.ODOO('http://localhost:PORT', timeout=60)
odoo.login('DATABASE', 'admin', 'PASSWORD')

model = odoo.env['model.name']
records = model.search([])
data = model.export_data(['id', 'field1', 'partner_id/id'])

# Save to file
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
for row_idx, row in enumerate(data['datas'], 2):
    for col_idx, val in enumerate(row, 1):
        ws.cell(row_idx, col_idx, val)
wb.save('/path/to/export.xlsx')
```

### Field Format untuk Export

| Field Type | Kolom di Excel | Contoh Nilai |
|------------|----------------|--------------|
| DB ID | `id` | `42` |
| External ID | `id` | `base.main_partner` |
| Many2one (DB ID) | `partner_id` | `22` |
| Many2one (Ext ID) | `partner_id/id` | `base.res_partner_22` |
| Char/Text | `name` | `John Doe` |

**Catatan:** Kolom `id` di Excel mengikuti format External ID dari `ir_model_data`. Jika record tidak punya external ID, Odoo akan generate `__export__.table_dbID_hash`.

---

## Step 2: Edit Excel

Guidelines:
- **Hapus kolom** yang tidak perlu di-import
- **Hapus baris** record yang tidak perlu
- **Jangan ubah kolom `id`** jika mau update existing records
- **Gunakan `partner_id/id`** untuk many2one dengan External ID
- **Jangan kosongkan `id`** jika mau create/update, kosongkan jika mau skip

### Konversi Table Name → Odoo Model Name
```
res_partner_bank → res.partner.bank
res_partner      → res.partner
account_invoice → account.move
```

---

## Step 3: Import (load ORM)

### Odoo Shell
```bash
python odoo-bin shell -c odoo.conf -d DATABASE --no-interactive << 'EOF'
    import openpyxl
    wb = openpyxl.load_workbook('/path/to/export.xlsx')
    ws = wb.active

    # Read header row
    headers = [cell.value for cell in ws[1]]
    # Read data rows
    rows = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]

    # Import
    result = env['model.name'].load(headers, rows)
    print("Import result:", result)
EOF
```

### Python RPC
```python
import openpyxl, odoorpc

odoo = odoorpc.ODOO('http://localhost:PORT', timeout=60)
odoo.login('DATABASE', 'admin', 'PASSWORD')

wb = openpyxl.load_workbook('/path/to/export.xlsx')
ws = wb.active

headers = [cell.value for cell in ws[1]]
rows = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]

model = odoo.env['model.name']
result = model.load(headers, rows)
print("Created IDs:", result.get('ids'))
print("Messages:", result.get('messages'))
```

### Import Options

```python
# With noupdate=True (update existing, skip missing)
env = odoo.env
ctx = {'noupdate': True, 'mode': 'init'}
result = model.with_context(ctx).load(headers, rows)

# With specific module context
ctx = {'module': '__import__', 'noupdate': False}
result = model.with_context(ctx).load(headers, rows)
```

---

## External ID Generation (Odoo ORM)

Odoo generate External ID via `BaseModel.__ensure_xml_id()` dengan format:

```
__export__.tableName_dbID_hash8char
```

Contoh: `__export__.res_partner_bank_2_5d96b266`

Komponen:
- `__export__` — module name (selalu fixed)
- `tableName` — nama tabel/model convention (`res_partner_bank`)
- `dbID` — integer primary key record
- `hash8char` — 8 karakter pertama UUID v4 hex (**random per export, tidak deterministic**)

**Source code Odoo (`odoo/orm/models.py:642-646`):**
```python
xids.update(
    (r.id, (modname, '%s_%s_%s' % (
        r._table,      # e.g., res_partner_bank
        r.id,          # e.g., 2
        uuid.uuid4().hex[:8]  # e.g., 5d96b266
    )))
    for r in missing
)
```

**Implikasi:** Hash ini random — tidak bisa di-generate ulang untuk record yang sama. Jika perlu stable External ID, buat manual dengan format `module.name` (misal di module custom).

---

## Konfigurasi Project Roedl

```bash
cd /Users/tri-mac/project/roedl
source venv19/bin/activate
ODOO_BIN=odoo19.0-roedl/odoo/odoo-bin
ODOO_CONF=odoo19.conf
DB_SOURCE=roedl_15_20260331      # Odoo 15
DB_TARGET=roedl_upgraded_20260331  # Odoo 19
```

**Export dari v15:**
```bash
echo "
records = env['res.partner.bank'].search([])
result = records.export_data(['id', 'acc_number', 'partner_id/id', 'company_id/id'])
print('Total:', len(result['datas']))
for row in result['datas'][:5]:
    print(row)
" | python $ODOO_BIN shell -c $ODOO_CONF -d $DB_SOURCE 2>/dev/null
```

**Export dari v19:**
```bash
echo "
records = env['res.partner.bank'].search([])
result = records.export_data(['id', 'acc_number', 'partner_id/id', 'company_id/id'])
print('Total:', len(result['datas']))
for row in result['datas'][:5]:
    print(row)
" | python $ODOO_BIN shell -c $ODOO_CONF -d $DB_TARGET 2>/dev/null
```

---

## Troubleshooting

### "External ID not found"
External ID tidak ada di target DB. Solusi:
1. Buat external ID manual di target DB
2. Gunakan format `__import__.model_dbID` untuk record baru
3. Export dari source dengan `--include-external-id`, lalu import dengan mode yang sama

### "id" column format untuk import
Odoo `load()` menerima:
- `id` kosong → create new record
- DB integer `id` → update existing (dengan `mode='init'`)
- External ID string → resolve via `ir_model_data`

### Field Many2one tidak resolve
Pastikan format kolom menggunakan suffix `/id`:
- `partner_id` → DB integer ID
- `partner_id/id` → External ID string (`module.name`)

### Import gagal dengan banyak errors
Gunakan `load()` dengan `context={'tracking_disable': True}` untuk speed:
```python
result = model.with_context(tracking_disable=True).load(headers, rows)
```

---

## Safety Rules

1. **SELALU backup** sebelum import ke production
2. **Export dulu** ke file Excel untuk review sebelum import
3. **Dry-run**: cek hasil export, edit sesuai kebutuhan, baru import
4. **External ID** tidak boleh duplicate dalam satu module
5. **JANGAN import ke database yang sedang berjalan** — stop Odoo service dulu jika bulk import
