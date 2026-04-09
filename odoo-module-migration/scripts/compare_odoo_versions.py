#!/usr/bin/env python3
"""
Odoo Version Comparison Script

Compare old and new Odoo versions to identify breaking changes.
This helps identify what needs to be reviewed manually during migration.

Usage:
    python3 compare_odoo_versions.py <old_odoo_path> <new_odoo_path> <source_ver> <target_ver>

Example:
    python3 compare_odoo_versions.py /path/to/odoo-15.0 /path/to/odoo-17.0 15.0 17.0
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime
import argparse


class OdooVersionComparator:
    """Compare two Odoo versions to identify breaking changes."""

    # Key files to compare (relative paths)
    KEY_FILES = {
        'models': ['odoo/models.py', 'odoo/osv/model.py'],
        'fields': ['odoo/fields.py'],
        'orm': ['odoo/osv/orm.py'],
    }

    # Patterns that indicate deprecated/changed APIs
    DEPRECATION_PATTERNS = {
        'api.multi': '@api.multi is deprecated',
        'api.v7': 'Old API (api.v7) not supported',
        'api.cr': 'Use self._cr instead of api.cr',
        'cr.execute': 'Direct cr.execute needs review',
        'self.env.cr': 'Use self._cr instead',
        'workflow': 'Workflow engine removed in v12+',
        'wkf': 'Workflow removed in v12+',
        'osv.Model': 'Use odoo.models.Model instead',
        'osv.TransientModel': 'Use odoo.models.TransientModel instead',
        'osv_memory': 'Use odoo.models.TransientModel instead',
        'openerp': 'Use odoo instead of openerp',
    }

    # Common module directories to check
    COMMON_MODULES = [
        'account', 'sale', 'purchase', 'stock', 'mrp',
        'project', 'crm', 'hr', 'website', 'point_of_sale',
    ]

    def __init__(self, old_path: str, new_path: str, source_ver: str, target_ver: str):
        self.old_path = Path(old_path).resolve()
        self.new_path = Path(new_path).resolve()
        self.source_ver = source_ver
        self.target_ver = target_ver
        self.breaking_changes: List[Dict[str, str]] = []
        self.deprecated_apis: Set[str] = set()
        self.renamed_modules: Dict[str, str] = {}
        self.new_required_fields: List[str] = []

    def validate_paths(self) -> Tuple[bool, str]:
        """Validate that the provided paths exist."""
        if not self.old_path.exists():
            return False, f"Old Odoo path does not exist: {self.old_path}"
        if not self.new_path.exists():
            return False, f"New Odoo path does not exist: {self.new_path}"
        return True, "Paths validated"

    def find_files(self, base_path: Path, pattern: str) -> List[Path]:
        """Find files matching a pattern."""
        return list(base_path.glob(f'**/{pattern}'))

    def read_file(self, filepath: Path) -> str:
        """Read file content safely."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Error reading {filepath}: {e}"

    def extract_models(self, path: Path) -> Dict[str, Dict]:
        """Extract model definitions from Odoo source."""
        models = {}

        # Look for model definitions in addons
        addons_path = path / 'odoo' / 'addons'
        if not addons_path.exists():
            addons_path = path / 'addons'

        if not addons_path.exists():
            return models

        for module_dir in addons_path.iterdir():
            if not module_dir.is_dir():
                continue

            models_dir = module_dir / 'models'
            if not models_dir.exists():
                continue

            for py_file in models_dir.glob('*.py'):
                content = self.read_file(py_file)
                # Extract class definitions
                class_pattern = r'class\s+(\w+)\(.*Model\)'
                matches = re.findall(class_pattern, content)
                if matches:
                    models[module_dir.name] = {
                        'classes': matches,
                        'file': str(py_file)
                    }

        return models

    def extract_views(self, path: Path) -> Dict[str, List[str]]:
        """Extract view definitions."""
        views = {}

        addons_path = path / 'odoo' / 'addons'
        if not addons_path.exists():
            addons_path = path / 'addons'

        if not addons_path.exists():
            return views

        for module_dir in addons_path.iterdir():
            if not module_dir.is_dir():
                continue

            views_dir = module_dir / 'views'
            if not views_dir.exists():
                continue

            view_types = []
            for xml_file in views_dir.glob('*.xml'):
                content = self.read_file(xml_file)
                # Extract view types
                view_types.extend(re.findall(r'<(\w+)\s+.*model=', content))

            if view_types:
                views[module_dir.name] = list(set(view_types))

        return views

    def check_deprecated_patterns(self, path: Path) -> List[Dict[str, str]]:
        """Check for deprecated API usage in Odoo source."""
        issues = []

        addons_path = path / 'odoo' / 'addons'
        if not addons_path.exists():
            addons_path = path / 'addons'

        if not addons_path.exists():
            return issues

        for py_file in addons_path.glob('**/*.py'):
            content = self.read_file(py_file)

            for pattern, message in self.DEPRECATION_PATTERNS.items():
                if pattern in content:
                    issues.append({
                        'pattern': pattern,
                        'file': str(py_file.relative_to(path)),
                        'message': message,
                        'status': 'deprecated_in_target' if 'v7' in pattern or 'api.multi' in pattern else 'needs_review'
                    })

        return issues

    def compare_modules(self) -> Dict[str, Any]:
        """Compare modules between old and new version."""
        old_models = self.extract_models(self.old_path)
        new_models = self.extract_models(self.new_path)

        # Find modules that exist in old but not in new
        old_module_names = set(old_models.keys())
        new_module_names = set(new_models.keys())

        removed_modules = old_module_names - new_module_names
        added_modules = new_module_names - old_module_names

        return {
            'removed_modules': sorted(removed_modules),
            'added_modules': sorted(added_modules),
            'common_modules': sorted(old_module_names & new_module_names),
        }

    def compare_model_fields(self) -> Dict[str, Any]:
        """Compare model fields between versions."""
        changes = {
            'renamed_models': {},
            'removed_fields': {},
            'new_required_fields': [],
        }

        # This is a simplified comparison
        # In reality, you'd need to parse the actual field definitions

        return changes

    def generate_breaking_changes_report(self) -> Dict[str, Any]:
        """Generate comprehensive breaking changes report."""

        # Validate paths first
        valid, message = self.validate_paths()
        if not valid:
            return {'error': message}

        report = {
            'metadata': {
                'source_version': self.source_ver,
                'target_version': self.target_ver,
                'old_path': str(self.old_path),
                'new_path': str(self.new_path),
                'generated_at': datetime.now().isoformat(),
            },
            'summary': {
                'total_breaking_changes': 0,
                'deprecated_apis': [],
                'removed_modules': [],
                'renamed_modules': [],
                'new_requirements': [],
            },
            'details': {
                'module_comparison': {},
                'deprecated_patterns_old': [],
                'deprecated_patterns_new': [],
                'view_changes': {},
            }
        }

        # Compare modules
        module_comp = self.compare_modules()
        report['details']['module_comparison'] = module_comp
        report['summary']['removed_modules'] = module_comp.get('removed_modules', [])

        # Check deprecated patterns
        old_deprecated = self.check_deprecated_patterns(self.old_path)
        new_deprecated = self.check_deprecated_patterns(self.new_path)

        report['details']['deprecated_patterns_old'] = old_deprecated
        report['details']['deprecated_patterns_new'] = new_deprecated

        # Find what APIs are deprecated in new but still used in old
        old_patterns = set(d['pattern'] for d in old_deprecated)
        new_patterns = set(d['pattern'] for d in new_deprecated)

        # APIs that exist in old but are deprecated in new
        still_deprecated = old_patterns & new_patterns

        # Add version-specific breaking changes
        source_num = int(self.source_ver.split('.')[0])
        target_num = int(self.target_ver.split('.')[0])

        if target_num >= 16:
            report['summary']['deprecated_apis'].extend([
                {'api': '@api.multi', 'replacement': '@api.model or regular method', 'since': 'v12'},
                {'api': 'workflow/wkf', 'replacement': 'Automatic states/flows', 'since': 'v12'},
                {'api': 'cr.execute', 'replacement': 'self._cr.execute()', 'since': 'v12'},
            ])

        if target_num >= 17:
            report['summary']['deprecated_apis'].extend([
                {'api': 'request.cr', 'replacement': 'request.env.cr', 'since': 'v17'},
                {'api': 'fields.Date.context_today', 'replacement': 'fields.Date.today()', 'since': 'v17'},
                {'api': 'osv.Model', 'replacement': 'odoo.models.Model', 'since': 'v17'},
            ])

        if target_num >= 18:
            report['summary']['deprecated_apis'].extend([
                {'api': 'XMLRPC', 'replacement': 'JSON-RPC or new API', 'since': 'v18'},
            ])

        # Count total breaking changes
        report['summary']['total_breaking_changes'] = (
            len(module_comp.get('removed_modules', [])) +
            len(report['summary']['deprecated_apis']) +
            len(still_deprecated)
        )

        return report

    def save_report(self, output_dir: str = '.') -> str:
        """Save report to file."""
        report = self.generate_breaking_changes_report()

        if 'error' in report:
            print(f"Error: {report['error']}")
            return ""

        # Save JSON
        json_path = os.path.join(output_dir, f'breaking_changes_{self.source_ver}_{self.target_ver}.json')
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Save Markdown
        md_path = os.path.join(output_dir, f'breaking_changes_{self.source_ver}_{self.target_ver}.md')
        self._save_markdown_report(md_path, report)

        print(f"Breaking changes report saved to:")
        print(f"  - {json_path}")
        print(f"  - {md_path}")

        return json_path

    def _save_markdown_report(self, path: str, report: Dict):
        """Save report as markdown."""
        md = f"""# Odoo Breaking Changes Report

## Migration: {self.source_ver} → {self.target_ver}

**Generated:** {report['metadata']['generated_at']}
**Old Path:** {report['metadata']['old_path']}
**New Path:** {report['metadata']['new_path']}

---

## Summary

| Category | Count |
|----------|-------|
| Total Breaking Changes | {report['summary']['total_breaking_changes']} |
| Removed Modules | {len(report['summary']['removed_modules'])} |
| Deprecated APIs | {len(report['summary']['deprecated_apis'])} |

---

## Deprecated APIs

These APIs are deprecated in the target version and need to be reviewed:

"""
        for api in report['summary']['deprecated_apis']:
            md += f"""### {api['api']}

- **Replacement:** {api['replacement']}
- **Deprecated Since:** v{api['since']}

"""

        if report['summary']['removed_modules']:
            md += """## Removed Modules

The following modules no longer exist in the target version:

"""
            for module in report['summary']['removed_modules']:
                md += f"- `{module}`\n"

            md += "\n**Action:** Check if custom module depends on these and find alternatives.\n\n"

        md += """## Module Comparison

| Status | Modules |
|--------|---------|
| Removed | {removed} |
| Added | {added} |
| Common | {common} |

""".format(
            removed=len(report['details']['module_comparison'].get('removed_modules', [])),
            added=len(report['details']['module_comparison'].get('added_modules', [])),
            common=len(report['details']['module_comparison'].get('common_modules', []))
        )

        md += """## Recommendations

1. **Review Deprecated APIs:** Update code to use new APIs
2. **Check Removed Modules:** Find alternatives or remove dependencies
3. **Test Thoroughly:** Run tests to catch runtime errors
4. **Manual Review:** Some changes require business logic review

---

*This report was generated by Odoo Migration Skill*
"""

        with open(path, 'w') as f:
            f.write(md)


def main():
    parser = argparse.ArgumentParser(
        description='Compare Odoo versions to identify breaking changes'
    )
    parser.add_argument(
        'old_path',
        help='Path to old Odoo source code'
    )
    parser.add_argument(
        'new_path',
        help='Path to new Odoo source code'
    )
    parser.add_argument(
        'source_ver',
        help='Source version (e.g., 15.0)'
    )
    parser.add_argument(
        'target_ver',
        help='Target version (e.g., 17.0)'
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory for report (default: current directory)'
    )

    args = parser.parse_args()

    comparator = OdooVersionComparator(
        args.old_path,
        args.new_path,
        args.source_ver,
        args.target_ver
    )

    # Run comparison and save report
    report_path = comparator.save_report(args.output)

    if report_path:
        print("\nComparison complete!")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
