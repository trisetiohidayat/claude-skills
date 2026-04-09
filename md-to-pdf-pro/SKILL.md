---
name: md-to-pdf-pro
description: |
  Mengubah file Markdown (MD) menjadi format PDF yang profesional dengan formatting yang rapi dan tab/indentasi yang tidak berantakan. Gunakan skill ini ketika:
  - User ingin convert MD ke PDF dengan format rapi
  - User mengeluh "tab berantakan", "tabel pecah", "format PDF berantakan"
  - User meminta PDF dari file MD yang memiliki tabel kompleks
  - User meminta PDF dari file MD yang memiliki code blocks dengan indentasi
  - User ingin "eksport dokumentasi ke PDF" yang harus rapi
  - User menyebutkan "PDF" dan "markdown" atau "MD" bersamaan dan butuh hasil profesional

  Skill ini menangani: tabs dalam code blocks, tabel yang tidak pecah antar halaman, URL panjang yang wrap,
  column widths yang proporsional, dan semua elemen MD lainnya.
---

# MD to PDF Pro Skill

## Overview

Skill ini mengkonversi file Markdown (.md) menjadi PDF profesional dengan penanganan khusus untuk:
- **Tabs dalam code blocks** - whitespace preservation dengan `pre-wrap`
- **Tabel kompleks** - tidak pecah antar halaman, column widths optimal
- **URL panjang** - auto-wrap untuk mencegah horizontal overflow
- **Indentation/tab** - preservasi yang tepat di semua konteks
- **Long code blocks** - horizontal scroll tanpa memecah layout

## Prerequisites

Pastikan dependencies sudah terinstall:

```bash
pip install markdown weasyprint
```

Untuk macOS:
```bash
brew install pango libffi
```

---

## Konversi Step-by-Step

### Step 1: Baca File MD

Baca file MD yang ingin dikonversi. Identifikasi jenis konten:
- Tabel (semua ukuran)
- Code blocks (fenced code dengan ```)
- Inline code (`code`)
- Lists (ordered/unordered/nested)
- URLs panjang
- Headings

### Step 2: Generate HTML dengan Template Pro

Gunakan Python script yang sudah disediakan di `scripts/md_to_pdf_pro.py` atau generate HTML dengan template di bawah ini.

**Template CSS Penting - Ini Kunci untuk Tabs dan Formatting:**

```python
CSS_TEMPLATE = """
<style>
    @page {
        size: A4;
        margin: 2cm;
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10px;
            color: #666;
        }
    }

    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }

    /* === HEADINGS === */
    h1 {
        font-size: 22pt;
        color: #1a1a1a;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 8px;
        margin-bottom: 20px;
        margin-top: 0;
    }

    h2 {
        font-size: 16pt;
        color: #2c3e50;
        margin-top: 25px;
        border-left: 4px solid #0066cc;
        padding-left: 10px;
    }

    h3 {
        font-size: 13pt;
        color: #34495e;
        margin-top: 18px;
    }

    h4 {
        font-size: 11pt;
        color: #555;
        margin-top: 15px;
    }

    /* === TABS & WHITESPACE PRESERVATION === */
    /* Ini penting! Tabs dalam code blocks harus dirender dengan benar */

    code {
        background-color: #f4f4f4;
        padding: 2px 5px;
        border-radius: 3px;
        font-family: 'Courier New', Consolas, monospace;
        font-size: 9pt;
        /* Prevent overflow for inline code */
        word-break: break-word;
        overflow-wrap: break-word;
    }

    pre {
        background-color: #f8f8f8;
        padding: 12px 15px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        margin: 15px 0;
        /* KUNCI: Preserve tabs dan whitespace */
        white-space: pre-wrap;
        /* Prevent horizontal overflow */
        overflow-x: auto;
        max-width: 100%;
        box-sizing: border-box;
    }

    pre code {
        padding: 0;
        background: none;
        font-size: 9pt;
        /* Ensure tabs don't cause overflow */
        white-space: pre-wrap;
        word-break: normal;
        overflow-wrap: normal;
    }

    /* === TABLES - ANTI-BREAK & PROPER FORMATTING === */
    /* KUNCI: Tabel tidak boleh pecah antar halaman */

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        /* Fixed layout untuk column widths yang konsisten */
        table-layout: fixed;
        /* KUNCI: Jangan pecah tabel antar halaman */
        break-inside: avoid;
        page-break-inside: avoid;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px 10px;
        text-align: left;
        vertical-align: top;
        /* KUNCI: Wrap text panjang */
        word-wrap: break-word;
        overflow-wrap: break-word;
        /* Prevent horizontal overflow dalam sel */
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    th {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        /* Column width untuk header - auto-sized */
        width: auto;
    }

    /* Zebra striping */
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    tr {
        /* KUNCI: Setiap baris tidak boleh pecah */
        break-inside: avoid;
        page-break-inside: avoid;
    }

    /* === LISTS === */
    ul, ol {
        margin-left: 25px;
        padding-left: 5px;
    }

    li {
        margin-bottom: 6px;
        /* KUNCI: Nested items dengan tab preserved */
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    li > ul, li > ol {
        margin-top: 4px;
        margin-bottom: 4px;
    }

    /* === BLOCKQUOTES === */
    blockquote {
        border-left: 4px solid #0066cc;
        margin: 15px 0;
        padding: 10px 15px;
        background-color: #f5f9ff;
        font-style: italic;
    }

    blockquote p {
        margin-bottom: 8px;
    }

    blockquote p:last-child {
        margin-bottom: 0;
    }

    /* === LINKS & URLS === */
    /* KUNCI: URLs panjang harus wrap */
    a {
        color: #0066cc;
        word-break: break-all;
        overflow-wrap: break-word;
        word-wrap: break-word;
        hyphens: auto;
    }

    /* === HORIZONTAL OVERFLOW PROTECTION === */
    /* Global: apapun elemen, jangan overflow */
    * {
        max-width: 100%;
        box-sizing: border-box;
    }

    /* === IMAGES === */
    img {
        max-width: 100%;
        height: auto;
        page-break-inside: avoid;
    }

    /* === PAGE BREAK CONTROL === */
    /* Jangan pecah elemen penting */
    h1, h2, h3, h4, h5, h6 {
        break-after: avoid;
        page-break-after: avoid;
    }

    /* === CHECKBOXES (Task lists) === */
    input[type="checkbox"] {
        margin-right: 8px;
    }

    /* === HR === */
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 25px 0;
    }

    /* === FOOTER === */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 9px;
        color: #999;
    }
</style>
"""
```

### Step 3: Convert MD to HTML

```python
import markdown

def md_to_html(md_content):
    """Convert Markdown to HTML dengan extensions untuk formatting lengkap."""
    extensions = [
        'tables',           # Tabel markdown
        'fenced_code',      # Code blocks dengan ```
        'codehilite',       # Syntax highlighting
        'nl2br',            # Newlines jadi <br>
        'toc',              # Table of contents
        'sane_lists',       # Better list handling
        'smarty',           # Smart quotes, etc.
    ]
    md = markdown.Markdown(extensions=extensions)
    return md.convert(md_content)
```

### Step 4: Generate PDF dengan WeasyPrint

```python
from weasyprint import HTML, CSS

def generate_pdf(html_content, output_path, title="Document"):
    """Generate PDF dari HTML content."""

    # Wrap dengan HTML template
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    {CSS_TEMPLATE}
</head>
<body>
    {html_content}
</body>
</html>"""

    # Generate PDF
    html_doc = HTML(string=full_html)
    html_doc.write_pdf(output_path)
    print(f"PDF generated: {output_path}")
```

---

## Complete Script

Script lengkap tersedia di `scripts/md_to_pdf_pro.py`.

### Cara Pakai:

```bash
# Single file
python md_to_pdf_pro.py document.md -o document.pdf

# Multiple files
python md_to_pdf_pro.py file1.md file2.md -o combined.pdf

# Dengan title
python md_to_pdf_pro.py *.md -o docs.pdf -t "Documentation Title"
```

---

## Tips Formatting

### Untuk Tabel yang Rapi:

1. **Gunakan pipe `|` untuk kolom**
2. **Gunakan `---` untuk header separator**
3. **Untuk kolom yang sempit**, taruh spasi dalam header
4. **Untuk data panjang**, akan auto-wrap dengan CSS

### Untuk Code Blocks:

1. **Indentasi 4 spasi** atau gunakan ``` untuk fenced blocks
2. **Tabs akan dipreserve** dengan `white-space: pre-wrap`
3. **Code panjang** akan scroll horizontal, tidak memecah layout

### Untuk URLs:

1. **URL panjang** akan auto-wrap dengan `word-break: break-all`
2. **Links dalam teks** akan tetap rapi

---

## Troubleshooting

### Error: "No module named 'weasyprint'"
```bash
pip install weasyprint
```

### Error: "PyGObject not found" (macOS)
```bash
brew install pygobject3 gtk+3
```

### Tabel masih pecah?
Tambahkan inline style pada tabel:
```html
<table style="break-inside: avoid; page-break-inside: avoid;">
```

### Code masih overflow?
Pastikan menggunakan `white-space: pre-wrap` di CSS untuk `<pre>`.

### Column terlalu sempit?
Gunakan `min-width` di CSS atau tambah spasi dalam markdown header.

---

## Output Format

PDF yang dihasilkan:
- ✅ Ukuran A4
- ✅ Margin 2cm
- ✅ Page numbers
- ✅ Tabel tidak pecah antar halaman
- ✅ Code blocks dengan tabs preserved
- ✅ URLs wrap dengan benar
- ✅ Column widths optimal
- ✅ Zebra striping untuk tabel
- ✅ Syntax highlighting untuk code
