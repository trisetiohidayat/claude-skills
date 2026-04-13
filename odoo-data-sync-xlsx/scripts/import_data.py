#!/usr/bin/env python3
"""
Odoo Data Import from Excel
Import data from Excel/CSV file to Odoo PostgreSQL database.

Usage:
    python import_data.py --database <db_name> --model <model_name> --input <file.xlsx> [--match-field <field>] [--update-fields <field1,field2>] [--dry-run]

Examples:
    # Dry run first (preview only)
    python import_data.py --database roedl_upgraded_20260331 --model res_partner_bank --input ~/Downloads/export.xlsx --match-field acc_number --update-fields company_id --dry-run

    # Execute import
    python import_data.py --database roedl_upgraded_20260331 --model res_partner_bank --input ~/Downloads/export.xlsx --match-field acc_number --update-fields company_id
"""

import argparse
import csv
import os
import sys
import openpyxl
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description='Import data from Excel/CSV to Odoo')
    parser.add_argument('--db-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--db-port', default='5432', help='PostgreSQL port')
    parser.add_argument('--db-user', default='odoo', help='PostgreSQL user')
    parser.add_argument('--db-password', default='odoo', help='PostgreSQL password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--model', required=True, help='Model/Table name (e.g., res_partner_bank)')
    parser.add_argument('--input', required=True, help='Input file path (.xlsx or .csv)')
    parser.add_argument('--match-field', default='id', help='Field to match records (default: id)')
    parser.add_argument('--update-fields', required=True, help='Comma-separated fields to update')
    parser.add_argument('--match-fields', default='', help='Comma-separated fields for composite match (overrides --match-field)')
    parser.add_argument('--create-missing', action='store_true', help='Create records if not found')
    parser.add_argument('--dry-run', action='store_true', help='Preview only, no changes')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for updates')
    parser.add_argument('--sheet', default='Export Data', help='Sheet name for Excel (default: Export Data)')
    parser.add_argument('--skip-header', action='store_true', default=True, help='Skip first row as header')
    return parser.parse_args()


def get_table_name(model):
    """Convert Odoo model name to PostgreSQL table name."""
    return model.replace('.', '_')


def read_excel(file_path, sheet_name='Export Data'):
    """Read data from Excel file."""
    wb = openpyxl.load_workbook(file_path, data_only=True)

    # Try specified sheet, or first sheet
    if sheet_name and sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.active

    rows = list(ws.values)

    if not rows:
        raise ValueError(f"No data found in {file_path}")

    # First row as header
    headers = [str(h) if h is not None else f'col_{i}' for i, h in enumerate(rows[0])]

    # Convert rows to dicts
    data = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue  # Skip empty rows
        # Skip non-data rows (summary, totals, etc.)
        first_col = str(row[0]).strip() if row[0] is not None else ''
        if first_col.startswith('Total') or first_col.startswith('=') or 'record' in first_col.lower():
            continue
        record = {}
        for i, val in enumerate(row):
            if i < len(headers):
                record[headers[i]] = val
        data.append(record)

    return headers, data


def read_csv(file_path):
    """Read data from CSV file."""
    data = []
    headers = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            if all(v == '' for v in row.values()):
                continue
            data.append(row)

    return headers, data


def get_connection(args):
    """Get PostgreSQL connection."""
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary")
        import psycopg2

    return psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        user=args.db_user,
        password=args.db_password,
        database=args.database
    )


def get_table_columns(conn, table_name):
    """Get list of columns in table."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return columns


def build_lookup_query(conn, table_name, match_fields):
    """Build query to lookup records by match fields."""
    if isinstance(match_fields, str):
        match_fields = [match_fields]

    # Get columns
    columns = get_table_columns(conn, table_name)
    id_col = 'id'

    # Build SELECT
    select_fields = [id_col] + match_fields
    select_clause = ', '.join(select_fields)

    query = f"SELECT {select_clause} FROM {table_name} WHERE "
    conditions = ' AND '.join([f"{f} = %s" for f in match_fields])
    query += conditions

    return query


def preview_changes(conn, table_name, data, match_field, update_fields, match_fields_list, create_missing=False):
    """Preview what changes will be made."""
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("DRY RUN - Preview Perubahan Data")
    print("=" * 70)

    # Get table columns
    available_cols = get_table_columns(conn, table_name)

    print(f"Table: {table_name}")
    print(f"Match field(s): {', '.join(match_fields_list)}")
    print(f"Update fields: {', '.join(update_fields)}")
    print(f"Total records in file: {len(data)}")
    print("-" * 70)

    matched = 0
    unmatched = 0
    no_change = 0
    will_update = 0
    will_skip = 0

    # Get current values
    current_values = {}

    # Build lookup for each record
    for record in data:
        match_val = record.get(match_field, '')
        if not match_val:
            match_val = record.get('id', '')

        if not match_val:
            unmatched += 1
            continue

        # Lookup current value
        cursor.execute(f"SELECT id, {match_field}, {', '.join(update_fields)} FROM {table_name} WHERE {match_field} = %s", (str(match_val),))
        row = cursor.fetchone()

        if row:
            matched += 1
            current_id = row[0]
            current_match = row[1]
            current_update_vals = row[2:]
            current_values[current_id] = {
                'match': current_match,
                'updates': {f: row[i+2] for i, f in enumerate(update_fields)}
            }

            # Check if values are different
            has_change = False
            for i, field in enumerate(update_fields):
                new_val = record.get(field, '')
                new_val = None if (new_val == '' or new_val is None) else new_val

                if str(current_update_vals[i] or '') != str(new_val or ''):
                    has_change = True
                    break

            if has_change:
                will_update += 1
                print(f"\n  [UPDATE] id={current_id}:")
                print(f"    Match on: {match_field}={current_match}")
                for i, field in enumerate(update_fields):
                    old_val = current_update_vals[i] if current_update_vals[i] is not None else '(NULL)'
                    new_val = record.get(field, '')
                    new_val = '(NULL)' if (new_val == '' or new_val is None) else new_val
                    if str(old_val) != str(new_val):
                        print(f"    {field}: {old_val} → {new_val}")
            else:
                will_skip += 1
                no_change += 1
        else:
            unmatched += 1
            print(f"\n  [NO MATCH] acc_number={match_val} (acc_holder: {record.get('acc_holder_name', 'N/A')})")
            if create_missing:
                print(f"    -> Will CREATE new record")

    cursor.close()

    print("\n" + "-" * 70)
    print("SUMMARY:")
    print(f"  Total records in file: {len(data)}")
    print(f"  Matched in database: {matched}")
    print(f"  NOT matched: {unmatched}")
    print(f"  Values same (skip): {no_change}")
    print(f"  Will UPDATE: {will_update}")
    if create_missing:
        print(f"  Will CREATE: {unmatched} (create-missing enabled)")
    print("=" * 70)

    return matched, unmatched, will_update


def execute_import(conn, table_name, data, match_field, update_fields, match_fields_list, batch_size=100):
    """Execute the actual import."""
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("EXECUTING IMPORT")
    print("=" * 70)

    updated = 0
    skipped = 0
    errors = 0

    for record in data:
        match_val = record.get(match_field, '')
        if not match_val:
            match_val = record.get('id', '')

        if not match_val:
            skipped += 1
            continue

        try:
            # Build UPDATE
            set_clause = ', '.join([f"{f} = %s" for f in update_fields])
            update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {match_field} = %s"

            # Prepare values
            values = []
            for field in update_fields:
                val = record.get(field, '')
                if val == '' or val is None:
                    values.append(None)
                else:
                    try:
                        values.append(int(val))
                    except ValueError:
                        values.append(val)

            values.append(str(match_val))

            cursor.execute(update_sql, values)

            if cursor.rowcount > 0:
                updated += 1
                print(f"  [OK] Updated {match_field}={match_val}")
            else:
                skipped += 1
                print(f"  [SKIP] No match for {match_field}={match_val}")

        except Exception as e:
            errors += 1
            print(f"  [ERROR] {match_field}={match_val}: {e}")

    conn.commit()
    cursor.close()

    print("\n" + "-" * 70)
    print("RESULT:")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print("=" * 70)


def main():
    args = parse_args()

    print(f"Connecting to: {args.database} ({args.db_host}:{args.db_port})")
    print(f"Model: {args.model}")
    print(f"Table: {get_table_name(args.model)}")
    print(f"Input file: {args.input}")
    print(f"Match field: {args.match_field}")
    print(f"Update fields: {args.update_fields}")
    print("-" * 50)

    # Read input file
    input_path = os.path.expanduser(args.input)
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    if input_path.endswith('.xlsx') or input_path.endswith('.xls'):
        headers, data = read_excel(input_path, args.sheet)
    else:
        headers, data = read_csv(input_path)

    print(f"Read {len(data)} records from file")
    print(f"Fields: {', '.join(headers[:10])}{'...' if len(headers) > 10 else ''}")

    # Parse update fields
    update_fields = [f.strip() for f in args.update_fields.split(',')]
    match_fields_list = [f.strip() for f in args.match_fields.split(',')] if args.match_fields else [args.match_field]

    # Connect to database
    conn = get_connection(args)
    table_name = get_table_name(args.model)

    # Verify table exists
    available_cols = get_table_columns(conn, table_name)
    print(f"Table columns: {', '.join(available_cols[:10])}{'...' if len(available_cols) > 10 else ''}")

    # Verify fields exist
    missing_fields = []
    for f in update_fields + match_fields_list:
        if f not in available_cols:
            missing_fields.append(f)

    if missing_fields:
        print(f"\nWARNING: Fields not found in table: {', '.join(missing_fields)}")
        print(f"Available columns: {', '.join(available_cols)}")

    # Preview
    matched, unmatched, will_update = preview_changes(
        conn, table_name, data,
        args.match_field, update_fields, match_fields_list,
        create_missing=args.create_missing
    )

    if args.dry_run:
        print("\n[DRY RUN COMPLETE] No changes made. Remove --dry-run to execute.")
        conn.close()
        return

    # Confirm before proceeding
    if will_update > 0:
        print(f"\nAbout to update {will_update} records.")
        response = input("Proceed with import? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Import cancelled.")
            conn.close()
            return

    # Execute import
    execute_import(conn, table_name, data, args.match_field, update_fields, match_fields_list, args.batch_size)

    conn.close()
    print("\n[COMPLETE]")


if __name__ == '__main__':
    main()
