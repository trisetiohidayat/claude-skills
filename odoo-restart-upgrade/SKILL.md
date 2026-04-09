# Odoo Restart & Upgrade Advisor

## Deskripsi

Memberikan rekomendasi berupa penalaran tentang kapan perlu restart server atau upgrade module berdasarkan file yang diubah.

## Trigger

- **Auto-trigger**: Setiap kali ada perubahan file di Odoo project
- **Manual**: `/odoo-restart-upgrade`

## Output Format

Format kombinasi - Brief explanation + checklist:

```
📋 ANALISIS PERUBAHAN

File: module_name/models/models.py
⚡ Aksi: Restart + Upgrade
💡 Karena: Perubahan Python model memerlukan server restart dan module upgrade untuk apply

━━━━━━━━━━━━━━━━━━━━━━
✅ CHECKLIST AKSI:

☐ python odoo-bin -c odoo19.conf -d roedl -u module_name --stop-after-init
☐ (Jika perlu restart) - Stop & Start Odoo server
```

## Kondisi yang Ditangani

### 1. Python Files

| File Pattern | Aksi | Alasan |
|--------------|------|--------|
| `__manifest__.py` | Restart + Upgrade | Version, dependencies, atau metadata module berubah |
| `models/*.py`, `models.py` | Restart + Upgrade | Python model logic berubah |
| `wizard/*.py`, `wizard.py` | Restart + Upgrade | Wizard logic berubah |
| `controllers/*.py` | Restart | HTTP endpoint/routing berubah |
| `report/*.py` | Restart + Upgrade | Report logic berubah |

### 2. XML Files

| File Pattern | Aksi | Alasan |
|--------------|------|--------|
| `views/*.xml`, `views.xml` | Upgrade | XML view changes (auto-reload jika dev=xml) |
| `reports/*.xml` | Upgrade | Report template berubah |
| `wizard/*.xml` | Upgrade | Wizard view berubah |
| `data/*.xml`, `data/*.csv` | Upgrade | Demo/data initialization berubah |
| `data/demo/*.xml` | Upgrade | Demo data berubah |

### 3. Security Files

| File Pattern | Aksi | Alasan |
|--------------|------|--------|
| `security/ir.model.access.csv` | Upgrade | Access Control List (ACL) berubah |
| `security/*.csv` | Upgrade | Security rules berubah |

### 4. Static Assets

| File Pattern | Aksi | Alasan |
|--------------|------|--------|
| `static/src/js/*.js` | Clear cache + Upgrade | JavaScript asset berubah |
| `static/src/css/*.css` | Clear cache + Upgrade | CSS asset berubah |
| `static/*.{js,css}` | Clear cache + Upgrade | Asset berubah |

### 5. Konfigurasi

| Pattern | Aksi | Alasan |
|---------|------|--------|
| `odoo.conf` | Restart | Konfigurasi server berubah |
| Konfigurasi internal module | Restart | System parameters berubah |

## Kondisi Khusus

### dev=xml Mode

Jika Odoo berjalan dengan flag `--dev=xml`:
- File XML `views/*.xml` tidak perlu manual upgrade
- Cukup save file dan Odoo auto-reload
- Tetap perlu restart untuk case lain

### CE vs EE

Jika feature membutuhkan Enterprise Edition:
- Tambahkan catatan: `⚠️ Memerlukan Odoo Enterprise Edition`
- Beberapa module (seperti `hr_payroll`) hanya tersedia di EE

### Multiple Modules

Jika mehrere modules berubah:
- Analyze setiap file per module
- Generate checklist per module
- Prioritaskan berdasarkan dependencies

## Checklist Template

```
━━━━━━━━━━━━━━━━━━━━━━
✅ CHECKLIST AKSI:

[ ] Upgrade module(s):
   python odoo-bin -c odoo19.conf -d roedl -u module_name --stop-after-init

[ ] Jika perlu restart server:
   - Stop Odoo server
   - Start Odoo server

[ ] Jika perlu clear cache:
   - Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
   - Atau disable asset bundling di Developer Tools
```

## Usage Example

**Input**: User mengubah file `hr_course/models/models.py`

**Output**:
```
📋 ANALISIS PERUBAHAN

File: hr_course/models/models.py
⚡ Aksi: Restart + Upgrade
💡 Karena: Perubahan Python model memerlukan server restart dan module upgrade untuk apply

━━━━━━━━━━━━━━━━━━━━━━
✅ CHECKLIST AKSI:

☐ python odoo-bin -c odoo19.conf -d roedl -u hr_course --stop-after-init
☐ Stop & Start Odoo server
```

**Input**: User mengubah file `hr_course/views/course_view.xml`

**Output**:
```
📋 ANALISIS PERUBAHAN

File: hr_course/views/course_view.xml
⚡ Aksi: Upgrade saja (dev=xml aktif)
💡 Karena: XML view changes auto-reload dengan dev=xml

File: hr_course/__manifest__.py (dependencies)
⚡ Aksi: Restart + Upgrade
💡 Karena: Perlu register ulang dependencies

━━━━━━━━━━━━━━━━━━━━━━
✅ CHECKLIST AKSI:

☐ python odoo-bin -c odoo19.conf -d roedl -u hr_course --stop-after-init
☐ Jika manifest berubah: Stop & Start Odoo server
```

## Implementation Notes

- Selalu check `__manifest__.py` terlebih dahulu
- Jika dependencies di manifest berubah → Restart WAJIB
- Untuk multiple files, prioritaskan: manifest > Python > XML
- Sertakan catatan khusus untuk EE-only features
