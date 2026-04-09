#!/usr/bin/env python3
"""
MD to PDF Converter
Convert Markdown files to professional PDF documents using WeasyPrint.
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

        h4 {{
            font-size: 12pt;
            color: #555;
            margin-top: 15px;
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

        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

def md_to_html(md_content):
    """Convert Markdown to HTML."""
    extensions = ['tables', 'fenced_code', 'codehilite', 'nl2br', 'toc']
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
    print(f"PDF generated successfully: {output_pdf}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MD to PDF')
    parser.add_argument('input', nargs='+', help='Input MD file(s)')
    parser.add_argument('-o', '--output', default='output.pdf', help='Output PDF file')
    parser.add_argument('-t', '--title', default='Documentation', help='PDF title')

    args = parser.parse_args()
    convert_md_to_pdf(args.input, args.output, args.title)
