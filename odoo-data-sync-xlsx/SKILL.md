---
name: odoo-data-sync-xlsx
description: >
  Export dan import data Odoo ke/dari Excel untuk keperluan migrasi, recovery, atau sync data antar database Odoo.
  Gunakan skill ini setiap kali user ingin:
  - Export data Odoo ke Excel (CSV/XLSX)
  - Import data dari Excel ke Odoo database
  - Recovery data yang hilang setelah upgrade (seperti company_id di res.partner.bank)
  - Sync atau bandingkan data antar Odoo 15 dan Odoo 19
  - Backup data tertentu dalam format spreadsheet

  Trigger phrases: "export excel", "import excel", "recovery data", "sync data", "migrasi data",
  "company_id hilang", "export ke csv", "import dari csv", "backup data ke excel"

  Tools: Bash (psql), Python (openpyxl, csv)
---

# Odoo Data Sync via Excel

## Purpose

Skill ini membantu export dan import data Odoo melalui Excel/CSV files, khusus untuk:
- **Export**: Ambil data dari Odoo database (PostgreSQL) → Excel
- **Import**: Baca Excel → Update/Create records di Odoo database
- **Recovery**: Restore field yang hilang setelah upgrade (seperti `company_id` di `res.partner.bank`)

## Konsep Penting

### Database & Server Configuration (Roedl Project)

**Odoo 15:**
| Property | Value |
|----------|-------|
| Database | `roedl_15_20260331` |
| HTTP Port | 8115 |
| Status | Running |
| PostgreSQL Host | localhost |
| PostgreSQL User | odoo |
| PostgreSQL Password | odoo |

**Odoo 19 (Upgraded):**
| Property | Value |
|----------|-------|
| Database | `roedl_upgraded_20260331` |
| HTTP Port | 8119 |
| Status | Running |
| PostgreSQL Host | localhost |
| PostgreSQL User | odoo |
| PostgreSQL Password | odoo |

### Alur Kerja Recovery Data

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: EXPORT dari Odoo 15 (Source)                     │
│  - Gunakan scripts/export_data.py                           │
│  - Target: ~/Downloads/odoo_export_[model]_[date].xlsx    │
│                                                             │
│  STEP 2: REVIEW & VALIDASI di Excel                        │
│  - User bisa edit manual jika perlu                        │
│  - Pastikan key fields (acc_number) match 100%              │
│                                                             │
│  STEP 3: IMPORT ke Odoo 19 (Target)                        │
│  - Gunakan scripts/import_data.py                           │
│  - Match berdasarkan key fields                             │
│  - Update field yang perlu di-recovery                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Export Data dari Odoo

### Command untuk Export

Gunakan `scripts/export_data.py`:

```bash
python scripts/export_data.py \
  --db-host localhost \
  --db-port 5432 \
  --db-user odoo \
  --db-password odoo \
  --database roedl_15_20260331 \
  --model res_partner_bank \
  --output ~/Downloads/odoo_export_res_partner_bank_20260331.xlsx \
  --fields id,acc_number,sanitized_acc_number,acc_holder_name,partner_id,bank_id,currency_id,company_id
```

### Field yang Direkomendasikan untuk Export

**res_partner_bank:**
| Field | Description | Wajib? |
|-------|-------------|--------|
| `id` | Record ID | Ya |
| `acc_number` | Account Number (key matching) | Ya |
| `sanitized_acc_number` | Cleaned account number | Ya |
| `acc_holder_name` | Account holder name | Ya |
| `partner_id` | Partner ID | Ya |
| `bank_id` | Bank reference ID | No |
| `currency_id` | Currency ID | No |
| `company_id` | **TARGET FIELD** - yang perlu di-recovery | Ya |

### Validasi Export

Pastikan file Excel sudah benar:
1. Buka file Excel
2. Check kolom `company_id` ada nilainya (tidak NULL untuk data yang perlu di-recovery)
3. Check `acc_number` tidak ada duplikat
4. Total row sesuai ekspektasi

---

## Step 2: Import Data ke Odoo

### Command untuk Import

Gunakan `scripts/import_data.py`:

```bash
python scripts/import_data.py \
  --db-host localhost \
  --db-port 5432 \
  --db-user odoo \
  --db-password odoo \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/odoo_export_res_partner_bank_20260331.xlsx \
  --match-field acc_number \
  --update-fields company_id \
  --dry-run
```

### Flag Penting

| Flag | Fungsi |
|------|--------|
| `--dry-run` | Preview saja, tidak execute UPDATE |
| `--batch-size` | Jumlah records per batch (default: 100) |
| `--match-field` | Field untuk match record (default: id) |
| `--update-fields` | Field yang akan di-update |
| `--create-missing` | Buat record baru jika tidak ditemukan |

### Dry Run Output

Contoh output dry-run:
```
=== DRY RUN - Preview Perubahan ===
Total records in file: 61
Matched records in DB: 60
Will UPDATE: 60 records
Will CREATE: 0 records
Will SKIP: 1 record (no match)

Preview perubahan:
  ID=71: company_id 1 → 1 (no change, will skip)
  ID=72: company_id NULL → 2 (will update)
  ...
```

### Execute Import

Setelah validasi dry-run OK, jalankan tanpa `--dry-run`:

```bash
python scripts/import_data.py \
  --db-host localhost \
  --db-port 5432 \
  --db-user odoo \
  --db-password odoo \
  --database roedl_upgraded_20260331 \
  --model res_partner_bank \
  --input ~/Downloads/odoo_export_res_partner_bank_20260331.xlsx \
  --match-field acc_number \
  --update-fields company_id
```

---

## Step 3: Verifikasi Hasil

### Check di Database

```sql
-- Check hasil import
SELECT company_id, COUNT(*)
FROM res_partner_bank
GROUP BY company_id;
```

Expected output setelah recovery:
```
 company_id | count
------------+------
          1 |    23
          2 |    10
       NULL |     0
(3 rows)
```

### Check di Odoo UI

1. Buka Odoo 19 di browser (http://localhost:8119)
2. Login sebagai admin
3. Navigate ke: Contacts → Configuration → Bank Accounts
4. Verify bahwa `company_id` sudah ter-set dengan benar

---

## Troubleshooting

### Error: "relation does not exist"

Pastikan database name correct:
```bash
# List available databases
PGPASSWORD=odoo psql -h localhost -U odoo -l
```

### Error: "permission denied"

Pastikan PostgreSQL credentials benar:
- User: `odoo`
- Password: `odoo`

### Error: "no such column"

Nama field berbeda antar versi. Check column names:
```sql
-- Di Odoo 15
\d res_partner_bank

-- Di Odoo 19
\d res_partner_bank
```

### Warning: "company_id will become NULL"

Jika partner company memiliki `company_id=NULL` secara default di Odoo 19, maka hasil computed `related('partner_id.company_id')` juga NULL.
Ini normal di Odoo 19 - partner yang IS A COMPANY tidak punya `company_id`.

---

## Model yang Umum untuk Migrasi

| Model | Use Case |
|-------|----------|
| `res_partner_bank` | Bank accounts - company_id recovery |
| `res_partner` | Contacts/Companies |
| `account_move` | Invoices/Journal Entries |
| `product_product` | Products |
| `stock_quant` | Inventory |

---

## Safety Rules

1. **SELALU gunakan `--dry-run` terlebih dahulu**
2. **Backup database sebelum import** jika data kritis
3. **Export data target terlebih dahulu** untuk perbandingan
4. **Verify match field** 100% sebelum execute
5. **JANGAN import ke database production** tanpa konfirmasi user
