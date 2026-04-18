#!/usr/bin/env python3
"""
Parse upgrade report from upgrade.odoo.com to extract errors and map to modules.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def detect_format(content: str) -> str:
    """Detect the format of the upgrade report."""
    content = content.strip()
    if content.startswith('{') or content.startswith('['):
        return 'json'
    elif '<html' in content.lower() or '<!DOCTYPE' in content:
        return 'html'
    else:
        return 'text'


def parse_json_report(content: str) -> List[Dict[str, Any]]:
    """Parse JSON format upgrade report."""
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Check for common JSON structures
            if 'errors' in data:
                return data['errors']
            elif 'results' in data:
                return data.get('results', {}).get('errors', [])
            elif 'upgrade' in data:
                return data['upgrade'].get('errors', [])
        return []
    except json.JSONDecodeError:
        return []


def parse_html_report(content: str) -> List[Dict[str, Any]]:
    """Parse HTML format upgrade report."""
    errors = []

    # Extract error blocks from HTML
    error_patterns = [
        r'error[^>]*>(.*?)</',
        r'<div[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</div>',
        r'<pre[^>]*>(.*?Error:.*?)</pre>',
    ]

    # Simple error extraction - look for common error patterns
    lines = content.split('\n')
    current_error = None

    for line in lines:
        if 'ERROR' in line.upper() or 'FATAL' in line.upper() or 'WARNING' in line.upper():
            if current_error:
                errors.append(current_error)
            current_error = {
                'level': 'ERROR' if 'ERROR' in line.upper() else 'WARNING',
                'message': line.strip(),
                'category': categorize_error(line)
            }
        elif current_error:
            current_error['message'] += '\n' + line.strip()

    if current_error:
        errors.append(current_error)

    return errors


def parse_text_report(content: str) -> List[Dict[str, Any]]:
    """Parse plain text format upgrade report."""
    errors = []
    lines = content.split('\n')

    current_error = None

    for line in lines:
        # Detect error start
        if re.search(r'\b(ERROR|FATAL|CRITICAL|WARNING)\b', line, re.IGNORECASE):
            if current_error:
                errors.append(current_error)

            level = 'ERROR'
            if 'FATAL' in line.upper():
                level = 'FATAL'
            elif 'CRITICAL' in line.upper():
                level = 'CRITICAL'
            elif 'WARNING' in line.upper():
                level = 'WARNING'

            current_error = {
                'level': level,
                'message': line.strip(),
                'category': categorize_error(line)
            }
        elif current_error:
            # Continue error message
            if line.strip():
                current_error['message'] += '\n' + line.strip()

    if current_error:
        errors.append(current_error)

    return errors


def categorize_error(message: str) -> str:
    """Categorize error based on message content."""
    msg_lower = message.lower()

    if 'relation' in msg_lower and 'does not exist' in msg_lower:
        return 'missing_table'
    elif 'column' in msg_lower and 'does not exist' in msg_lower:
        return 'missing_column'
    elif 'duplicate key' in msg_lower:
        return 'duplicate_key'
    elif 'view' in msg_lower and ('depends' in msg_lower or 'cannot be located' in msg_lower):
        return 'broken_view'
    elif 'constraint' in msg_lower and 'failed' in msg_lower:
        return 'constraint_failed'
    elif 'module' in msg_lower and 'not found' in msg_lower:
        return 'missing_module'
    elif 'external id' in msg_lower or 'xmlid' in msg_lower:
        return 'missing_xmlid'
    elif 'field' in msg_lower:
        return 'field_error'
    else:
        return 'unknown'


def extract_module_from_error(error: Dict[str, Any]) -> List[str]:
    """Extract module names from error message."""
    message = error.get('message', '')
    modules = []

    # Common patterns for module extraction
    patterns = [
        r"module ['\"]([^'\"]+)['\"]",
        r"module\.(\w+)",
        r"['\"](\w+)['\"] module",
        r"in module ['\"]([^'\"]+)['\"]",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        modules.extend(matches)

    # Known Odoo modules to filter
    known_modules = {
        'base', 'web', 'mail', 'crm', 'sale', 'purchase', 'stock',
        'account', 'invoice', 'accounting', 'hr', 'project', 'portal',
        'l10n_id', 'l10n_de', 'l10n_fr', 'l10n_es', 'l10n',
    }

    # Filter and deduplicate
    modules = [m for m in modules if m.lower() not in known_modules or m in known_modules]
    modules = list(set(modules))

    return modules if modules else ['unknown']


def map_to_custom_modules(errors: List[Dict[str, Any]], modules_path: str = None) -> Dict[str, List[Dict]]:
    """Map errors to custom modules if path provided."""
    if not modules_path:
        return {error['category']: [error] for error in errors}

    # Get list of custom modules
    custom_modules = []
    modules_dir = Path(modules_path)
    if modules_dir.exists():
        custom_modules = [d.name for d in modules_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    # Map errors
    module_errors = {}
    for error in errors:
        error_modules = extract_module_from_error(error)
        for mod in error_modules:
            if mod not in module_errors:
                module_errors[mod] = []
            module_errors[mod].append(error)

    return module_errors


def main():
    parser = argparse.ArgumentParser(
        description='Parse upgrade report from upgrade.odoo.com'
    )
    parser.add_argument(
        'input_file',
        help='Path to upgrade report file'
    )
    parser.add_argument(
        '-o', '--output',
        default='upgrade_errors.json',
        help='Output JSON file (default: upgrade_errors.json)'
    )
    parser.add_argument(
        '--map-modules',
        action='store_true',
        help='Map errors to custom modules'
    )
    parser.add_argument(
        '--modules-path',
        help='Path to custom modules directory'
    )

    args = parser.parse_args()

    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    content = input_path.read_text(encoding='utf-8', errors='ignore')

    # Detect format and parse
    fmt = detect_format(content)

    if fmt == 'json':
        errors = parse_json_report(content)
    elif fmt == 'html':
        errors = parse_html_report(content)
    else:
        errors = parse_text_report(content)

    # Map to modules if requested
    if args.map_modules:
        module_errors = map_to_custom_modules(errors, args.modules_path)
        output_data = {
            'format': fmt,
            'total_errors': len(errors),
            'by_module': module_errors,
            'all_errors': errors
        }
    else:
        output_data = {
            'format': fmt,
            'total_errors': len(errors),
            'errors': errors
        }

    # Write output
    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    print(f"Parsed {len(errors)} errors from {fmt} report")
    print(f"Output written to: {args.output}")

    # Summary
    if errors:
        categories = {}
        for error in errors:
            cat = error.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1

        print("\nError categories:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()
