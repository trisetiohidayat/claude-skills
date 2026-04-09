#!/usr/bin/env python3
"""
MD to PDF Pro Converter
Convert Markdown files to professional PDF with proper tab/formatting handling.

Features:
- Tabs and whitespace preservation in code blocks
- Tables that don't break across pages
- Proper column widths for tables
- Long URL wrapping
- Professional styling
"""

import os
import sys
import argparse
import markdown


# CSS Template dengan fokus pada tab/formatting preservation
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
        break-after: avoid;
    }

    h2 {
        font-size: 16pt;
        color: #2c3e50;
        margin-top: 25px;
        border-left: 4px solid #0066cc;
        padding-left: 10px;
        break-after: avoid;
    }

    h3 {
        font-size: 13pt;
        color: #34495e;
        margin-top: 18px;
        break-after: avoid;
    }

    h4 {
        font-size: 11pt;
        color: #555;
        margin-top: 15px;
        break-after: avoid;
    }

    h5, h6 {
        font-size: 10pt;
        color: #666;
        margin-top: 12px;
        break-after: avoid;
    }

    /* === TABS & WHITESPACE PRESERVATION - KUNCI UTAMA === */
    /* Inline code styling */
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

    /* Fenced code blocks - KUNCI untuk tabs */
    pre {
        background-color: #f8f8f8;
        padding: 12px 15px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        margin: 15px 0;
        /* KUNCI: Preserve tabs dan whitespace, wrap jika perlu */
        white-space: pre-wrap;
        /* Prevent horizontal overflow */
        overflow-x: auto;
        max-width: 100%;
        box-sizing: border-box;
        /* Min height untuk code blocks */
        min-height: 30px;
    }

    pre code {
        padding: 0;
        background: none;
        font-size: 9pt;
        /* Ensure tabs don't cause overflow */
        white-space: pre-wrap;
        word-break: normal;
        overflow-wrap: normal;
        /* Preserve tab characters */
        tab-size: 4;
    }

    /* === TABLES - ANTI-BREAK & PROPER FORMATTING === */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        /* Fixed layout untuk column widths yang konsisten */
        table-layout: fixed;
        /* KUNCI: Don't break table across pages */
        break-inside: avoid;
        page-break-inside: avoid;
        /* Max width protection */
        max-width: 100%;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px 10px;
        text-align: left;
        vertical-align: top;
        /* KUNCI: Wrap long text */
        word-wrap: break-word;
        overflow-wrap: break-word;
        /* Prevent horizontal overflow */
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    th {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        width: auto;
    }

    /* Zebra striping */
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    /* KUNCI: Don't break rows across pages */
    tr {
        break-inside: avoid;
        page-break-inside: avoid;
    }

    /* Table header row - absolutely don't break */
    thead tr {
        break-after: avoid;
        page-break-after: avoid;
    }

    /* === LISTS === */
    ul, ol {
        margin-left: 25px;
        padding-left: 5px;
    }

    li {
        margin-bottom: 6px;
        /* KUNCI: Nested items preserve formatting */
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

    /* === LINKS & URLS - KUNCI === */
    a {
        color: #0066cc;
        /* KUNCI: URLs panjang harus wrap */
        word-break: break-all;
        overflow-wrap: break-word;
        word-wrap: break-word;
        hyphens: auto;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    /* === HORIZONTAL OVERFLOW PROTECTION === */
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

    /* === PARAGRAPHS === */
    p {
        margin-bottom: 12px;
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

    /* === STRONG & EMPHASIS === */
    strong, b {
        font-weight: bold;
    }

    em, i {
        font-style: italic;
    }

    /* === CODEHILITE STYLING === */
    .highlight {
        background-color: #f8f8f8;
        border-radius: 5px;
    }

    /* === DEFINITION LISTS === */
    dl {
        margin-left: 20px;
    }

    dt {
        font-weight: bold;
        margin-top: 10px;
    }

    dd {
        margin-left: 20px;
    }
</style>
"""


def md_to_html(md_content):
    """Convert Markdown to HTML dengan full extensions support."""
    extensions = [
        'tables',           # Tables
        'fenced_code',      # Code blocks
        'codehilite',       # Syntax highlighting
        'nl2br',            # Newlines to <br>
        'toc',              # Table of contents
        'sane_lists',       # Better list handling
        'smarty',           # Smart quotes
        'nl2br',            # Extra newline handling
    ]
    md = markdown.Markdown(extensions=extensions)
    return md.convert(md_content)


def convert_md_to_pdf(md_files, output_pdf, title="Document"):
    """Convert satu atau beberapa file MD ke PDF dengan formatting optimal."""

    if not md_files:
        print("Error: No input files specified")
        return False

    combined_content = []

    for i, md_file in enumerate(md_files):
        if not os.path.exists(md_file):
            print(f"Warning: File not found: {md_file}")
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        html_body = md_to_html(md_content)

        # Add page break between files (except first)
        if i > 0:
            combined_content.append('<div style="page-break-after: always;"></div>')

        # Add file title as section header (optional)
        # filename = os.path.basename(md_file)
        # section_title = os.path.splitext(filename)[0].replace('-', ' ').title()
        # combined_content.append(f'<h1>{section_title}</h1>')
        combined_content.append(html_body)

    # Wrap with full HTML template
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    {CSS_TEMPLATE}
</head>
<body>
{chr(10).join(combined_content)}
</body>
</html>"""

    try:
        # Generate PDF
        from weasyprint import HTML
        html_doc = HTML(string=full_html)
        html_doc.write_pdf(output_pdf)
        print(f"PDF generated successfully: {output_pdf}")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert MD to PDF with proper formatting (tabs, tables, etc.)'
    )
    parser.add_argument('input', nargs='+', help='Input MD file(s)')
    parser.add_argument('-o', '--output', default='output.pdf', help='Output PDF file')
    parser.add_argument('-t', '--title', default='Document', help='PDF title')

    args = parser.parse_args()

    success = convert_md_to_pdf(args.input, args.output, args.title)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
