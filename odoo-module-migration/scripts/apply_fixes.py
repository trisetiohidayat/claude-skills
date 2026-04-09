#!/usr/bin/env python3
"""
Apply generated fix patches to module files.

Usage:
    python3 apply_fixes.py \
        --fixes ./module_migration/fixes.json \
        --module ./module_migration/roedl/asb_project_followers \
        --dry-run true
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime


def apply_fix(file_path: Path, old_code: str, new_code: str, dry_run: bool = True) -> bool:
    """Apply a single fix to a file."""
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    content = file_path.read_text()

    # Simple string replacement
    if old_code in content:
        if not dry_run:
            new_content = content.replace(old_code, new_code)
            file_path.write_text(new_content)
            print(f"  ✅ Applied: {file_path.name}")
        else:
            print(f"  🔍 Would apply: {file_path.name}")
        return True

    # Try regex replacement for more complex cases
    try:
        if re.search(re.escape(old_code), content):
            if not dry_run:
                new_content = re.sub(re.escape(old_code), new_code, content)
                file_path.write_text(new_content)
                print(f"  ✅ Applied (regex): {file_path.name}")
            else:
                print(f"  🔍 Would apply (regex): {file_path.name}")
            return True
    except Exception as e:
        print(f"  ❌ Regex error: {e}")

    print(f"  ⚠️  Pattern not found in file")
    return False


def apply_fixes(fixes_json: dict, module_path: Path, dry_run: bool = True) -> dict:
    """Apply all auto-applicable fixes."""
    applied = []
    failed = []
    skipped = []

    fixes = fixes_json.get('fixes', [])

    for fix in fixes:
        if not fix.get('auto_apply', False):
            skipped.append({
                'file': fix['file'],
                'reason': 'Not auto-applicable',
                'description': fix.get('description', '')
            })
            continue

        # Find the file
        file_path = module_path / fix['file']

        # Try different paths
        if not file_path.exists():
            file_path = module_path / 'migrated' / fix['file']

        if not file_path.exists():
            # Try to find it
            for pattern in ['**/*.py', '**/*.xml']:
                for f in module_path.glob(pattern):
                    if fix['file'] in str(f):
                        file_path = f
                        break

        success = apply_fix(
            file_path,
            fix['old_code'],
            fix['new_code'],
            dry_run
        )

        if success:
            applied.append({
                'file': fix['file'],
                'type': fix.get('type'),
                'description': fix.get('description', '')
            })
        else:
            failed.append({
                'file': fix['file'],
                'old_code': fix.get('old_code'),
                'reason': 'Pattern not found or file missing'
            })

    return {
        'applied': applied,
        'failed': failed,
        'skipped': skipped,
        'dry_run': dry_run
    }


def main():
    parser = argparse.ArgumentParser(description='Apply migration fixes')
    parser.add_argument('--fixes', required=True, help='Path to fixes JSON')
    parser.add_argument('--module', required=True, help='Path to module directory')
    parser.add_argument('--dry-run', default='true', help='Dry run mode (default: true)')

    args = parser.parse_args()

    # Load fixes
    fixes_path = Path(args.fixes)
    if not fixes_path.exists():
        print(f"Error: Fixes file not found: {args.fixes}")
        return

    fixes_json = json.loads(fixes_path.read_text())

    # Module path
    module_path = Path(args.module)
    if not module_path.exists():
        print(f"Error: Module path not found: {args.module}")
        return

    dry_run = args.dry_run.lower() == 'true'

    print(f"Applying fixes to {module_path.name} (dry-run: {dry_run})")

    # Apply fixes
    result = apply_fixes(fixes_json, module_path, dry_run)

    print(f"\n✅ Fix application {'simulation' if dry_run else ''} complete!")
    print(f"   - Applied: {len(result['applied'])}")
    print(f"   - Failed: {len(result['failed'])}")
    print(f"   - Skipped: {len(result['skipped'])}")

    if result['failed']:
        print(f"\n⚠️  Failed fixes:")
        for f in result['failed']:
            print(f"   - {f['file']}: {f['reason']}")

    if result['skipped']:
        print(f"\nℹ️  Skipped fixes (manual review required):")
        for s in result['skipped']:
            print(f"   - {s['file']}: {s['reason']}")

    # Save result
    result_path = module_path / 'fix_application_result.json'
    if not dry_run:
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n   Result saved to: {result_path}")


if __name__ == '__main__':
    main()
