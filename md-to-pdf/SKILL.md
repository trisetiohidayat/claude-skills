---
name: md-to-pdf
description: |
  Mengubah file Markdown (MD) menjadi format PDF yang profesional. Gunakan skill ini ketika:
  - User ingin convert MD ke PDF
  - User ingin menggabungkan beberapa file MD menjadi satu PDF
  - User meminta "eksport dokumentasi ke PDF"
  - User ingin membuat laporan dalam format PDF dari file markdown
  - User menyebutkan "PDF" dan "markdown" atau "MD" bersamaan
  - User ingin print Dokumentasi project

  Skill ini wajib digunakan untuk semua request yang berkaitan dengan konversi MD ke PDF.
---

# MD to PDF Conversion Skill

## Overview

Skill ini digunakan untuk mengkonversi satu atau beberapa file Markdown (.md) menjadi format PDF yang profesional menggunakan library WeasyPrint.

## Prerequisites

Pastikan dependencies berikut sudah terinstall:

```bash
pip install markdown weasyprint jinja2
```

Untuk macOS, mungkin perlu install additional dependencies:
```bash
brew install pango libffi
```

---

## Step 1: Identifikasi Input

### A. Single File
Jika user memberikan satu file MD:
1. Baca isi file MD tersebut
2. Tentukan output PDF name (default: `<nama_file>.pdf`)

### B. Multiple Files
Jika user memberikan beberapa file MD:
1. Identifikasi semua file MD yang disebutkan
2.urutkan berdasarkan urutan yang diminta user atau alphabetical
3. Gabungkan semua konten menjadi satu PDF

### C. Semua MD di Directory
Jika user ingin convert semua MD di sebuah folder:
1. List semua file .md di folder tersebut
2. Urutkan berdasarkan nama file
3. Proses semua menjadi satu PDF

---

## Step 2: Generate HTML dari MD

Konversi Markdown ke HTML menggunakan Python:

```python
import markdown

def md_to_html(md_content, template='default'):
    """Convert Markdown to HTML with styling."""
    extensions = [
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'nl2br',
    ]
    md = markdown.Markdown(extensions=extensions)
    html_body = md.convert(md_content)

    return html_body
```

---

## Step 3: Apply Template

### Default Template (recommended)

Gunakan template berikut untuk hasil profesional:

```python
DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }
            @top-right {
                content: "{header}";
                font-size: 10px;
                color: #999;
            }
        }

        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}

        h1 {{
            font-size: 24pt;
            color: #1a1a1a;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        h2 {{
            font-size: 18pt;
            color: #2c3e50;
            margin-top: 30px;
            border-left: 4px solid #0066cc;
            padding-left: 10px;
        }}

        h3 {{
            font-size: 14pt;
            color: #34495e;
            margin-top: 20px;
        }}

        p {{
            margin-bottom: 12px;
            text-align: justify;
        }}

        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}

        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #ddd;
        }}

        pre code {{
            padding: 0;
            background: none;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}

        th {{
            background-color: #0066cc;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        blockquote {{
            border-left: 4px solid #0066cc;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f5f9ff;
            font-style: italic;
        }}

        ul, ol {{
            margin-left: 20px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        img {{
            max-width: 100%;
            height: auto;
        }}

        .page-break {{
            page-break-after: always;
        }}

        /* Footer styling */
        .footer {{
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 10px;
            color: #666;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""
```

---

## Step 4: Generate PDF dengan WeasyPrint

```python
from weasyprint import HTML

def generate_pdf(html_content, output_path):
    """Generate PDF from HTML content."""
    html_doc = HTML(string=html_content)
    html_doc.write_pdf(output_path)
    print(f"PDF generated: {output_path}")
```

---

## Step 5: Gabungkan Multiple MD Files

```python
def combine_md_files(file_paths, output_pdf_path):
    """Combine multiple MD files into single PDF."""

    combined_html = []

    for i, file_path in enumerate(file_paths):
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        html_body = md_to_html(md_content)

        # Add separator between files (except first)
        if i > 0:
            combined_html.append('<div class="page-break"></div>')

        # Add section title
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0].replace('-', ' ').title()
        combined_html.append(f'<h1>{title}</h1>')
        combined_html.append(html_body)

    # Wrap with template
    full_html = DEFAULT_TEMPLATE.format(
        title='Documentation',
        header=output_pdf_path,
        content='\n'.join(combined_html)
    )

    # Generate PDF
    generate_pdf(full_html, output_pdf_path)
```

---

## Complete Script

Berikut script lengkap yang bisa langsung digunakan:

```python
#!/usr/bin/env python3
"""
MD to PDF Converter
Convert Markdown files to professional PDF documents.
"""

import os
import sys
import argparse
import markdown
from weasyprint import HTML

# Default template
TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}

        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}

        h1 {{
            font-size: 24pt;
            color: #1a1a1a;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        h2 {{
            font-size: 18pt;
            color: #2c3e50;
            margin-top: 30px;
            border-left: 4px solid #0066cc;
            padding-left: 10px;
        }}

        h3 {{
            font-size: 14pt;
            color: #34495e;
            margin-top: 20px;
        }}

        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}

        th {{
            background-color: #0066cc;
            color: white;
        }}

        .page-break {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

def md_to_html(md_content):
    """Convert Markdown to HTML."""
    extensions = ['tables', 'fenced_code', 'codehilite', 'nl2br']
    md = markdown.Markdown(extensions=extensions)
    return md.convert(md_content)

def convert_md_to_pdf(md_files, output_pdf, title="Documentation"):
    """Convert one or more MD files to PDF."""

    combined_content = []

    for i, md_file in enumerate(md_files):
        if not os.path.exists(md_file):
            print(f"Warning: File not found: {md_file}")
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        html_body = md_to_html(md_content)

        # Add page break between files
        if i > 0:
            combined_content.append('<div class="page-break"></div>')

        # Add file title as section header
        filename = os.path.basename(md_file)
        section_title = os.path.splitext(filename)[0].replace('-', ' ').title()
        combined_content.append(f'<h1>{section_title}</h1>')
        combined_content.append(html_body)

    # Generate full HTML
    full_html = TEMPLATE.format(
        title=title,
        content='\n'.join(combined_content)
    )

    # Convert to PDF
    HTML(string=full_html).write_pdf(output_pdf)
    print(f"PDF generated: {output_pdf}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MD to PDF')
    parser.add_argument('input', nargs='+', help='Input MD file(s)')
    parser.add_argument('-o', '--output', default='output.pdf', help='Output PDF file')
    parser.add_argument('-t', '--title', default='Documentation', help='PDF title')

    args = parser.parse_args()
    convert_md_to_pdf(args.input, args.output, args.title)
```

---

## Cara Penggunaan

### Command Line

```bash
# Single file
python md_to_pdf.py document.md -o document.pdf

# Multiple files
python md_to_pdf.py intro.md main.md conclusion.md -o full_doc.pdf

# Dengan title
python md_to_pdf.py *.md -o documentation.pdf -t "My Documentation"
```

### Dalam Claude Code

Ketika user meminta convert MD ke PDF:

1. Identifikasi file MD yang ingin dikonversi
2. Jika single file → konversi langsung
3. Jika multiple files → gabungkan lalu konversi
4. Jika semua MD di folder → list dulu, minta konfirmasi

Contoh prompt ke user:
```
Saya akan mengkonversi file MD berikut ke PDF:
- 01_overview.md
- 02_detailed_fields.md
- 03_business_process.md

Output: documentation.pdf

Tekan Enter untuk melanjutkan atau jelaskan jika ada yang ingin diubah.
```

---

## Error Handling

### Error: "No module named 'weasyprint'"
```
pip install weasyprint
```

### Error: "PyGObject not found" (macOS)
```bash
brew install pygobject3 gtk+3
```

### Error: "Failed to load font"
Ini adalah warning, PDF tetap bisa di-generate. Abaikan saja.

---

## Output Format

PDF yang dihasilkan memiliki:
- ✅ Ukuran A4
- ✅ Margin 2cm
- ✅ Header dengan nomor halaman
- ✅ Table styling
- ✅ Code block styling
- ✅ Heading styles yang konsisten
- ✅ Page break antar file (jika multiple)
