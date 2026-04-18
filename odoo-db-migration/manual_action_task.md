# Post-Upgrade Manual Action Tasks

## Overview

Setelah upgrade database berhasil (misalnya dari Odoo 15.0 ke 19.0 via upgrade.odoo.com), ada beberapa **manual action tasks** yang perlu dilakukan secara manual karena tidak bisa di-handle oleh proses upgrade otomatis.

File ini adalah **checklist** untuk memastikan semua data dan konfigurasi pasca-upgrade sudah benar.

---

## Kategori Manual Action Tasks

### 1. Custom Modules - Migrasi atau Disable

**7 modul custom** yang tidak bisa di-upgrade otomatis perlu ditangani:

```
asft_employee_payroll    → EE-only, perlu migrasi khusus
asb_setting_accounting   → Perlu cek manifest & dependencies
asb_timesheets_invoice   → Perlu cek manifest & dependencies
asb_project             → Perlu migrasi
asb_project_followers    → Perlu migrasi
asb_calendar_feature     → Perlu migrasi
asb_account_reports     → Custom account types perlu di-disable
```

**File SQL Fix (dari upgrade process):**
```sql
-- Set state='to upgrade' untuk preserve
UPDATE ir_module_module SET state = 'to upgrade'
WHERE name IN (
    'asb_timesheets_invoice', 'asft_employee_payroll',
    'asb_setting_accounting', 'asb_calendar_feature',
    'asb_project', 'asb_account_reports', 'asb_project_followers'
);

-- Audit table untuk tracking
CREATE TABLE IF NOT EXISTS migration_modules_to_upgrade (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(100),
    current_state VARCHAR(50),
    reason TEXT,
    needs_upgrade BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    migrated_at TIMESTAMP
);
```

**Steps:**
1. [ ] Migrasi setiap modul ke versi target
2. [ ] Atau set ke `state='uninstalled'` jika tidak diperlukan
3. [ ] Update `ir_module_module` dengan state baru

---

### 2. Views yang Dinonaktifkan (Auto-Disabled)

**23 view** dinonaktifkan otomatis karena inheritance XPath tidak valid:

| View ID | Nama | Masalah |
|---------|------|---------|
| 383 | (custom) | XPath `action_assign_to_me` tidak ditemukan |
| 514 | (custom) | XPath `action_assign_to_me` tidak ditemukan |
| 705 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 741 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 773 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 809 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1114 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1388 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1406 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1413 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1432 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1514 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1523 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1758 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1851 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1854 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1895 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 1969 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 2105 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 2160 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 2168 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |
| 2193 | (custom) | XPath `settings/data-key='account'` tidak ditemukan |

**XPath fixes yang diperlukan:**
```
//field[@name='deposit_taxes_id']     → Field dihapus di Odoo 17+
//div[hasclass('settings')]/div[@data-key='account']  → Struktur Settings berubah
//button[@name='action_assign_to_me']  → Button/action dihapus
```

**Steps:**
1. [ ] Identifikasi view apa yang digunakan user
2. [ ] Rekreasi view dengan XPath yang valid untuk versi baru
3. [ ] Atau hapus view jika tidak diperlukan
4. [ ] Enable view dengan: `UPDATE ir_ui_view SET active = true WHERE id = <id>;`

**Query untuk cek view yang disabled:**
```sql
SELECT id, name, model, type
FROM ir_ui_view
WHERE active = false
ORDER BY model;
```

---

### 3. Custom Financial Reports (Tidak Dimigrasikan)

**Laporan kustom** yang TIDAK dimigrasikan oleh Odoo upgrade:

| Report ID | Nama | Notes |
|-----------|------|-------|
| 8 | Balance Sheet (New Version) | Revamp total reporting engine |

**Steps:**
1. [ ] Identifikasi isi laporan yang hilang
2. [ ] Rekreasi laporan menggunakan Odoo Report Designer
3. [ ] Atau hubungi Odoo support untuk migrasi custom reports
4. [ ] Export laporan lama dari versi sebelumnya jika ada backup

---

### 4. Partner - Pricelist Cross-Company Fix

**27+ partners** menggunakan pricelist dari company yang berbeda — semua di-unassign otomatis:

**Partners yang affected (sebagian):**
```
Dennis Vogt (#1148)          → pricelist di-unassign
Heinrich Brechmann (#1149)   → pricelist di-unassign
Herr Dirk Stumpe (#1150)     → pricelist di-unassign
Herr Neil Hirst (#1151)      → pricelist di-unassign
Mustan Tan (#1153)           → pricelist di-unassign
Thomas Gössling (#1152)      → pricelist di-unassign
Michael Rausch (#104)        → pricelist di-unassign
+ 20+ lainnya...
```

**Steps:**
1. [ ] Export list partners yang pricelist-nya di-unassign
2. [ ] Buat pricelist yang sesuai untuk setiap company
3. [ ] Assign pricelist ke partners yang sesuai
4. [ ] Verifikasi tidak ada cross-company assignment lagi

**Query untuk identifikasi:**
```sql
-- Partners yang pricelist di-unassign
SELECT r.name, r.id, pp.property_product_pricelist
FROM res_partner rp
JOIN res_partner r ON rp.commercial_partner_id = r.id
WHERE rp.property_product_pricelist IS NULL
  AND r.customer_rank > 0;

-- Cek cross-company pricelist
SELECT rp.name, rp.id, pp.name as pricelist, rc.name as company
FROM res_partner rp
JOIN res_company rc ON rp.company_id = rc.id
JOIN product_pricelist pp ON rp.property_product_pricelist = pp.id
WHERE pp.company_id IS DISTINCT FROM rp.company_id;
```

---

### 5. Time Off Allocations (Dihapus)

**2 allocation** di state Draft/Cancel dihapus karena tidak valid di Odoo 17+:

**Steps:**
1. [ ] Identifikasi employees yang allocation-nya dihapus
2. [ ] Buat allocation baru untuk employee tersebut
3. [ ] Komunikasikan ke employees jika perlu

---

### 6. Server Actions / Fields yang Berubah

**ir.actions.server** yang perlu di-update karena field rename:

| Action ID | Action Name | Field Yang Berubah |
|-----------|-------------|-------------------|
| 571 | Mark as lost | `product.template.type` → `detailed_type` |
| 612 | Set Payment Status Paid | `report.project.task.user.state` → `kanban_state` |
| 683 | Base: Activate Private Address Recycling | Multiple field renames |

**Field Rename Summary per Version:**

**Odoo 16:**
| Model | Field Lama | Field Baru |
|-------|-----------|------------|
| `account.invoice.send` | `res_id` | `composer_id.res_id` |

**Odoo 17:**
| Model | Field Lama | Field Baru |
|-------|-----------|------------|
| `hr.employee` | `phone` | `private_phone` |
| `report.project.task.user` | `state` | `kanban_state` |
| `report.project.task.user.fsm` | `state` | `kanban_state` |
| `spreadsheet.dashboard` | `data` | `spreadsheet_binary_data` |

**Odoo 18:**
| Model | Field Lama | Field Baru |
|-------|-----------|------------|
| `product.template` | `type` | `detailed_type` |
| `product.product` | `type` | `detailed_type` |
| `product.product` | `type` | `product_tmpl_id.detailed_type` |
| `account.payment` | `ref` | `memo` |
| `account.payment` | `payment_state` | `move_id.payment_state` |

**Odoo 19:**
| Model | Field Lama | Field Baru |
|-------|-----------|------------|
| `hr.employee` | `phone` | `user_id.phone` |
| `hr.employee.public` | `phone` | `user_id.phone` |
| `hr.employee.public` | `email` | `user_id.email` |

**Steps:**
1. [ ] Cek ir.actions.server yang affected
2. [ ] Update field references di action code
3. [ ] Test setiap action untuk memastikan berfungsi

---

### 7. Private Address Handling (Odoo 17+)

Private addresses dipindahkan dan perlu follow-up:

| Tipe | Action |
|------|--------|
| Employee private address | Dipindahkan ke `hr.employee` model |
| Applicant private address | Dipindahkan ke `hr.applicant` model |
| Other private addresses | Di-archive dengan tag "Old Private Address" |

**Steps:**
1. [ ] Klik tombol "Recycle Private Addresses" di UI (Admin only)
2. [ ] Verifikasi data employee private address lengkap
3. [ ] Cek applicant private address di hr.applicant
4. [ ] Audit archived private addresses

---

### 8. Mail Alias Domain Migration (Odoo 17)

Alias domain `localhost` dimigrasikan ke model `mail.alias.domain`:

**Steps:**
1. [ ] Cek mail.alias.domain yang baru dibuat
2. [ ] Verifikasi semua alias menggunakan domain yang benar
3. [ ] Set default domain untuk setiap company

---

### 9. Missing Filestore Files

**9 file** tidak ditemukan di filestore (biasanya aman untuk diabaikan):

**Steps:**
1. [ ] Identifikasi attachment yang file-nya hilang
2. [ ] Jika attachment penting, restore dari backup filestore
3. [ ] Jika tidak penting, biarkan saja

**Query untuk identifikasi:**
```sql
SELECT id, name, res_model, res_id, db_datas
FROM ir_attachment
WHERE db_datas IS NOT NULL
  AND store_fname IS NULL;
```

---

### 10. Partner - Commercial Partner Alignment

**1 partner** di-assign ke company berbeda dari commercial partner:

| Partner | Di-assign ke | Commercial Partner Company |
|---------|-------------|--------------------------|
| Egbert Freiherr von Cramm | Andi Gunawan & Associates | (berbeda) |

**Steps:**
1. [ ] Evaluasi apakah alignment ini benar
2. [ ] Update jika perlu

---

## Quick Checklist - Post Upgrade

```
SEBELUM RESTORE KE PRODUCTION:
=========================================

PRE-RESTORE CHECKLIST:
□  Backup production database
□  Backup filestore
□  Test restore di staging environment
□  Catat semua custom modules yang perlu dimigrasi

IMMEDIATE POST-UPGRADE (Staging):
□  [ ] Cek module states — 7 custom modules
□  [ ] Cek disabled views — 23 views
□  [ ] Migrasi/disable custom modules
□  [ ] Update ir.actions.server field references
□  [ ] Assign pricelists ke partners
□  [ ] Rekreasi custom financial reports
□  [ ] Re-create time off allocations
□  [ ] Klik "Recycle Private Addresses"
□  [ ] Verifikasi mail alias domains
□  [ ] Cek employee/applicant private addresses

PRE-PRODUCTION CHECKLIST:
□  [ ] Semua TransactionCase tests pass
□  [ ] Semua HttpCase tests pass
□  [ ] User acceptance testing selesai
□  [ ] Dokumentasi update selesai
□  [ ] Training user jika ada fitur baru
□  [ ] Monitoring setup untuk error tracking
```

---

## File Reference dari Upgrade Process

File SQL fix yang di-generate saat upgrade process:

```
migration_YYYYMMDD_HHMMSS/upgrade_logs/run_001/fix_run001.sql
```

**Contents:**
- VIEW FIXES (23 views disabled)
- MODULE FIXES (7 custom modules set to 'to upgrade')
- TRACKING TABLE (migration_fix_sql)
- ERROR ANALYSIS SUMMARY

**Tracking tables yang dibuat:**
```sql
migration_fix_sql        -- Record setiap fix yang diterapkan
migration_modules_to_upgrade  -- Audit custom module migration
```

---

## Version-Specific Notes

### Odoo 15 → 16
- Financial reporting engine dirombak total
- Custom reports TIDAK dimigrasikan
- View inheritance untuk settings berubah

### Odoo 16 → 17
- Private addresses dipindahkan
- Time off allocation states berubah
- Mail alias domains dimigrasikan
- `phone` field di hr.employee di-rename

### Odoo 17 → 18
- `product.template.type` → `detailed_type`
- `product.product.type` → `detailed_type`
- `account.payment.ref` → `memo`
- `state` → `kanban_state` di project reports
- Tax Name/Address fields deprecated

### Odoo 18 → 19
- `hr.employee.phone` → `user_id.phone`
- `hr.employee.public.phone` → `user_id.phone`
- `hr.employee.public.email` → `user_id.email`

---

## Useful SQL Queries

```sql
-- 1. Cek semua view yang di-disable
SELECT id, name, model, type, arch_db
FROM ir_ui_view
WHERE active = false;

-- 2. Cek module states
SELECT name, state, latest_version
FROM ir_module_module
WHERE name IN (
    'asb_timesheets_invoice', 'asft_employee_payroll',
    'asb_setting_accounting', 'asb_calendar_feature',
    'asb_project', 'asb_account_reports', 'asb_project_followers'
);

-- 3. Cek ir.actions.server yang affected
SELECT id, name, model, action_server_xml_id
FROM ir_actions_server
WHERE id IN (571, 612, 683);

-- 4. Cek migration fix records
SELECT fix_name, fix_category, status
FROM migration_fix_sql
ORDER BY created_at DESC;

-- 5. Cek modules needing migration
SELECT module_name, current_state, reason
FROM migration_modules_to_upgrade;
```
