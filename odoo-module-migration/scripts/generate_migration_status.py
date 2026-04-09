#!/usr/bin/env python3
"""
Generate and update MIGRATION_STATUS.md for Odoo module migration.

Usage:
    # Generate initial status file
    python3 generate_migration_status.py \
        --source-version 15.0 \
        --target-version 17.0 \
        --modules module_a,module_b,module_c \
        --test-type syntax,load,integration \
        --output ./module_migration/MIGRATION_STATUS.md

    # Update after each module
    python3 generate_migration_status.py \
        --update \
        --module module_a \
        --status DONE \
        --changes "models: 2 files, views: 1 file" \
        --test-result PASSED \
        --output ./module_migration/MIGRATION_STATUS.md

    # Add issue
    python3 generate_migration_status.py \
        --issue \
        --module module_a \
        --issue "View XPath error" \
        --resolution "Deactivated broken view" \
        --output ./module_migration/MIGRATION_STATUS.md
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def parse_modules(modules_str):
    """Parse comma-separated modules list."""
    return [m.strip() for m in modules_str.split(',') if m.strip()]


def calculate_dependency_levels(modules, custom_modules_path):
    """
    Calculate dependency levels for modules based on their __manifest__.py.

    Returns a dict: {module_name: {'level': int, 'deps': list, 'depended_by': list}}
    """
    levels = {}
    all_deps = {}

    # First pass: collect all dependencies
    for module in modules:
        module_path = Path(custom_modules_path) / module
        manifest_path = module_path / '__manifest__.py'

        deps = []
        if manifest_path.exists():
            try:
                # Read manifest.py and extract dependencies
                with open(manifest_path, 'r') as f:
                    content = f.read()
                    # Simple regex to extract 'depends' list
                    import re
                    match = re.search(r"'depends'\s*:\s*\[(.*?)\]", content, re.DOTALL)
                    if match:
                        deps_str = match.group(1)
                        # Extract module names
                        deps = re.findall(r"'(\w+)'", deps_str)
            except Exception as e:
                print(f"Warning: Could not parse manifest for {module}: {e}")

        all_deps[module] = [d for d in deps if d in modules]  # Only custom deps

    # Second pass: calculate levels
    def get_level(module, visited=None):
        if visited is None:
            visited = set()

        if module in visited:
            return 0  # Circular dependency protection
        visited.add(module)

        deps = all_deps.get(module, [])
        if not deps:
            return 0

        return max(get_level(dep, visited) + 1 for dep in deps)

    for module in modules:
        levels[module] = {
            'level': get_level(module),
            'deps': all_deps.get(module, []),
            'depended_by': []
        }

    # Calculate depended_by
    for module, data in levels.items():
        for dep in data['deps']:
            if dep in levels:
                levels[dep]['depended_by'].append(module)

    return levels


def generate_initial_status(source_version, target_version, modules, test_types, output_path):
    """Generate initial MIGRATION_STATUS.md."""

    # Try to find custom modules path (assume parent of output)
    custom_modules_path = str(Path(output_path).parent.parent) if output_path else './custom_modules'

    # Calculate dependency levels
    levels = calculate_dependency_levels(modules, custom_modules_path)

    # Group by level
    level_groups = {}
    for module, data in levels.items():
        level = data['level']
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(module)

    # Generate markdown
    test_types_str = ', '.join(test_types) if isinstance(test_types, list) else test_types

    md = f"""# Migration Status: (Project Name)
- **Source Version:** Odoo {source_version}
- **Target Version:** Odoo {target_version}
- **Date Started:** {datetime.now().strftime('%Y-%m-%d')}
- **Test Types:** {test_types_str}
- **Current Module:** (None - migration not started)

## Dependency Graph (Level-based)

```
"""
    for level in sorted(level_groups.keys()):
        modules_at_level = level_groups[level]
        md += f"Level {level}: {', '.join(modules_at_level)}\n"

    md += """```

## Progress

| # | Module | Level | Dependencies | Custom Deps | Status | Changes | Testing |
|---|--------|-------|-------------|-------------|--------|---------|---------|
"""

    for i, module in enumerate(modules, 1):
        data = levels[module]
        deps = ', '.join(data['deps']) if data['deps'] else '-'
        depended = ', '.join(data['depended_by']) if data['depended_by'] else '-'
        md += f"| {i} | {module} | {data['level']} | base | {deps} | ⏳ PENDING | - | ⏳ |\n"

    md += f"""
## Current Context

**No module in progress yet.**

## Module Details (Completed)

*(Will be populated as modules are completed)*

## Issues Log

| # | Module | Issue | Status | Resolution |
|---|--------|-------|--------|------------|
| 1 | | | ⏭️ PENDING | |

## Next Steps

- [ ] Start migration with first module at Level 0
- [ ] Run tests after each module
- [ ] Update status after each module completion
- [ ] Generate final CLAUDE.md after all modules complete
"""

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(md)

    print(f"✅ Generated MIGRATION_STATUS.md at: {output_path}")
    print(f"   Modules: {', '.join(modules)}")
    print(f"   Dependency levels: {', '.join(f'L{k}: {v}' for k, v in sorted(level_groups.items()))}")
    return levels


def update_module_status(module, status, changes, test_result, output_path):
    """Update status for a specific module."""

    if not os.path.exists(output_path):
        print(f"❌ ERROR: MIGRATION_STATUS.md not found at: {output_path}")
        print("   Run without --update first to generate initial file.")
        sys.exit(1)

    with open(output_path, 'r') as f:
        content = f.read()

    # Update Current Module
    content = content.replace(
        "- **Current Module:** (None - migration not started)",
        f"- **Current Module:** {module}"
    )

    # Update progress table
    import re

    # Find and update the module row
    pattern = rf"(\| \d+ \| {re.escape(module)} \| \d+ \| [^|]+ \| [^|]+ \|) ⏳ PENDING (\| [^|]+ \|) ⏳ (\|)"
    replacement = rf"\1 {status} \2 {test_result} \3"
    content = re.sub(pattern, replacement, content)

    # Add to Module Details section if DONE
    if status == "✅ DONE":
        # Extract level from progress table
        level_match = re.search(rf"\|\s*\d+\s*\|\s*{re.escape(module)}\s*\|\s*(\d+)", content)
        level = level_match.group(1) if level_match else "?"

        # Find dependencies
        deps_match = re.search(rf"\|\s*\d+\s*\|\s*{re.escape(module)}\s*\|\s*\d+\s*\|\s*base\s*\|\s*([^|]+)", content)
        deps = deps_match.group(1).strip() if deps_match else "-"

        # Find depended by
        depended_by = []
        for m in re.findall(rf"\|\s*\d+\s*\|\s*(\w+)\s*\|", content):
            row_match = re.search(rf"\|\s*\d+\s*\|\s*{re.escape(m)}\s*\|.*?\|\s*base\s*\|\s*([^|]+)", content, re.DOTALL)
            if row_match and module in row_match.group(1):
                depended_by.append(m)
        depended_by_str = ', '.join(depended_by) if depended_by else "-"

        module_detail = f"""
### {module} (DONE - Level {level})
- **Depends On:** [{deps}]
- **Depended By:** [{depended_by_str}]
- **Files Changed:** {changes}
- **Test Result:** {test_result}
- **Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        # Insert after "## Module Details (Completed)"
        content = content.replace(
            "## Module Details (Completed)\n\n*(Will be populated as modules are completed)*",
            f"## Module Details (Completed)\n{module_detail}"
        )

    # Update Next Steps - mark current module as complete
    content = f"- [x] Complete {module}\n" + content

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Updated MIGRATION_STATUS.md")
    print(f"   Module: {module}")
    print(f"   Status: {status}")
    print(f"   Changes: {changes}")
    print(f"   Test: {test_result}")


def add_issue(module, issue, resolution, output_path):
    """Add an issue to the issues log."""

    if not os.path.exists(output_path):
        print(f"❌ ERROR: MIGRATION_STATUS.md not found at: {output_path}")
        sys.exit(1)

    with open(output_path, 'r') as f:
        content = f.read()

    # Add new issue row
    issue_row = f"| | {module} | {issue} | ✅ FIXED | {resolution} |\n"

    # Find the issues table and insert before the last row
    content = content.replace(
        "| 1 | | | ⏭️ PENDING | |",
        f"| | {module} | {issue} | ✅ FIXED | {resolution} |\n| 1 | | | ⏭️ PENDING | |"
    )

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Added issue to MIGRATION_STATUS.md")
    print(f"   Module: {module}")
    print(f"   Issue: {issue}")
    print(f"   Resolution: {resolution}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate and update MIGRATION_STATUS.md for Odoo module migration'
    )

    # Mode selection
    parser.add_argument('--update', action='store_true',
                        help='Update status for a completed module')
    parser.add_argument('--issue', action='store_true',
                        help='Add an issue to the log')

    # Generation args
    parser.add_argument('--source-version', type=str,
                        help='Source Odoo version (e.g., 15.0)')
    parser.add_argument('--target-version', type=str,
                        help='Target Odoo version (e.g., 17.0)')
    parser.add_argument('--modules', type=str,
                        help='Comma-separated list of modules')
    parser.add_argument('--test-type', type=str,
                        help='Comma-separated test types (syntax,load,integration)')

    # Update args
    parser.add_argument('--module', type=str,
                        help='Module name to update')
    parser.add_argument('--status', type=str,
                        choices=['✅ DONE', '🔄 IN PROGRESS', '❌ FAILED'],
                        help='New status for the module')
    parser.add_argument('--changes', type=str,
                        help='Description of changes made')
    parser.add_argument('--test-result', type=str,
                        help='Test result (e.g., PASSED, FAILED, ⏭️ SKIP)')

    # Issue args
    parser.add_argument('--issue-text', type=str,
                        help='Issue description')
    parser.add_argument('--resolution', type=str,
                        help='Issue resolution')

    # Output
    parser.add_argument('--output', type=str, default='./MIGRATION_STATUS.md',
                        help='Output path for MIGRATION_STATUS.md')

    args = parser.parse_args()

    # Validate arguments
    if args.update:
        if not args.module or not args.status:
            print("ERROR: --update requires --module, --status")
            sys.exit(1)
        update_module_status(
            args.module,
            args.status,
            args.changes or '-',
            args.test_result or '⏭️ SKIP',
            args.output
        )
    elif args.issue:
        if not args.module or not args.issue_text:
            print("ERROR: --issue requires --module and --issue-text")
            sys.exit(1)
        add_issue(
            args.module,
            args.issue_text,
            args.resolution or '-',
            args.output
        )
    else:
        # Generate initial
        if not all([args.source_version, args.target_version, args.modules]):
            print("ERROR: Initial generation requires --source-version, --target-version, --modules")
            sys.exit(1)

        modules = parse_modules(args.modules)
        test_types = parse_modules(args.test_type) if args.test_type else ['syntax']

        generate_initial_status(
            args.source_version,
            args.target_version,
            modules,
            test_types,
            args.output
        )


if __name__ == '__main__':
    main()
