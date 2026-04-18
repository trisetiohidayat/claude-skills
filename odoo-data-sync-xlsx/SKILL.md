---
name: odoo-data-sync-xlsx
description: >
  Export dan import data Odoo ke/dari Excel untuk keperluan migrasi, recovery, atau sync data antar database Odoo.
  Gunakan skill ini setiap kali user ingin:
  - Export data Odoo ke Excel (CSV/XLSX) dengan atau tanpa External ID
  - Import data dari Excel ke Odoo database menggunakan DB ID atau External ID
  - Recovery data yang hilang setelah upgrade (seperti company_id di res.partner.bank)
  - Sync atau bandingkan data antar Odoo 15 dan Odoo 19
  - Backup data tertentu dalam format spreadsheet yang bisa langsung diimport ulang

  Trigger phrases: "export excel", "import excel", "recovery data", "sync data", "migrasi data",
  "company_id hilang", "export ke csv", "import dari csv", "backup data ke excel",
  "external id", "xml id", "buat file import odoo"

  Tools: Bash (psql), Python (openpyxl, psycopg2)
---

# Odoo Data Sync via Excel

## Purpose

Export dan import data Odoo melalui Excel/CSV, dengan dukungan penuh untuk:
- **External ID** (XML ID) — format standar Odoo yang portabel antar database
- **DB ID** — integer primary key untuk operasi cepat dalam satu database
- **Field matching** — match berdasarkan nilai field (seperti acc_number)

---

## Konsep: DB ID vs External ID

Dalam Odoo ada dua cara mengidentifikasi record:

| Jenis | Contoh | Kapan Digunakan |
|-------|--------|-----------------|
| **DB ID** | `22` | Satu database, operasi cepat |
| **External ID** | `base.res_partner_22` | Lintas database, import resmi Odoo |

External ID disimpan di tabel `ir_model_data` dengan format `module.name`.

**Kenapa External ID lebih baik untuk migrasi:**
- DB ID bisa berbeda antar database (record yang sama bisa ID 22 di DB lama, ID 3017 di DB baru)
- External ID stabil dan bisa di-resolve di database mana pun
- Format yang digunakan Odoo UI saat Export/Import

---

## Alur Kerja Recovery Data

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: EXPORT dari Source DB                              │
│  export_data.py --include-external-id                       │
│  → Kolom "id" berisi External ID (base.res_partner_22)      │
│                                                             │
│  STEP 2: REVIEW & EDIT di Excel                             │
│  → User bisa edit nilai, hapus baris yang tidak perlu       │
│                                                             │
│  STEP 3: IMPORT ke Target DB                                │
│  import_data.py --use-external-id ATAU --match-field id     │
│  → Script resolve External ID → DB ID di target database    │
└─────────────────────────────────────────────────────────────┘
```

---

## Script 1: export_data.py

### Mode Export

**Mode 1: DB ID biasa (default)**
```bash
python export_data.py \
  --database roedl_15_20260331 \
  --model res_partner_bank \
  --output ~/Downloads/export.xlsx \
  --fields id,acc_number,partner_id,company_id
```

**Mode 2: Dengan External ID di kolom `id`**
```bash
python export_data.py \
  --database roedl_15_20260331 \
  --model res_partner_bank \
  --output ~/Downloads/export.xlsx \
  --fields id,acc_number,partner_id,company_id \
  --include-external-id
# Kolom "id" akan berisi: "__import__.res_partner_bank_22"
```

**Mode 3: Odoo-compatible format (External ID untuk semua many2one)**
```bash
python export_data.py \
  --database roedl_15_20260331 \
  --model res.partner.bank \
  --output ~/Downloads/export.xlsx \
  --fields id,acc_number,partner_id,company_id \
  --odoo-format
# Output: kolom "id" (ext id record), "partner_id/id" (ext id partner), "company_id/id" (ext id company)
```

**Mode 4: Related fields tertentu sebagai External ID**
```bash
python export_data.py \
  --database roedl_15_20260331 \
  --model res_partner_bank \
  --output ~/Downloads/export.xlsx \
  --fields id,acc_number,partner_id,company_id \
  --include-external-id \
  --related-as-external-id partner_id,company_id
# Menambahkan kolom partner_id/id dan company_id/id di samping nilai aslinya
```

### Parameter export_data.py

| Parameter | Default | Fungsi |
|-----------|---------|--------|
| `--database` | (required) | Nama database PostgreSQL |
| `--model` | (required) | Nama model Odoo (titik atau underscore) |
| `--output` | (required) | Path output (.xlsx atau .csv) |
| `--fields` | `*` | Fields yang di-export (comma-separated) |
| `--where` | `1=1` | Kondisi WHERE untuk filter |
| `--limit` | `0` (no limit) | Batas jumlah record |
| `--include-external-id` | off | Ganti kolom `id` dengan External ID |
| `--odoo-format` | off | Format Odoo import (id + many2one/id) |
| `--related-as-external-id` | `''` | Kolom many2one yang dijadikan ext id |

---

## Script 2: import_data.py

### Mode Import

**Mode 1: Match by DB id (integer)**
```bash
python import_data.py \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/fix.xlsx \
  --match-field id \
  --update-fields partner_id \
  --dry-run
```

**Mode 2: Match by External ID (kolom `id` berisi module.name)**
```bash
python import_data.py \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/fix.xlsx \
  --use-external-id \
  --update-fields partner_id \
  --dry-run
```

**Mode 3: Update many2one field menggunakan External ID (kolom `partner_id/id`)**
```bash
python import_data.py \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/fix.xlsx \
  --match-field acc_number \
  --update-fields partner_id/id,company_id/id \
  --dry-run
# Script akan resolve partner_id/id (external id) → DB id sebelum UPDATE
```

**Mode 4: Match field + External ID update**
```bash
python import_data.py \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/fix.xlsx \
  --match-field acc_number \
  --update-fields partner_id/id \
  --dry-run
```

### Parameter import_data.py

| Parameter | Default | Fungsi |
|-----------|---------|--------|
| `--database` | (required) | Nama database PostgreSQL |
| `--model` | (required) | Nama model Odoo |
| `--input` | (required) | Path file Excel/CSV |
| `--match-field` | `id` | Kolom untuk match record |
| `--update-fields` | (required) | Field yang di-update. Gunakan `/id` suffix untuk external ID (contoh: `partner_id/id`) |
| `--use-external-id` | off | Kolom `id` berisi External ID untuk match |
| `--create-missing` | off | INSERT jika record tidak ditemukan |
| `--dry-run` | off | Preview saja, tidak execute |
| `--sheet` | `Export Data` | Sheet Excel yang dibaca |
| `--batch-size` | `100` | Jumlah record per batch |

### Format Kolom di Excel untuk Import

| Nama Kolom | Isi | Keterangan |
|-----------|-----|-----------|
| `id` | `22` (integer) | DB id — dipakai dengan `--match-field id` |
| `id` | `base.res_partner_22` | External ID — dipakai dengan `--use-external-id` |
| `partner_id` | `22` | DB id dari related partner |
| `partner_id/id` | `base.res_partner_22` | External ID dari related partner |
| `company_id/id` | `base.main_company` | External ID dari related company |

---

## Database Configuration (Roedl Project)

| Version | Database | Port |
|---------|----------|------|
| Odoo 15 | `roedl_15_20260331` | 8115 |
| Odoo 19 | `roedl_upgraded_20260331` | 8119 |

Credentials PostgreSQL: `host=localhost user=odoo password=odoo port=5432`

---

## Contoh Workflow: Recovery partner_id di res.partner.bank

```bash
# 1. Export dari v15 dengan External ID
python export_data.py \
  --database roedl_15_20260331 \
  --model res_partner_bank \
  --output ~/Downloads/rpb_v15.xlsx \
  --fields id,acc_number,partner_id,company_id \
  --odoo-format

# File mengandung kolom: id, acc_number, partner_id/id, company_id/id

# 2. Dry run import ke v19 menggunakan external ID untuk match dan update
python import_data.py \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/rpb_v15.xlsx \
  --use-external-id \
  --update-fields partner_id/id,company_id/id \
  --dry-run

# 3. Execute jika preview OK (hapus --dry-run)
python import_data.py \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/rpb_v15.xlsx \
  --use-external-id \
  --update-fields partner_id/id,company_id/id
```

---

## Safety Rules

1. **SELALU gunakan `--dry-run` terlebih dahulu** — script akan menampilkan semua perubahan tanpa mengeksekusi
2. **Backup database** jika data kritis (gunakan skill `odoo-db-management`)
3. **Verify match field** 100% match sebelum execute
4. **JANGAN import ke database production** tanpa konfirmasi user
5. **External ID tidak wajib ada** — jika record tidak punya entry di `ir_model_data`, export akan generate ID sementara `__import__.table_id`

---

## Troubleshooting

### "External ID 'xyz' not found"
Record ada di source DB tapi tidak punya External ID yang dikenali di target DB.
```sql
-- Cek apakah external ID ada di target
SELECT * FROM ir_model_data WHERE module = 'base' AND name = 'res_partner_22';
```

### "Table not found"
Nama model salah. Odoo model `res.partner.bank` → tabel PostgreSQL `res_partner_bank`.
Script otomatis convert, tapi pastikan model yang ditulis benar.

### "Column not in table"
Field yang di-update tidak ada di versi Odoo target (misal field baru di v19).
```bash
# Cek kolom yang tersedia
PGPASSWORD=odoo psql -h localhost -U odoo -d DB -c "\d res_partner_bank"
```
