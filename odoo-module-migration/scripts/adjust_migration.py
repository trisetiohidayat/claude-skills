#!/usr/bin/env python3
"""
Adjust module migration based on parsed upgrade errors.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_errors(error_file: str) -> Dict[str, Any]:
    """Load parsed errors from JSON file."""
    with open(error_file, 'r') as f:
        return json.load(f)


def get_all_errors(error_data: Dict[str, Any]) -> List[Dict]:
    """Extract all errors from error data structure."""
    if 'all_errors' in error_data:
        return error_data.get('all_errors', [])
    elif 'errors' in error_data:
        return error_data.get('errors', [])
    else:
        return []


def analyze_missing_column(error: Dict) -> Dict[str, str]:
    """Analyze missing column error and suggest fix."""
    message = error.get('message', '')

    # Extract table and column names
    match = re.search(r'column\s+(\w+)\s+does not exist', message, re.IGNORECASE)
    if match:
        column = match.group(1)
        # Try to find table name
        table_match = re.search(r'table\s+"(\w+)"', message, re.IGNORECASE)
        table = table_match.group(1) if table_match else 'unknown'

        return {
            'action': 'add_column',
            'table': table,
            'column': column,
            'sql': f'ALTER TABLE {table} ADD COLUMN {column} VARCHAR;'
        }

    return {'action': 'unknown', 'message': message}


def analyze_missing_table(error: Dict) -> Dict[str, str]:
    """Analyze missing table error and suggest fix."""
    message = error.get('message', '')

    match = re.search(r'relation\s+"(\w+)"\s+does not exist', message, re.IGNORECASE)
    if match:
        table = match.group(1)
        return {
            'action': 'create_table',
            'table': table,
            'sql': f'CREATE TABLE {table} (id SERIAL PRIMARY KEY); -- Needs manual definition'
        }

    return {'action': 'unknown', 'message': message}


def analyze_missing_xmlid(error: Dict) -> Dict[str, str]:
    """Analyze missing XMLID error."""
    message = error.get('message', '')

    # Extract module and xmlid
    match = re.search(r"External ID not found.*?['\"]?([\w.]+)['\"]?", message)
    xmlid = match.group(1) if match else 'unknown'

    # Extract module name
    module_match = re.search(r'^([\w_]+)\.', xmlid)
    module = module_match.group(1) if module_match else 'unknown'

    return {
        'action': 'fix_xmlid',
        'xmlid': xmlid,
        'module': module,
        'suggestion': f'Check if {module} module data needs regeneration'
    }


def analyze_missing_module(error: Dict) -> Dict[str, str]:
    """Analyze missing module error."""
    message = error.get('message', '')

    match = re.search(r"module\s+['\"]?(\w+)['\"]?\s+not found", message, re.IGNORECASE)
    module = match.group(1) if match else 'unknown'

    return {
        'action': 'install_module',
        'module': module,
        'suggestion': f'Install {module} before migrating custom modules'
    }


def analyze_duplicate_key(error: Dict) -> Dict[str, str]:
    """Analyze duplicate key error."""
    message = error.get('message', '')

    match = re.search(r'Key\s+\(([^)]+)\)=([^)]+)', message)
    if match:
        key = match.group(1)
        value = match.group(2)

        return {
            'action': 'remove_duplicate',
            'key': key,
            'value': value,
            'sql': f'-- Remove duplicate: DELETE FROM table WHERE key = {value}'
        }

    return {'action': 'unknown', 'message': message}


def analyze_broken_view(error: Dict) -> Dict[str, str]:
    """Analyze broken view error."""
    message = error.get('message', '')

    match = re.search(r'view\s+["\']?(\w+)["\']?', message, re.IGNORECASE)
    view = match.group(1) if match else 'unknown'

    return {
        'action': 'fix_view',
        'view': view,
        'suggestion': f'Recreate or update view {view} for new version'
    }


def analyze_error(error: Dict) -> Dict[str, Any]:
    """Analyze an error and return suggested fix."""
    category = error.get('category', 'unknown')

    analyzers = {
        'missing_column': analyze_missing_column,
        'missing_table': analyze_missing_table,
        'missing_xmlid': analyze_missing_xmlid,
        'missing_module': analyze_missing_module,
        'duplicate_key': analyze_duplicate_key,
        'broken_view': analyze_broken_view,
    }

    analyzer = analyzers.get(category, lambda e: {'action': 'unknown', 'category': category})
    result = analyzer(error)
    result['category'] = category
    result['level'] = error.get('level', 'ERROR')
    result['original_message'] = error.get('message', '')

    return result


def apply_fix_to_module(fix: Dict, modules_path: str, dry_run: bool = True) -> List[str]:
    """Apply fix to module code."""
    changes = []
    action = fix.get('action', 'unknown')

    if action == 'fix_view' or action == 'fix_xmlid':
        # These require manual intervention
        changes.append(f"# Manual fix needed: {fix.get('suggestion', '')}")

    elif action == 'install_module':
        # Could update __manifest__.py dependencies
        changes.append(f"# Install module: {fix.get('module', 'unknown')}")

    return changes


def generate_module_adjustments(error_data: Dict[str, Any], modules_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """Generate adjustment plan for modules."""
    errors = get_all_errors(error_data)

    # Group by module
    module_fixes = {}
    global_fixes = []

    for error in errors:
        fix = analyze_error(error)
        category = fix.get('category', 'unknown')

        # Determine affected module
        if 'module' in fix:
            module = fix['module']
        else:
            module = 'global'

        if module not in module_fixes:
            module_fixes[module] = []

        module_fixes[module].append(fix)

        if category not in ['missing_module', 'install_module']:
            global_fixes.append(fix)

    # Generate adjustment report
    adjustments = {
        'total_errors': len(errors),
        'modules_affected': list(module_fixes.keys()),
        'by_module': {},
        'global_fixes': global_fixes,
        'recommendations': []
    }

    # Add recommendations
    if 'missing_module' in str(module_fixes):
        adjustments['recommendations'].append(
            "Install missing modules before running module migration"
        )

    if 'missing_column' in str(module_fixes):
        adjustments['recommendations'].append(
            "Add missing columns to models before migration"
        )

    if 'broken_view' in str(module_fixes):
        adjustments['recommendations'].append(
            "Migrate views to new Odoo version format"
        )

    # Format output
    for module, fixes in module_fixes.items():
        adjustments['by_module'][module] = {
            'fix_count': len(fixes),
            'fixes': fixes,
            'needs_attention': any(f.get('action') == 'unknown' for f in fixes)
        }

    return adjustments


def main():
    parser = argparse.ArgumentParser(
        description='Adjust module migration based on upgrade errors'
    )
    parser.add_argument(
        'error_file',
        help='JSON file with parsed errors (from parse_upgrade_report.py)'
    )
    parser.add_argument(
        '--modules-path',
        help='Path to custom modules directory'
    )
    parser.add_argument(
        '-o', '--output',
        default='migration_adjustments.json',
        help='Output file for adjustments (default: migration_adjustments.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually apply the changes (default is dry-run)'
    )

    args = parser.parse_args()

    # Load errors
    if not Path(args.error_file).exists():
        print(f"Error: File not found: {args.error_file}", file=sys.stderr)
        sys.exit(1)

    error_data = load_errors(args.error_file)

    # Generate adjustments
    adjustments = generate_module_adjustments(
        error_data,
        args.modules_path,
        dry_run=args.dry_run
    )

    # Write output
    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(adjustments, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    print(f"Generated adjustments for {len(adjustments['modules_affected'])} modules")
    print(f"Output written to: {args.output}")

    # Summary
    print("\nSummary:")
    print(f"  Total errors: {adjustments['total_errors']}")
    print(f"  Modules affected: {len(adjustments['modules_affected'])}")

    if adjustments['recommendations']:
        print("\nRecommendations:")
        for rec in adjustments['recommendations']:
            print(f"  - {rec}")

    if args.dry_run and not args.apply:
        print("\n[DRY RUN] No changes made. Use --apply to make changes.")

    # Show details
    print("\nModule Details:")
    for module, data in adjustments['by_module'].items():
        print(f"\n  {module}:")
        print(f"    Fixes needed: {data['fix_count']}")
        for fix in data['fixes'][:3]:  # Show first 3
            print(f"      - {fix.get('action', 'unknown')}: {fix.get('category', '')}")
        if data['fix_count'] > 3:
            print(f"      ... and {data['fix_count'] - 3} more")


if __name__ == '__main__':
    main()
