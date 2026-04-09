#!/usr/bin/env python3
"""
Compare module models against target Odoo version to detect breaking changes.

Usage:
    python3 compare_versions.py \
        --blueprint ./module_migration/blueprint.json \
        --target-odoo /path/to/odoo-17.0 \
        --output ./module_migration/analysis.json
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from datetime import datetime


@dataclass
class ModelChange:
    model_name: str
    change_type: str  # REMOVED, RENAMED, CHANGED
    old_location: Optional[str] = None
    new_location: Optional[str] = None
    replacement: Optional[str] = None
    confidence: int = 100  # 0-100
    details: List[str] = field(default_factory=list)


@dataclass
class FieldChange:
    model_name: str
    field_name: str
    change_type: str  # TYPE_CHANGED, REQUIRED_ADDED, REQUIRED_REMOVED, etc.
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class MigrationAnalysis:
    source_version: str
    target_version: str
    model_changes: Dict[str, ModelChange] = field(default_factory=dict)
    field_changes: List[FieldChange] = field(default_factory=list)
    method_changes: Dict[str, List[str]] = field(default_factory=dict)
    removed_models: List[str] = field(default_factory=list)
    renamed_models: List[str] = field(default_factory=list)
    changed_models: List[str] = field(default_factory=list)


# Known model replacements across Odoo versions
KNOWN_REPLACEMENTS = {
    # Odoo 15 -> 16
    'mail.wizard.invite': {
        'replacement': 'mail.wizard.followers',
        'reason': 'Replaced by new follower wizard',
        'version': '16.0'
    },
    # Odoo 16 -> 17
    'account.invoice': {
        'replacement': 'account.move',
        'reason': 'Unified move model',
        'version': '16.0'
    },
    'account.invoice.report': {
        'replacement': 'account.move.report',
        'reason': 'Unified move model',
        'version': '16.0'
    },
    'hr.expense': {
        'replacement': 'hr.expense.sheet',
        'reason': 'Expense workflow change',
        'version': '16.0'
    },
    # Odoo 17 removals
    'account.payment.term': {
        'replacement': 'account.payment.term',
        'reason': 'Renamed to account.payment.term',
        'version': '17.0'
    },
    'stock.picking.type': {
        'replacement': 'stock.picking.type',
        'reason': 'Moved to inventory app',
        'version': '17.0'
    },
}


def get_version_from_odoo_path(odoo_path: Path) -> str:
    """Extract version from Odoo source path."""
    # Try to find version from odoo/release.py or setup.py
    release_file = odoo_path / 'odoo' / 'release.py'
    if release_file.exists():
        content = release_file.read_text()
        version_match = re.search(r"version\s*=\s*['\"]([\d.]+)", content)
        if version_match:
            return version_match.group(1)

    # Try from setup.py
    setup_file = odoo_path / 'setup.py'
    if setup_file.exists():
        content = setup_file.read_text()
        version_match = re.search(r"version\s*=\s*['\"]([\d.]+)", content)
        if version_match:
            return version_match.group(1)

    # Try from folder name
    folder_name = odoo_path.name
    version_match = re.search(r'(\d+\.\d+)', folder_name)
    if version_match:
        return version_match.group(1)

    return "unknown"


def find_model_in_odoo(odoo_path: Path, model_name: str) -> Optional[Path]:
    """Search for a model definition in Odoo source."""
    model_path = model_name.replace('.', '/')

    # Search patterns
    search_patterns = [
        odoo_path / 'odoo' / 'addons' / model_path,
        odoo_path / 'addons' / model_path,
    ]

    for pattern in search_patterns:
        # Check if it's a directory with models
        if pattern.exists():
            return pattern
        # Check if it's a file
        py_file = pattern.with_suffix('.py')
        if py_file.exists():
            return py_file

    # Search in all addons
    addons_dir = odoo_path / 'odoo' / 'addons'
    if addons_dir.exists():
        for addon in addons_dir.iterdir():
            if addon.is_dir():
                # Check models directory
                model_dir = addon / 'models'
                if model_dir.exists():
                    for py_file in model_dir.glob('*.py'):
                        content = py_file.read_text()
                        if f"_name = '{model_name}'" in content or f'_name = "{model_name}"' in content:
                            return py_file

    return None


def check_model_exists(odoo_path: Path, model_name: str) -> bool:
    """Check if a model exists in Odoo source."""
    return find_model_in_odoo(odoo_path, model_name) is not None


def get_model_fields(odoo_path: Path, model_name: str) -> Dict[str, str]:
    """Extract field definitions from Odoo model."""
    model_file = find_model_in_odoo(odoo_path, model_name)
    if not model_file or not model_file.is_file():
        return {}

    content = model_file.read_text()
    fields = {}

    # Parse fields
    field_pattern = r'(\w+)\s*=\s*fields\.(\w+)\('
    for match in re.finditer(field_pattern, content):
        field_name = match.group(1)
        field_type = match.group(2)
        fields[field_name] = field_type

    return fields


def check_method_exists(odoo_path: Path, model_name: str, method_name: str) -> bool:
    """Check if a method exists in Odoo model."""
    model_file = find_model_in_odoo(odoo_path, model_name)
    if not model_file or not model_file.is_file():
        return False

    content = model_file.read_text()
    pattern = rf'def\s+{method_name}\s*\('
    return bool(re.search(pattern, content))


def analyze_blueprint(blueprint: dict, target_odoo_path: Path) -> MigrationAnalysis:
    """Analyze blueprint against target Odoo version."""
    analysis = MigrationAnalysis(
        source_version=blueprint.get('version', 'unknown'),
        target_version=get_version_from_odoo_path(target_odoo_path)
    )

    # Get all model references from blueprint
    all_models = set()

    # From models
    for model_name in blueprint.get('models', {}).keys():
        all_models.add(model_name)

    # From wizards ( TransientModels are models too)
    for wizard in blueprint.get('wizards', []):
        model_name = wizard.get('model_name', '')
        if model_name and '.' in model_name:
            all_models.add(model_name)

    # From dependencies (model_references)
    for ref in blueprint.get('dependencies', {}).get('model_references', []):
        all_models.add(ref)

    # From _inherit in models
    for model_data in blueprint.get('models', {}).values():
        if model_data.get('inherits'):
            all_models.add(model_data['inherits'])

    # Analyze each model
    for model_name in all_models:
        # Check if model still exists in target Odoo
        if not check_model_exists(target_odoo_path, model_name):
            # Check if it's a known replacement
            if model_name in KNOWN_REPLACEMENTS:
                replacement_info = KNOWN_REPLACEMENTS[model_name]
                change = ModelChange(
                    model_name=model_name,
                    change_type='RENAMED',
                    replacement=replacement_info['replacement'],
                    confidence=90,
                    details=[replacement_info['reason']]
                )
                analysis.model_changes[model_name] = change
                analysis.renamed_models.append(model_name)
            else:
                # Unknown removal
                change = ModelChange(
                    model_name=model_name,
                    change_type='REMOVED',
                    confidence=50,
                    details=['Model not found in target Odoo version']
                )
                analysis.model_changes[model_name] = change
                analysis.removed_models.append(model_name)
        else:
            # Model exists - check for field changes
            old_fields = blueprint.get('models', {}).get(model_name, {}).get('fields', {})

            if old_fields:
                new_fields = get_model_fields(target_odoo_path, model_name)

                # Check for removed fields
                for field_name in old_fields:
                    if field_name not in new_fields:
                        field_change = FieldChange(
                            model_name=model_name,
                            field_name=field_name,
                            change_type='REMOVED',
                            old_value=old_fields[field_name].get('field_type')
                        )
                        analysis.field_changes.append(field_change)

                # Check for new required fields
                for field_name, field_info in old_fields.items():
                    if field_name in new_fields:
                        old_required = field_info.get('required', False)
                        # Can't easily check new required without deeper parsing

                if analysis.field_changes or model_name in [c.model_name for c in analysis.field_changes]:
                    analysis.changed_models.append(model_name)

    return analysis


def main():
    parser = argparse.ArgumentParser(description='Compare module against target Odoo version')
    parser.add_argument('--blueprint', required=True, help='Path to blueprint JSON')
    parser.add_argument('--target-odoo', required=True, help='Path to target Odoo source')
    parser.add_argument('--output', '-o', required=True, help='Output analysis JSON file')
    parser.add_argument('--source-version', help='Source Odoo version (auto-detect from blueprint if not provided)')

    args = parser.parse_args()

    # Load blueprint
    blueprint_path = Path(args.blueprint)
    if not blueprint_path.exists():
        print(f"Error: Blueprint not found: {args.blueprint}")
        return

    blueprint = json.loads(blueprint_path.read_text())

    # Target Odoo path
    target_odoo = Path(args.target_odoo)
    if not target_odoo.exists():
        print(f"Error: Target Odoo path not found: {args.target_odoo}")
        return

    print(f"Comparing module {blueprint.get('module_name')} against Odoo {get_version_from_odoo_path(target_odoo)}")

    # Analyze
    analysis = analyze_blueprint(blueprint, target_odoo)

    # Convert to dict
    result = {
        'analysis_version': '1.0',
        'module_name': blueprint.get('module_name'),
        'source_version': analysis.source_version,
        'target_version': analysis.target_version,
        'analyzed_at': datetime.now().isoformat(),
        'summary': {
            'removed_models': analysis.removed_models,
            'renamed_models': analysis.renamed_models,
            'changed_models': analysis.changed_models,
            'total_field_changes': len(analysis.field_changes)
        },
        'model_changes': {
            name: {
                'change_type': change.change_type,
                'replacement': change.replacement,
                'confidence': change.confidence,
                'details': change.details
            }
            for name, change in analysis.model_changes.items()
        },
        'field_changes': [
            {
                'model_name': fc.model_name,
                'field_name': fc.field_name,
                'change_type': fc.change_type,
                'old_value': fc.old_value,
                'new_value': fc.new_value
            }
            for fc in analysis.field_changes
        ]
    }

    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Analysis complete!")
    print(f"   - Removed models: {len(analysis.removed_models)}")
    print(f"   - Renamed models: {len(analysis.renamed_models)}")
    print(f"   - Changed models: {len(analysis.changed_models)}")
    print(f"   - Field changes: {len(analysis.field_changes)}")
    print(f"   Output: {args.output}")


if __name__ == '__main__':
    main()
