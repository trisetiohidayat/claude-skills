#!/usr/bin/env python3
"""
Odoo Data Import from Excel
Import data from Excel/CSV file to Odoo PostgreSQL database.

Supports three ID modes:
  1. DB ID    : match by integer primary key (id column = 22)
  2. External ID: match by Odoo XML ID (id column = 'base.res_partner_22')
  3. Field match: match by any field value (--match-field acc_number)

For related many2one fields, values can be:
  - Integer DB ID  : partner_id = 22
  - External ID    : partner_id/id = 'base.res_partner_22'  (column name with /id suffix)

Usage:
    # Match by DB id, update partner_id
    python import_data.py --database roedl_upgraded_20260331 --model res_partner_bank \\
        --input fix.xlsx --match-field id --update-fields partner_id --dry-run

    # Match by external ID (id column contains 'module.name')
    python import_data.py --database roedl_upgraded_20260331 --model res_partner_bank \\
        --input fix.xlsx --use-external-id --update-fields partner_id --dry-run

    # Related fields as external IDs (column: partner_id/id)
    python import_data.py --database roedl_upgraded_20260331 --model res_partner_bank \\
        --input fix.xlsx --match-field id --update-fields partner_id/id --dry-run
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
    parser.add_argument('--model', required=True, help='Model/Table name (e.g., res_partner_bank or res.partner.bank)')
    parser.add_argument('--input', required=True, help='Input file path (.xlsx or .csv)')
    parser.add_argument('--match-field', default='id', help='Field to match records (default: id)')
    parser.add_argument('--update-fields', required=True,
                        help='Comma-separated fields to update. Use field/id for external ID references (e.g., partner_id/id)')
    parser.add_argument('--match-fields', default='',
                        help='Comma-separated fields for composite match (overrides --match-field)')
    parser.add_argument('--use-external-id', action='store_true',
                        help='Match records by external ID (id column contains module.name)')
    parser.add_argument('--create-missing', action='store_true',
                        help='Create records if not found by match field')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview only, no changes written to database')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for updates')
    parser.add_argument('--sheet', default='Export Data', help='Sheet name for Excel (default: Export Data)')
    return parser.parse_args()


def get_table_name(model):
    """Convert Odoo model name to PostgreSQL table name."""
    return model.replace('.', '_')


def get_model_name(table_or_model):
    """Normalize to Odoo model name (with dots)."""
    if '.' in table_or_model:
        return table_or_model
    # res_partner_bank -> res.partner.bank
    return table_or_model.replace('_', '.')


def read_excel(file_path, sheet_name='Export Data'):
    """Read data from Excel file."""
    wb = openpyxl.load_workbook(file_path, data_only=True)

    if sheet_name and sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.active

    rows = list(ws.values)
    if not rows:
        raise ValueError(f"No data found in {file_path}")

    headers = [str(h) if h is not None else f'col_{i}' for i, h in enumerate(rows[0])]

    data = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue
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
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames)
        for row in reader:
            if all(v == '' for v in row.values()):
                continue
            data.append(dict(row))
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
    columns = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    return columns


def resolve_external_id(conn, model_name, external_id):
    """Resolve external ID (module.name) to database record ID.

    Handles three formats:
    1. 'base.main_company'          → lookup via ir_model_data
    2. '__import__.res_partner_bank_22' → extract numeric suffix → DB id 22 (fallback)
    3. '__export__.res_partner_9_a25896cd' → extract numeric part → DB id 9 (fallback)
    4. '22' (plain integer string)  → return 22 directly as DB id
    """
    if not external_id or str(external_id).strip() == '':
        return None

    external_id = str(external_id).strip()

    # Plain integer → use directly as DB id
    try:
        return int(float(external_id))
    except (ValueError, TypeError):
        pass

    if '.' not in external_id:
        raise ValueError(
            f"External ID '{external_id}' must be in format 'module.name' (e.g., 'base.res_partner_1')."
        )

    module, name = external_id.split('.', 1)

    # Fast path: __import__ and __export__ auto-generated IDs
    # __import__ format: res_partner_bank_22  → id is the last segment (22)
    # __export__ format: res_partner_9_a25896cd → id is the first pure-numeric segment
    if module in ('__import__', '__export__'):
        import re
        parts = name.split('_')
        # Find the first segment that is purely numeric
        for part in parts:
            if part.isdigit():
                candidate = int(part)
                if candidate > 0:
                    return candidate
        return None

    # Normal case: lookup via ir_model_data
    cursor = conn.cursor()
    cursor.execute("""
        SELECT res_id FROM ir_model_data
        WHERE model = %s AND module = %s AND name = %s
        LIMIT 1
    """, (model_name, module, name))
    row = cursor.fetchone()
    cursor.close()
    return row[0] if row else None


def resolve_external_id_any_model(conn, external_id):
    """Resolve external ID without knowing the model - returns (res_id, model)."""
    if not external_id or '.' not in str(external_id):
        return None, None
    external_id = str(external_id).strip()
    module, name = external_id.split('.', 1)

    # Auto-generated IDs: extract first pure-numeric segment
    if module in ('__import__', '__export__'):
        parts = name.split('_')
        for part in parts:
            if part.isdigit():
                return int(part), None
        return None, None

    cursor = conn.cursor()
    cursor.execute("""
        SELECT res_id, model FROM ir_model_data
        WHERE module = %s AND name = %s
        LIMIT 1
    """, (module, name))
    row = cursor.fetchone()
    cursor.close()
    return (row[0], row[1]) if row else (None, None)


def get_related_model_for_field(conn, model_name, field_name):
    """Get the related model name for a many2one field."""
    # Strip /id suffix if present
    field_name = field_name.replace('/id', '').replace('/.id', '')

    cursor = conn.cursor()
    cursor.execute("""
        SELECT relation FROM ir_model_fields
        WHERE model = %s AND name = %s AND ttype = 'many2one'
        LIMIT 1
    """, (model_name, field_name))
    row = cursor.fetchone()
    cursor.close()

    if row:
        return row[0]

    # Fallback: common field → model mapping
    common_map = {
        'partner_id': 'res.partner',
        'company_id': 'res.company',
        'bank_id': 'res.bank',
        'currency_id': 'res.currency',
        'user_id': 'res.users',
        'product_id': 'product.product',
        'product_tmpl_id': 'product.template',
        'category_id': 'res.partner.category',
        'journal_id': 'account.journal',
        'account_id': 'account.account',
        'move_id': 'account.move',
        'picking_id': 'stock.picking',
        'warehouse_id': 'stock.warehouse',
        'location_id': 'stock.location',
        'employee_id': 'hr.employee',
        'department_id': 'hr.department',
    }
    return common_map.get(field_name)


def coerce_value(val, col_type):
    """Convert a value to the appropriate Python type for SQL."""
    if val is None or (isinstance(val, str) and val.strip() == ''):
        return None
    if col_type in ('integer', 'bigint', 'smallint'):
        try:
            return int(float(str(val)))
        except (ValueError, TypeError):
            return None
    if col_type in ('numeric', 'real', 'double precision'):
        try:
            return float(str(val))
        except (ValueError, TypeError):
            return None
    if col_type == 'boolean':
        return str(val).lower() in ('true', '1', 'yes', 't')
    return str(val)


class FieldSpec:
    """Represents a single field to update, with its source column name and resolution strategy."""

    def __init__(self, raw_name):
        self.raw = raw_name  # as given by user (e.g., 'partner_id' or 'partner_id/id')
        self.is_external_ref = raw_name.endswith('/id') or raw_name.endswith('/.id')
        self.db_field = raw_name.replace('/id', '').replace('/.id', '')  # actual DB column
        self.col_name = raw_name  # column name in the Excel file

    def __repr__(self):
        mode = 'external_id' if self.is_external_ref else 'db_value'
        return f"FieldSpec({self.db_field}, mode={mode})"


def resolve_field_value(conn, spec, raw_value, model_name, col_types):
    """Resolve a field value from Excel to its DB-ready form.

    For external ID fields (partner_id/id), looks up the related record's DB id.
    For regular fields, coerces to the right type.
    """
    if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == ''):
        return None

    if spec.is_external_ref:
        # Value is an external ID like 'base.res_partner_1'
        related_model = get_related_model_for_field(conn, model_name, spec.db_field)
        if related_model:
            db_id = resolve_external_id(conn, related_model, str(raw_value).strip())
        else:
            # Try without model constraint
            db_id, _ = resolve_external_id_any_model(conn, str(raw_value).strip())
        if db_id is None:
            raise ValueError(
                f"External ID '{raw_value}' not found for field '{spec.db_field}' "
                f"(model: {related_model or 'unknown'})"
            )
        return db_id
    else:
        col_type = col_types.get(spec.db_field, 'text')
        return coerce_value(raw_value, col_type)


def find_record_id(conn, table_name, model_name, record, match_fields, use_external_id, col_types):
    """Find the DB id of a record to update.

    Returns (db_id, match_value_used) or (None, None) if not found.
    """
    cursor = conn.cursor()

    if use_external_id:
        # 'id' column contains external ID like 'base.res_partner_bank_22'
        ext_id = record.get('id', '')
        if not ext_id:
            return None, None
        db_id = resolve_external_id(conn, model_name, str(ext_id).strip())
        return db_id, ext_id
    else:
        # Match by field value(s)
        conditions = []
        values = []
        for mf in match_fields:
            val = record.get(mf)
            if val is None or (isinstance(val, str) and val.strip() == ''):
                continue
            col_type = col_types.get(mf, 'text')
            coerced = coerce_value(val, col_type)
            conditions.append(f"{mf} = %s")
            values.append(coerced)

        if not conditions:
            return None, None

        query = f"SELECT id FROM {table_name} WHERE {' AND '.join(conditions)} LIMIT 1"
        cursor.execute(query, values)
        row = cursor.fetchone()
        cursor.close()
        match_val = ', '.join(str(record.get(mf, '')) for mf in match_fields)
        return (row[0] if row else None), match_val


def preview_changes(conn, table_name, model_name, data, match_fields, field_specs,
                    use_external_id, create_missing, col_types):
    """Preview what changes will be made (dry-run mode)."""
    print("\n" + "=" * 70)
    print("DRY RUN - Preview Perubahan Data")
    print("=" * 70)
    print(f"Table  : {table_name}")
    print(f"Model  : {model_name}")
    if use_external_id:
        print(f"Match  : External ID (id column)")
    else:
        print(f"Match  : {', '.join(match_fields)}")
    print(f"Update : {', '.join(s.raw for s in field_specs)}")
    print(f"Records: {len(data)} in file")
    print("-" * 70)

    matched = 0
    unmatched = 0
    will_update = 0
    will_skip = 0

    for record in data:
        db_id, match_val = find_record_id(
            conn, table_name, model_name, record,
            match_fields, use_external_id, col_types
        )

        if db_id is None:
            unmatched += 1
            print(f"\n  [NO MATCH] {match_val or '(empty key)'}")
            if create_missing:
                print(f"    → Will CREATE new record")
            continue

        # Get current values
        select_cols = ', '.join(s.db_field for s in field_specs)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {select_cols} FROM {table_name} WHERE id = %s", (db_id,))
        current_row = cursor.fetchone()
        cursor.close()

        if current_row is None:
            unmatched += 1
            print(f"\n  [NO MATCH] {match_val or '(empty key)'} — id={db_id} not found in table")
            continue

        matched += 1

        # Check which fields actually change
        changes = []
        for i, spec in enumerate(field_specs):
            current_val = current_row[i]
            try:
                new_val = resolve_field_value(conn, spec, record.get(spec.col_name), model_name, col_types)
            except ValueError as e:
                changes.append((spec.db_field, current_val, f'[ERROR: {e}]'))
                continue

            current_str = str(current_val) if current_val is not None else '(NULL)'
            new_str = str(new_val) if new_val is not None else '(NULL)'
            if current_str != new_str:
                changes.append((spec.db_field, current_val, new_val))

        if changes:
            will_update += 1
            print(f"\n  [UPDATE] id={db_id} (matched on: {match_val})")
            for field, old, new in changes:
                old_disp = old if old is not None else '(NULL)'
                new_disp = new if new is not None else '(NULL)'
                print(f"    {field}: {old_disp} → {new_disp}")
        else:
            will_skip += 1

    print("\n" + "-" * 70)
    print("SUMMARY:")
    print(f"  Total in file  : {len(data)}")
    print(f"  Matched in DB  : {matched}")
    print(f"  NOT matched    : {unmatched}")
    print(f"  No change      : {will_skip}")
    print(f"  Will UPDATE    : {will_update}")
    if create_missing:
        print(f"  Will CREATE    : {unmatched}")
    print("=" * 70)

    return matched, unmatched, will_update


def execute_import(conn, table_name, model_name, data, match_fields, field_specs,
                   use_external_id, create_missing, col_types, batch_size=100):
    """Execute the actual import."""
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("EXECUTING IMPORT")
    print("=" * 70)

    updated = 0
    created = 0
    skipped = 0
    errors = 0

    for record in data:
        db_id, match_val = find_record_id(
            conn, table_name, model_name, record,
            match_fields, use_external_id, col_types
        )

        if db_id is None:
            if create_missing:
                # Build INSERT
                try:
                    insert_cols = []
                    insert_vals = []
                    for spec in field_specs:
                        val = resolve_field_value(conn, spec, record.get(spec.col_name), model_name, col_types)
                        insert_cols.append(spec.db_field)
                        insert_vals.append(val)
                    col_clause = ', '.join(insert_cols)
                    val_clause = ', '.join(['%s'] * len(insert_cols))
                    cursor.execute(
                        f"INSERT INTO {table_name} ({col_clause}) VALUES ({val_clause}) RETURNING id",
                        insert_vals
                    )
                    new_id = cursor.fetchone()[0]
                    created += 1
                    print(f"  [CREATED] id={new_id} (key: {match_val})")
                except Exception as e:
                    errors += 1
                    print(f"  [ERROR] CREATE failed for {match_val}: {e}")
            else:
                skipped += 1
                print(f"  [SKIP] No match for: {match_val}")
            continue

        # Build UPDATE
        try:
            set_parts = []
            values = []
            for spec in field_specs:
                val = resolve_field_value(conn, spec, record.get(spec.col_name), model_name, col_types)
                set_parts.append(f"{spec.db_field} = %s")
                values.append(val)
            values.append(db_id)

            sql = f"UPDATE {table_name} SET {', '.join(set_parts)} WHERE id = %s"
            cursor.execute(sql, values)

            if cursor.rowcount > 0:
                updated += 1
                print(f"  [OK] Updated id={db_id} (key: {match_val})")
            else:
                skipped += 1
                print(f"  [SKIP] No rows updated for id={db_id}")

        except Exception as e:
            errors += 1
            print(f"  [ERROR] id={db_id} ({match_val}): {e}")

    conn.commit()
    cursor.close()

    print("\n" + "-" * 70)
    print("RESULT:")
    print(f"  Updated : {updated}")
    print(f"  Created : {created}")
    print(f"  Skipped : {skipped}")
    print(f"  Errors  : {errors}")
    print("=" * 70)

    return updated, created, errors


def main():
    args = parse_args()

    table_name = get_table_name(args.model)
    model_name = get_model_name(args.model)

    print(f"Database : {args.database} ({args.db_host}:{args.db_port})")
    print(f"Model    : {model_name}")
    print(f"Table    : {table_name}")
    print(f"Input    : {args.input}")
    if args.use_external_id:
        print(f"Match by : External ID (id column)")
    else:
        print(f"Match by : {args.match_field}")
    print(f"Update   : {args.update_fields}")
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
    print(f"Columns: {', '.join(headers[:12])}{'...' if len(headers) > 12 else ''}")

    # Parse field specs (supports 'partner_id' and 'partner_id/id')
    field_specs = [FieldSpec(f.strip()) for f in args.update_fields.split(',')]

    # Parse match fields
    if args.match_fields:
        match_fields = [f.strip() for f in args.match_fields.split(',')]
    else:
        match_fields = [args.match_field]

    # Connect to database
    conn = get_connection(args)

    # Get table columns with types
    col_types = get_table_columns(conn, table_name)
    if not col_types:
        print(f"ERROR: Table '{table_name}' not found in database.")
        print("Available tables: run 'PGPASSWORD=odoo psql -h localhost -U odoo -d DB -c \"\\dt\"'")
        conn.close()
        sys.exit(1)

    print(f"Table columns: {', '.join(list(col_types.keys())[:10])}{'...' if len(col_types) > 10 else ''}")

    # Verify update fields exist in table
    for spec in field_specs:
        if spec.db_field not in col_types:
            print(f"WARNING: Column '{spec.db_field}' not found in table '{table_name}'")
            print(f"Available: {', '.join(col_types.keys())}")

    # Preview (always show preview)
    matched, unmatched, will_update = preview_changes(
        conn, table_name, model_name, data,
        match_fields, field_specs,
        args.use_external_id, args.create_missing, col_types
    )

    if args.dry_run:
        print("\n[DRY RUN COMPLETE] No changes made. Remove --dry-run to execute.")
        conn.close()
        return

    if will_update == 0 and (not args.create_missing or unmatched == 0) and not dry_run:
        print("\nNothing to do.")
        conn.close()
        return

    # Confirm before executing
    total_ops = will_update + (unmatched if args.create_missing else 0)
    print(f"\nAbout to execute {total_ops} database operation(s).")
    response = input("Proceed? (yes/no): ").strip().lower()
    if response not in ('yes', 'y'):
        print("Import cancelled.")
        conn.close()
        return

    execute_import(
        conn, table_name, model_name, data,
        match_fields, field_specs,
        args.use_external_id, args.create_missing, col_types,
        args.batch_size
    )

    conn.close()
    print("\n[COMPLETE]")


if __name__ == '__main__':
    main()
