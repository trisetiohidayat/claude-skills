#!/usr/bin/env python3
"""
Generate automatic fix patches for migration issues.

Usage:
    python3 generate_fixes.py \
        --analysis ./module_migration/analysis.json \
        --module ./module_migration/roedl/asb_project_followers \
        --output ./module_migration/fixes.json
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Fix:
    file: str
    fix_type: str  # MODEL_INHERIT, FIELD_RENAME, etc.
    description: str
    old_code: str
    new_code: str
    auto_apply: bool = True
    line_number: Optional[int] = None


@dataclass
class ManualReview:
    file: str
    issue: str
    suggestion: str
    line_number: Optional[int] = None


def find_file_in_module(module_path: Path, file_pattern: str) -> Optional[Path]:
    """Find a file in the module matching the pattern."""
    # Direct match
    direct = module_path / file_pattern
    if direct.exists():
        return direct

    # Search in common directories
    for subdir in ['', 'migrated/']:
        for prefix in ['', 'wizards/', 'models/', 'views/']:
            candidate = module_path / subdir / prefix / file_pattern
            if candidate.exists():
                return candidate

    # Glob search
    for pattern in ['**/*.py', '**/*.xml']:
        for f in module_path.glob(pattern):
            if file_pattern in f.name:
                return f

    return None


def generate_model_inherit_fix(module_path: Path, old_model: str, new_model: str) -> List[Fix]:
    """Generate fixes for _inherit changes."""
    fixes = []

    # Search for _inherit = 'old.model'
    for py_file in module_path.glob('**/*.py'):
        if py_file.name.startswith('__'):
            continue

        content = py_file.read_text()
        old_pattern = rf"_inherit\s*=\s*['\"]({re.escape(old_model)})['\"]"
        match = re.search(old_pattern, content)

        if match:
            # Find line number
            lines = content[:match.start()].split('\n')
            line_number = len(lines)

            fix = Fix(
                file=str(py_file.relative_to(module_path)),
                fix_type='MODEL_INHERIT',
                description=f"Update _inherit from '{old_model}' to '{new_model}'",
                old_code=f"_inherit = '{old_model}'",
                new_code=f"_inherit = '{new_model}'",
                line_number=line_number
            )
            fixes.append(fix)

    return fixes


def generate_view_model_fix(module_path: Path, old_model: str, new_model: str) -> List[Fix]:
    """Generate fixes for model references in views."""
    fixes = []

    # Search for model="old.model" in XML
    for xml_file in module_path.glob('**/*.xml'):
        content = xml_file.read_text()

        # Match model="old.model"
        old_pattern = rf'model\s*=\s*["\']({re.escape(old_model)})["\']'
        matches = list(re.finditer(old_pattern, content))

        if matches:
            # Simple replacement - in practice would need more sophisticated handling
            new_content = re.sub(old_pattern, f'model="{new_model}"', content)

            fix = Fix(
                file=str(xml_file.relative_to(module_path)),
                fix_type='VIEW_MODEL_REFERENCE',
                description=f"Update model reference from '{old_model}' to '{new_model}'",
                old_code=f'model="{old_model}"',
                new_code=f'model="{new_model}"',
                auto_apply=True
            )
            fixes.append(fix)

    return fixes


def generate_external_id_fix(module_path: Path, old_model: str, new_model: str) -> List[Fix]:
    """Generate fixes for external ID references."""
    fixes = []

    # Search for ref="module.old_model" in XML
    for xml_file in module_path.glob('**/*.xml'):
        content = xml_file.read_text()

        # Match ref="module.old_model"
        old_ref = old_model.replace('.', '_')
        new_ref = new_model.replace('.', '_')
        pattern = rf'ref\s*=\s*["\']([\w.]*){re.escape(old_ref)}["\']'
        matches = list(re.finditer(pattern, content))

        if matches:
            fix = Fix(
                file=str(xml_file.relative_to(module_path)),
                fix_type='EXTERNAL_ID',
                description=f"Update external ID reference from '{old_ref}' to '{new_ref}'",
                old_code=f'ref="...{old_ref}"',
                new_code=f'ref="...{new_ref}"',
                auto_apply=True
            )
            fixes.append(fix)

    return fixes


def check_manual_review(module_path: Path, model_name: str, wizard_fields: List[dict]) -> List[ManualReview]:
    """Check for issues that need manual review."""
    reviews = []

    # Check wizard fields that depend on old models
    for wizard in wizard_fields:
        for field_name, field_info in wizard.get('fields', {}).items():
            relation = field_info.get('relation', '')

            # Check if relation model might be removed
            if relation:
                reviews.append(ManualReview(
                    file=f"wizards/{wizard.get('name', 'unknown')}.py",
                    issue=f"Field '{field_name}' has relation to '{relation}'",
                    suggestion="Verify this model exists in target Odoo version"
                ))

    return reviews


def generate_fixes(analysis: dict, module_path: Path) -> dict:
    """Generate all fixes based on analysis."""
    fixes = []
    manual_reviews = []

    model_changes = analysis.get('model_changes', {})

    for model_name, change_info in model_changes.items():
        change_type = change_info.get('change_type')
        replacement = change_info.get('replacement')

        if change_type == 'RENAMED' and replacement:
            # Generate model inherit fixes
            fixes.extend(generate_model_inherit_fix(module_path, model_name, replacement))

            # Generate view fixes
            fixes.extend(generate_view_model_fix(module_path, model_name, replacement))

            # Generate external ID fixes
            fixes.extend(generate_external_id_fix(module_path, model_name, replacement))

        elif change_type == 'REMOVED':
            # Check if there's a known replacement we can suggest
            if change_info.get('confidence', 0) < 50:
                manual_reviews.append(ManualReview(
                    file="unknown",
                    issue=f"Model '{model_name}' was removed with no clear replacement",
                    suggestion="Manual research required to find replacement or alternative approach"
                ))

    # Check for field changes that might need manual review
    field_changes = analysis.get('field_changes', [])
    if field_changes:
        for fc in field_changes:
            if fc.get('change_type') == 'REMOVED':
                manual_reviews.append(ManualReview(
                    file=f"models/{fc.get('model_name', 'unknown').replace('.', '/')}.py",
                    issue=f"Field '{fc.get('field_name')}' was removed from model '{fc.get('model_name')}'",
                    suggestion="Check if field was renamed or removed in target version"
                ))

    # Convert fixes to dict
    fixes_dict = [
        {
            'file': f.file,
            'type': f.fix_type,
            'description': f.description,
            'old_code': f.old_code,
            'new_code': f.new_code,
            'auto_apply': f.auto_apply,
            'line_number': f.line_number
        }
        for f in fixes
    ]

    manual_dict = [
        {
            'file': m.file,
            'issue': m.issue,
            'suggestion': m.suggestion,
            'line_number': m.line_number
        }
        for m in manual_reviews
    ]

    return {
        'fixes': fixes_dict,
        'manual_review_required': manual_dict,
        'summary': {
            'total_fixes': len(fixes_dict),
            'auto_applicable': len([f for f in fixes_dict if f['auto_apply']]),
            'manual_review': len(manual_dict)
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Generate migration fixes')
    parser.add_argument('--analysis', required=True, help='Path to analysis JSON')
    parser.add_argument('--module', required=True, help='Path to module directory')
    parser.add_argument('--output', '-o', required=True, help='Output fixes JSON file')

    args = parser.parse_args()

    # Load analysis
    analysis_path = Path(args.analysis)
    if not analysis_path.exists():
        print(f"Error: Analysis file not found: {args.analysis}")
        return

    analysis = json.loads(analysis_path.read_text())

    # Module path
    module_path = Path(args.module)
    if not module_path.exists():
        print(f"Error: Module path not found: {args.module}")
        return

    print(f"Generating fixes for {analysis.get('module_name')}")

    # Generate fixes
    result = generate_fixes(analysis, module_path)

    # Add metadata
    result['metadata'] = {
        'module_name': analysis.get('module_name'),
        'source_version': analysis.get('source_version'),
        'target_version': analysis.get('target_version'),
        'generated_at': datetime.now().isoformat()
    }

    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Fix generation complete!")
    print(f"   - Total fixes: {result['summary']['total_fixes']}")
    print(f"   - Auto-applicable: {result['summary']['auto_applicable']}")
    print(f"   - Manual review: {result['summary']['manual_review']}")
    print(f"   Output: {args.output}")


if __name__ == '__main__':
    main()
