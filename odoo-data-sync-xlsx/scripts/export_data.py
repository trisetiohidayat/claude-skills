#!/usr/bin/env python3
"""
Odoo Data Export to Excel
Export data from Odoo PostgreSQL database to Excel file.

Usage:
    python export_data.py --database <db_name> --model <model_name> --output <file.xlsx> [--fields <field1,field2>]

Examples:
    python export_data.py --database roedl_15_20260331 --model res_partner_bank --output ~/Downloads/export.xlsx --fields id,acc_number,company_id
"""

import argparse
import csv
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def parse_args():
    parser = argparse.ArgumentParser(description='Export Odoo data to Excel')
    parser.add_argument('--db-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--db-port', default='5432', help='PostgreSQL port')
    parser.add_argument('--db-user', default='odoo', help='PostgreSQL user')
    parser.add_argument('--db-password', default='odoo', help='PostgreSQL password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--model', required=True, help='Model/Table name (e.g., res_partner_bank)')
    parser.add_argument('--output', required=True, help='Output file path (.xlsx or .csv)')
    parser.add_argument('--fields', default='*', help='Comma-separated fields to export (default: *)')
    parser.add_argument('--where', default='1=1', help='WHERE clause filter')
    parser.add_argument('--limit', type=int, default=0, help='Limit results (0 = no limit)')
    return parser.parse_args()


def get_connection_string(args):
    return f"postgresql://{args.db_user}:{args.db_password}@{args.db_host}:{args.db_port}/{args.database}"


def get_table_name(model):
    """Convert Odoo model name to PostgreSQL table name."""
    # Odoo model: res.partner.bank -> Table: res_partner_bank
    return model.replace('.', '_')


def fetch_data(args):
    """Fetch data from PostgreSQL."""
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("ERROR: psycopg2 not installed. Installing...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary")
        import psycopg2

    conn = psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        user=args.db_user,
        password=args.db_password,
        database=args.database
    )

    table_name = get_table_name(args.model)

    # Get fields
    if args.fields == '*':
        fields_query = '*'
        fields_list = []
    else:
        fields_list = [f.strip() for f in args.fields.split(',')]
        fields_query = ', '.join(fields_list)

    # Build query
    query = f'SELECT {fields_query} FROM {table_name} WHERE {args.where}'
    if args.limit > 0:
        query += f' LIMIT {args.limit}'

    cursor = conn.cursor()
    cursor.execute(query)

    # Get column names
    if args.fields == '*':
        fields_list = [desc[0] for desc in cursor.description]
    else:
        fields_list = [f.strip() for f in args.fields.split(',')]

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return fields_list, rows


def write_excel(fields, rows, output_path):
    """Write data to Excel file with formatting."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Export Data"

    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Write header
    for col_idx, field in enumerate(fields, 1):
        cell = ws.cell(row=1, column=col_idx, value=field)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Write data
    for row_idx, row in enumerate(rows, 2):
        for col_idx, value in enumerate(row, 1):
            # Handle NULL values
            if value is None:
                display_value = ''
            else:
                display_value = str(value)

            cell = ws.cell(row=row_idx, column=col_idx, value=display_value)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

    # Auto-adjust column widths
    for col_idx, field in enumerate(fields, 1):
        max_length = len(str(field))
        for row in rows:
            if row[col_idx - 1] is not None:
                max_length = max(max_length, len(str(row[col_idx - 1])))
        adjusted_width = min(max_length + 2, 50)  # Max 50 chars
        ws.column_dimensions[get_column_letter(col_idx)].width = adjusted_width

    # Add summary row
    summary_row = len(rows) + 3
    ws.cell(row=summary_row, column=1, value=f"Total Records: {len(rows)}")
    ws.cell(row=summary_row, column=1).font = Font(bold=True)

    wb.save(output_path)
    return len(rows)


def write_csv(fields, rows, output_path):
    """Write data to CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            # Convert None to empty string
            row_data = ['' if val is None else str(val) for val in row]
            writer.writerow(row_data)
    return len(rows)


def main():
    args = parse_args()

    print(f"Connecting to: {args.database} ({args.db_host}:{args.db_port})")
    print(f"Model: {args.model}")
    print(f"Table: {get_table_name(args.model)}")
    print(f"Fields: {args.fields}")
    print("-" * 50)

    try:
        fields, rows = fetch_data(args)
        print(f"Fetched {len(rows)} records")
        print(f"Fields: {', '.join(fields)}")

        # Determine output format
        output_path = os.path.expanduser(args.output)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if output_path.endswith('.xlsx') or output_path.endswith('.xls'):
            count = write_excel(fields, rows, output_path)
            print(f"\nExcel file saved: {output_path}")
        else:
            count = write_csv(fields, rows, output_path)
            print(f"\nCSV file saved: {output_path}")

        print(f"Total records exported: {count}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
