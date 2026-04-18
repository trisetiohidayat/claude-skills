---
name: odoo-manual-writer
description: BUATKAN user manual/dokumentasi lengkap ke file DOCX dengan screenshot otomatis dari Odoo. Trigger ketika user meminta membuat dokumen panduan pengguna, SOP, manual aplikasi, dokumentasi langkah-langkah dengan screenshot. Kolaborasi dengan playwright-cli-odoo untuk navigasi dan capture screenshot Odoo, lalu tulis hasil ke file DOCX dengan formatting yang rapi. Trigger especially ketika user menyebutkan kata: manual, dokumentasi, SOP, panduan, langkah-langkah, user guide, dokumentasi lengkap, screenshot, dengan screenshot.
allowed-tools: Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*) Bash(python3:*) Bash(mkdir:*) Bash(cp:*)
---

# User Manual Writer untuk Odoo dengan Screenshot

## Philosophy: Screenshot Sekaligus, Dokumentasi Sekaligus

Workflow ini mengintegrasikan:
1. **playwright-cli-odoo** — navigasi Odoo, capture screenshot per langkah
2. **DOCX generation** — tulis semua langkah + screenshot ke file Word

**Prinsip:** setiap langkah自动化 = 1 screenshot + 1 paragraf penjelasan. Tidak perlu capture manual.

---

## Konfigurasi Awal

### Direktori Kerja

```bash
# Buat direktori untuk project dokumentasi
mkdir -p ./manual-output/screenshots
# Simpan semua screenshot di folder ini
```

### Setup DOCX (Python)

Pastikan `python-docx` tersedia:

```bash
pip install python-docx Pillow 2>/dev/null || pip3 install python-docx Pillow
```

---

## Workflow: Buat User Manual Lengkap

### Step 1: Tentukan Struktur Manual

Sebelum mulai, buat outline manual:

```
# Judul: [Judul Manual]
# Module: [Nama Modul Odoo]
# Scope: [Apa yang dicakup]
#
# Langkah 1: [Judul Langkah]
# → Command navigasi + screenshot
#
# Langkah 2: [Judul Langkah]
# → Command navigasi + screenshot
# ...
```

### Step 2: Capture Screenshot per Langkah

Untuk setiap langkah, navigasi dulu, lalu capture:

```bash
# Navigasi ke halaman target
playwright-cli goto 'http://localhost:8119/odoo/employees'

# Screenshot dengan nama deskriptif
playwright-cli screenshot --filename="./manual-output/screenshots/step-01-employees-list.png"
```

**Pola naming screenshot:**
```
step-01-{nama-halaman}.png   # langkah 1
step-02-{nama-halaman}.png   # langkah 2
step-03-{nama-halaman}.png   # langkah 3
```

### Step 3: Generate DOCX

Setelah semua screenshot tertangkap, generate DOCX:

```bash
python3 << 'PYEOF'
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

# ===== TITLE PAGE =====
title = doc.add_heading('[Judul Manual]', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('Versi: 1.0')
doc.add_paragraph('Tanggal: 2026-04-17')
doc.add_paragraph('Modul: [Nama Modul]')
doc.add_paragraph('Odoo Version: 19')
doc.add_page_break()

# ===== TABLE OF CONTENTS =====
doc.add_heading('Daftar Isi', 1)
toc_items = [
    '1. Pendahuluan',
    '2. Prasyarat',
    '3. Langkah-Langkah',
    '4. Catatan Penting',
]
for item in toc_items:
    doc.add_paragraph(item, style='List Number')

doc.add_page_break()

# ===== SECTION 1: PENDAHULUAN =====
doc.add_heading('1. Pendahuluan', 1)
doc.add_paragraph(
    'Dokumen ini berisi panduan lengkap untuk [process/task] '
    'menggunakan modul [Nama Modul] di Odoo. Manual ini disusun '
    'untuk membantu pengguna memahami dan menjalankan proses '
    '[deskripsi proses] secara sistematis.'
)

# ===== SECTION 2: PRASYARAT =====
doc.add_heading('2. Prasyarat', 1)
prasy = [
    'User memiliki akses ke modul [Nama Modul]',
    'User login sebagai [role] di database Odoo',
    'Modul [Nama Modul] sudah terinstall dan aktif',
    'Data pendukung sudah dikonfigurasi (jika diperlukan)',
]
for item in prasy:
    doc.add_paragraph(item, style='List Bullet')

# ===== SECTION 3: LANGKAH-LANGKAH =====
doc.add_heading('3. Langkah-Langkah', 1)

steps = [
    {
        'no': '3.1',
        'title': '[Judul Langkah 1]',
        'desc': '[Paragraf penjelasan apa yang dilakukan di langkah ini, '
                'dan mengapa langkah ini diperlukan. 2-3 kalimat.]',
        'screenshot': './manual-output/screenshots/step-01-employees-list.png',
    },
    {
        'no': '3.2',
        'title': '[Judul Langkah 2]',
        'desc': '[Penjelasan langkah 2]',
        'screenshot': './manual-output/screenshots/step-02-employee-form.png',
    },
]

for step in steps:
    # Step heading
    doc.add_heading(f"{step['no']} {step['title']}", 2)

    # Penjelasan
    p = doc.add_paragraph(step['desc'])

    # Screenshot
    if os.path.exists(step['screenshot']):
        img = doc.add_picture(step['screenshot'], width=Inches(6.0))
        last_para = doc.paragraphs[-1]
        last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Caption
        caption = doc.add_paragraph(f"Gambar {step['no']}: {step['title']}")
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption.runs[0].italic = True
        caption.runs[0].font.size = Pt(9)
    else:
        doc.add_paragraph(f'[Screenshot: {step["screenshot"]}]')

    doc.add_paragraph()  # spacing

# ===== SECTION 4: CATATAN =====
doc.add_heading('4. Catatan Penting', 1)
catatan = [
    'Pastikan semua field yang bertanda (*) wajib diisi.',
    'Data yang sudah disimpan tidak dapat dihapus (depends pada konfigurasi).',
    'Hubungi admin jika mengalami kendala akses.',
]
for item in catatan:
    doc.add_paragraph(item, style='List Bullet')

# ===== SAVE =====
output_path = './manual-output/[Nama-Modul]-User-Manual.docx'
doc.save(output_path)
print(f'Saved: {output_path}')
PYEOF
```

---

## Template Steps Array (Isi Dinamis)

Bagian `steps` di script Python di atas adalah template. Untuk setiap manual:

```python
steps = [
    {
        'no': '3.1',
        'title': 'Buka Modul Employees',
        'desc': (
            'Langkah pertama adalah membuka modul Employees melalui menu utama. '
            'Navigasi ke menu Employees dapat dilakukan melalui hamburger menu '
            'di pojok kiri atas, lalu pilih menu Employees.'
        ),
        'screenshot': './manual-output/screenshots/step-01-employees-list.png',
    },
    {
        'no': '3.2',
        'title': 'Klik Tombol New untuk Membuat Data Baru',
        'desc': (
            'Setelah halaman list terbuka, klik tombol "New" di pojok kiri atas '
            'untuk membuka form pembuatan employee baru. '
            'Form akan terbuka di panel kanan.'
        ),
        'screenshot': './manual-output/screenshots/step-02-employee-form.png',
    },
    # Tambah langkah berikutnya...
]
```

---

## Command Sequence untuk Setiap Langkah

### Pola Universal (Gunakan di Setiap Langkah)

```
# 1. Navigasi ke halaman
playwright-cli goto 'http://localhost:8119/odoo/[path]'

# 2. Tunggu page load
playwright-cli eval "() => document.querySelector('.o_form_view, .o_list_view, .o_kanban_view') ? 'ready' : 'loading'"

# 3. Screenshot
playwright-cli screenshot --filename="./manual-output/screenshots/step-XX-deskripsi.png"

# 4. (Opsional) Isi data jika perlu
playwright-cli click '[name="..."]'
```

### Screenshots untuk Berbagai View

```bash
# Screenshot list view
playwright-cli screenshot --filename="./manual-output/screenshots/step-01-list.png"

# Screenshot form view
playwright-cli screenshot --filename="./manual-output/screenshots/step-02-form.png"

# Screenshot kanban view
playwright-cli screenshot --filename="./manual-output/screenshots/step-03-kanban.png"

# Screenshot dialog/modal
playwright-cli screenshot --filename="./manual-output/screenshots/step-04-dialog.png"

# Screenshot error state
playwright-cli screenshot --filename="./manual-output/screenshots/step-05-error.png"
```

---

## Referensi

Untuk detail playwright-cli-odoo commands (navigasi, selectors, dll):
- `playwright-cli-odoo` skill — navigasi Odoo, CSS selectors, form fill, dll.
- `docx` skill — untuk formatting DOCX advanced (header, footer, table of contents, dll).

---

## Tips & Best Practices

1. **1 Langkah = 1 Screenshot** — Jangan masukkan banyak langkah dalam 1 screenshot
2. **Nama file deskriptif** — Gunakan format `step-XX-nama-halaman.png`
3. **Caption wajib** — Selalu tambahkan caption di bawah setiap screenshot
4. **Penjelasan 2-3 kalimat** — Cukup jelas, tidak perlu terlalu panjang
5. **Urutan kronologis** — Steps harus mengikuti urutan sebenarnya di aplikasi
6. **Version Odoo** — Selalu catat versi Odoo di title page
7. **Screenshot resolution** — Gunakan `playwright-cli resize 1280 800` sebelum screenshot agar konsisten

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Screenshot blank/hitam | Browser belum fully loaded — tambah `sleep 2` sebelum screenshot |
| Elemen tidak ditemukan | Gunakan `playwright-cli snapshot` untuk cari ref terbaru |
| DOCX tidak bisa di-open | Pastikan path screenshot relative dan file exist |
| Gambar terlalu besar | Set `width=Inches(5.5)` atau lebih kecil di Python script |
| Teks Bahasa Indonesia tidak rapi | Gunakan font yang support Unicode (Arial fallback) |
