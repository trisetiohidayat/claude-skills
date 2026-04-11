---
name: odoo-investigate-before-fix
description: >
  HANYA trigger untuk REQUEST PERBAIKAN/DEBUGGING yang spesifik.

  TRIGGER (WAJIB ada minimal 1 dari situasi ini):
  - User menyebut error message/exception spesifik (misal: "AccessError", "ValidationError", "View types not defined")
  - User menyebut nama bug atau issue number (misal: "bug di PO line", "issue #123")
  - User meminta cara修复合正 bug/kesalahan
  - User mengatakan sesuatu "tidak jalan", "error", "gagal", "crash"
  - Konteks jelas这是一个 debugging/migration task

  JANGAN trigger untuk:
  - Penjelasan/tutorial/belajar cara kerja (→ gunakan odoo-vault-base-context)
  - Step-by-step panduan operasi
  - Memahami field/model/API secara umum
  - Pertanyaan konseptual tanpa error
  - Kode baru yang ingin dibuat dari nol

  ATURAN: Selalu investigasi source code terlebih dahulu SEBELUM rekomendasi fix.
  Jangan pernah memberikan solusi perbaikan berdasarkan asumsi tanpa bukti dari source code.

  # Penggunaan Path Resolver

  Gunakan odoo_path_resolver untuk mendapatkan path yang benar:

  ```python
  from odoo_path_resolver import resolve

  paths = resolve()
  odoo19_ce = paths['odoo']['ce']['path']        # Odoo 19 CE source
  odoo19_ee = paths['odoo']['ee']['path']        # Odoo 19 EE source
  odoo15_ce = paths['odoo15']['ce']['path']     # Odoo 15 CE source
  custom = paths['project']['custom_addons']     # Custom modules
  ```
---

# Odoo Investigate Before Fix

## Aturan Utama

**JANGAN PERNAH membuat rekomendasi perbaikan berdasarkan asumsi!**

Setiap kali ada error atau bug:
1. **Investigasi DULU** - Cek source code yang relevan
2. **Cari bukti** - Temukan bukti nyata di codebase
3. **Verifikasi** - Pastikan penyebabnya sebelum menyarankan perbaikan

## Step-by-Step Investigation

### Step 1: Identifikasi Lokasi Error

Dari error message, identifikasi:
- Module name (contoh: `asft_employee_payroll`)
- Model name (contoh: `hr.master.ump`)
- Field name (contoh: `l10n_id_tax_number`)

### Step 2: Cek Custom Modules

```bash
# Cari di custom addons
grep -r "pattern" /path/to/custom_addons_roedl/
```

### Step 3: Cek Odoo CE Source

```bash
# Cari di Odoo CE (gunakan paths dari resolve())
# paths['odoo']['ce']['path']
grep -r "pattern" <CE_SOURCE_PATH>/addons/
```

### Step 4: Cek Odoo EE Source (jika ada)

```bash
# Cari di Odoo EE (gunakan paths dari resolve())
# paths['odoo']['ee']['path']
grep -r "pattern" <EE_SOURCE_PATH>/
```

### Step 5: Bandingkan dengan Versi Lama (jika perlu migration)

```bash
# Cek di Odoo 15 (gunakan paths dari resolve())
# paths['odoo15']['ce']['path']
grep -r "pattern" <Odoo15_CE_PATH>/addons/
```

## Contoh Investigation

### Error: "View types not defined tree"

**SALAH (Asumsi):**
"Kemungkinan view mode salah"

**BENAR (Investigasi):**
```bash
# Step 1: Cari view XML di custom module
# (gunakan paths['project']['custom_addons'])
grep -r "view_mode.*tree" <CUSTOM_MODULES_PATH>/asft_employee_payroll/

# Hasil: master_ump.xml:20: <field name="view_mode">tree</field>

# Step 2: Cek Odoo 19 CE untuk syntax yang benar
# (gunakan paths['odoo']['ce']['path'])
grep -r "view_mode.*list" <CE_SOURCE_PATH>/addons/ | head -5

# Hasil: sale/views/sale_order_views.xml:1022: <field name="view_mode">list</field>

# Kesimpulan: Ganti "tree" -> "list" di Odoo 19
```

### Error: "field is undefined"

**SALAH (Asumsi):**
"Field tersebut tidak ada di database"

**BENAR (Investigasi):**
```bash
# Step 1: Cari definisi field di Odoo 19
# (gunakan paths['odoo']['ce']['path'])
grep -r "l10n_id_tax_number" <CE_SOURCE_PATH>/addons/
# Hasil: TIDAK ADA - field tidak ada di Odoo 19

# Step 2: Cek di Odoo 15 (migration context)
# (gunakan paths['odoo15']['ce']['path'])
grep -r "l10n_id_tax_number" <Odoo15_CE_PATH>/addons/l10n_id_efaktur/
# Hasil: ADA di l10n_id_efaktur/models/account_move.py

# Kesimpulan: Module l10n_id_efaktur belum di-migrate ke Odoo 19
```

## Checklist Investigation

Sebelum membuat rekomendasi, pastikan:

- [ ] Sudah cek file XML/view di custom module yang terkait error
- [ ] Sudah cek Odoo CE source untuk syntax yang benar
- [ ] Sudah cek Odoo EE source jika ada modul EE
- [ ] Sudah cek versi lama jika ini adalah migrasi dari Odoo lama
- [ ] Punya bukti kode yang salah/salah dari source
- [ ] Punya referensi kode yang benar dari source lain

## Reporting Format

Gunakan format ini untuk melaporkan hasil investigation:

```
## Hasil Investigasi

### Error: [error message]
### Lokasi: [file/line]
### Penyebab (Bukti):
[Copy-paste kode yang salah]
### Solusi (Bukti):
[Copy-paste kode yang benar dari source]
```

## Contoh Laporan Investigation

### Error: "View types not defined tree found in act_window action 226"

**Investigasi:**
```bash
# (gunakan paths['project']['custom_addons'])
$ grep -r "view_mode.*tree" <CUSTOM_MODULES_PATH>/asft_employee_payroll/
master_ump.xml:20:            <field name="view_mode">tree</field>
lapis_pph.xml:20:             <field name="view_mode">tree</field>
res_input_extra_category.xml:21: <field name="view_mode">tree</field>
```

**Cek Odoo 19 untuk syntax yang benar:**
```bash
# (gunakan paths['odoo']['ce']['path'])
$ grep -r "view_mode.*list" <CE_SOURCE_PATH>/addons/sale/ | head -3
sale_order_views.xml:1022: <field name="view_mode">list</field>
```

**Kesimpulan:**
- Penyebab: Custom modules menggunakan `view_mode="tree"` (sintax lama Odoo 15/16)
- Solusi: Ganti menjadi `view_mode="list"` untuk Odoo 19
- Files yang perlu diperbaiki:
  - `master_ump.xml` line 20
  - `lapis_pph.xml` line 20
  - `res_input_extra_category.xml` line 21
  - `contract.xml` line 18
