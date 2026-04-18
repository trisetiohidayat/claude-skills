---
name: odoo19-export-import
description: >
  Export dan import data model Odoo 19 ke Excel via ORM native Odoo.
  Gunakan skill ini setiap kali user ingin:
  - Export data Odoo 19 ke Excel (CSV/XLSX) dengan field tertentu
  - Export dengan External ID column (`__export__.table_N_hash`)
  - Import data dari Excel/CSV ke Odoo 19 via ORM `load()`
  - Update field tertentu saja tanpa export semua kolom
  - Export hanya record yang dipilih (filter by domain)

  Trigger phrases: "export odoo 19", "export data model", "import excel ke odoo 19",
  "export to excel", "import from csv", "export specific fields",
  "export with external id", "dump data odoo", "export odoo model to csv"
---

# Odoo 19 Export & Import

## ⚠️ CRITICAL: External ID Stability

**`__ensure_xml_id()` uses `uuid.uuid4().hex[:8]` — RANDOM per call!**

But here's the KEY insight (tested in source code):
- **First `export_data()` call** → `__ensure_xml_id()` creates entries in `ir_model_data`, hash is RANDOM
- **Second `export_data()` call** → `__ensure_xml_id()` FINDS existing entries → REUSES same hash → **STABLE**

**CORRECT workflow — Call export TWICE:**

```bash
echo "
import openpyxl
from openpyxl.styles import Font, PatternFill

records = env['MODEL'].search([])

# STEP 1: First export → creates ir_model_data entries (hash=RANDOM)
records.export_data(['id'])

# STEP 2: Second export → REUSES entries, hash is STABLE
fields = ['id', 'acc_number', 'partner_id/id', 'company_id/id']
result = records.export_data(fields)

# Save to Excel
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Export Data'

hf = Font(bold=True, color='FFFFFF')
fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
for ci, h in enumerate(fields, 1):
    c = ws.cell(1, ci, h)
    c.font = hf
    c.fill = fill

for ri, row in enumerate(result['datas'], 2):
    for ci, v in enumerate(row, 1):
        ws.cell(ri, ci, v or '')

wb.save('~/Downloads/export.xlsx')
print('Saved', len(result['datas']), 'records with STABLE external IDs')
" | python odoo-bin shell -c odoo.conf -d DATABASE 2>/dev/null
```

**Why this works:**
- Step 1 creates 60 entries in `ir_model_data` (one-time RANDOM hash)
- Step 2 reuses those entries → same hash → stable IDs
- Import will resolve correctly because IDs exist in `ir_model_data`

---

## Export: export_data() ORM

### Field Format

| Field | Kolom `id` | Banyak External ID |
|-------|-----------|-------------------|
| DB integer ID | `id` → `22` | - |
| External ID string | `id` → `base.main_partner` | - |
| Many2one DB ID | `partner_id` → `22` | - |
| Many2one Ext ID | `partner_id/id` → `base.main_partner` | ✅ External ID untuk related record |

### Save to Excel

```bash
echo "
import openpyxl
from openpyxl.styles import Font, PatternFill

fields = ['id', 'acc_number', 'partner_id/id', 'company_id/id']
records = env['MODEL'].search([])
result = records.export_data(fields)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Export Data'

# Header from field list (NOT from result['datas'][0])
hf = Font(bold=True, color='FFFFFF')
fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
for ci, h in enumerate(fields, 1):
    c = ws.cell(1, ci, h)
    c.font = hf
    c.fill = fill

# Data rows
for ri, row in enumerate(result['datas'], 2):
    for ci, v in enumerate(row, 1):
        ws.cell(ri, ci, v or '')

wb.save('~/Downloads/export.xlsx')
print('Saved', len(result['datas']), 'records')
" | python odoo-bin shell -c odoo.conf -d DATABASE 2>/dev/null
```

> **CATATAN:** Header menggunakan `fields` list, BUKAN `result['datas'][0]` — karena `datas[0]` berisi data row pertama, bukan header.

---

## Import: load() ORM

### Basic Import

```bash
echo "
import openpyxl
wb = openpyxl.load_workbook('/path/to/file.xlsx')
ws = wb.active

headers = [cell.value for cell in ws[1]]
rows = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)
        if any(c.value for c in row)]

result = env['MODEL'].load(headers, rows)
print('IDs:', result.get('ids'))
print('Messages:', result.get('messages'))
" | python odoo-bin shell -c odoo.conf -d DATABASE 2>/dev/null
```

### Update Existing (mode='init')

```bash
echo "
import openpyxl
wb = openpyxl.load_workbook('/path/to/file.xlsx')
ws = wb.active
headers = [cell.value for cell in ws[1]]
rows = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)
        if any(c.value for c in row)]

result = env['MODEL'].with_context(mode='init').load(headers, rows)
print('IDs:', result.get('ids'))
" | python odoo-bin shell -c odoo.conf -d DATABASE 2>/dev/null
```

### Create Only (mode='create')

```bash
echo "
import openpyxl
wb = openpyxl.load_workbook('/path/to/file.xlsx')
ws = wb.active
headers = [cell.value for cell in ws[1]]
rows = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)
        if any(c.value for c in row)]

result = env['MODEL'].with_context(mode='create').load(headers, rows)
print('Created:', result.get('ids'))
" | python odoo-bin shell -c odoo.conf -d DATABASE 2>/dev/null
```

### Import Options

```python
.with_context(mode='init')          # Update existing, create new (default)
.with_context(mode='create')        # Create only, skip existing
.with_context(noupdate=True)        # Jangan overwrite existing record
.with_context(tracking_disable=True)  # Faster, no mail tracking
```

### id Column Rules

| Kolom `id` | Efek |
|------------|------|
| Kosong / `None` | Create new record |
| DB integer (misal `22`) | Update existing record by DB ID |
| `__export__.table_N_hash` | Resolve via `ir_model_data`, update if found |
| `module.name` | Resolve via `ir_model_data`, update if found |

---

## Project Config: Roedl

Workdir: `/Users/tri-mac/project/roedl`

```bash
source venv19/bin/activate
ODOO_BIN=odoo19.0-roedl/odoo/odoo-bin
ODOO_CONF=odoo19.conf
DB=roedl_upgraded_20260331
```

**Export:**
```bash
echo "
records = env['MODEL'].search([])
result = records.export_data(['id', 'field1', 'partner_id/id'])
print('Total:', len(result['datas']))
" | python $ODOO_BIN shell -c $ODOO_CONF -d $DB 2>/dev/null
```

**Export with Excel (Two-Call for STABLE IDs):**
```bash
echo "
import openpyxl
from openpyxl.styles import Font, PatternFill

records = env['MODEL'].search([])

# STEP 1: First export → creates ir_model_data entries (hash=RANDOM)
records.export_data(['id'])

# STEP 2: Second export → REUSES entries, hash is STABLE
fields = ['id', 'field1', 'partner_id/id']
result = records.export_data(fields)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Export Data'

hf = Font(bold=True, color='FFFFFF')
fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
for ci, h in enumerate(fields, 1):
    c = ws.cell(1, ci, h)
    c.font = hf
    c.fill = fill

for ri, row in enumerate(result['datas'], 2):
    for ci, v in enumerate(row, 1):
        ws.cell(ri, ci, v or '')

wb.save('/Users/tri-mac/Downloads/export.xlsx')
print('Saved', len(result['datas']), 'records with STABLE external IDs')
" | python $ODOO_BIN shell -c $ODOO_CONF -d $DB 2>/dev/null
```

> **CATATAN:** Header menggunakan `fields` list, BUKAN `result['datas'][0]` — karena `datas[0]` berisi data row pertama, bukan header.

---

## Troubleshooting

### "No matching record found for external id '__export__.*'" saat import

**PENYEBAB UTAMA:** Format `__export__.table_N_hash` adalah **auto-generated saat export** — ID ini RANDOM dan TIDAK ada di `ir_model_data` database target. Odoo tidak bisa resolve.

**Solusi:**

#### Solusi 1: Export langsung dari database yang sama (self-repair)
Jika export dan import di database yang SAMA, `__export__` ID akan match karena record di-create saat export pertama kali:

```bash
# Export dari database target itu sendiri
echo "
records = env['MODEL'].search([])
result = records.export_data(['id', 'acc_number', 'partner_id/id'])
# Edit Excel sesuai kebutuhan
# Import kembali ke database yang sama
" | python odoo-bin shell -c odoo.conf -d TARGET_DB 2>/dev/null
```

#### Solusi 2: Pakai DB integer ID (bukan External ID) untuk many2one

Export dengan DB integer ID, lalu import juga pakai DB integer ID:

```bash
# Export: partner_id tanpa /id suffix → DB integer
echo "
records = env['res.partner.bank'].search([])
result = records.export_data(['id', 'acc_number', 'partner_id'])
# partner_id = integer DB ID
" | python odoo-bin shell -c odoo.conf -d TARGET_DB 2>/dev/null
```

#### Solusi 3: Pakai proper `module.name` External ID (stable)

Proper external ID seperti `base.main_partner`, `__import__.res_partner_22` ada di `ir_model_data` dan akan resolve saat import:

```bash
# Cek apakah external ID ada di ir_model_data
echo "
ext = env['ir.model.data'].search_read([
    ('model', '=', 'res.partner'),
    ('name', 'ilike', 'res_partner_22')
], ['id', 'name', 'module', 'res_id'])
print('Found:', ext)
" | python odoo-bin shell -c odoo.conf -d TARGET_DB 2>/dev/null
```

#### Solusi 4: Generate `__export__` ID dulu di target DB

```bash
# Buat __export__ external ID untuk semua partner di target DB
# dengan iterate melalui shell
echo "
records = env['MODEL'].search([])
# Trigger __ensure_xml_id untuk create entries di ir_model_data
for rec in records:
    pass  # accessing record triggers __ensure_xml_id
result = records.export_data(['id'])
print('Created __export__ IDs for', len(result['datas']), 'records')
" | python odoo-bin shell -c odoo.conf -d TARGET_DB 2>/dev/null
```

### Field Many2one tidak resolve
Pastikan kolom gunakan suffix `/id`:
- `partner_id` → DB integer ID (selalu resolve)
- `partner_id/id` → External ID string

### Import skip existing record
Pakai `mode='init'` (default) — Odoo update jika `id` cocok, create jika `id` kosong.

### Banyak error saat import
```python
.with_context(tracking_disable=True, no_mail_thread=True)
```

---

## Safety

1. **Backup** sebelum import ke database production
2. **Export dulu** ke Excel, review/edit, baru import
3. **JANGAN import ke database yang sedang running** jika bulk data
4. **Stop Odoo service** untuk bulk import via shell
