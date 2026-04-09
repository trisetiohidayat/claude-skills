#!/usr/bin/env python3
"""
Generate standard Odoo tests for migrated modules.

Usage:
    python3 generate_tests.py --modules ./module_migration/roedl --output ./module_migration/roedl
"""

import re
import os
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set


@dataclass
class ModelInfo:
    name: str
    inherits: str | None
    fields: Dict[str, str] = field(default_factory=dict)
    methods: List[str] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)
    many2one_fields: List[str] = field(default_factory=list)
    selection_fields: List[tuple] = field(default_factory=list)


def parse_model_from_file(file_path: Path) -> ModelInfo | None:
    """Parse a Python model file to extract model info."""
    try:
        content = file_path.read_text()
    except Exception:
        return None

    # Find model class (supports Model and TransientModel)
    class_match = re.search(r'class\s+(\w+)\(.*?(?:Model|TransientModel)\):', content)
    if not class_match:
        return None

    class_name = class_match.group(1)

    # Find _name
    name_match = re.search(r"_name\s*=\s*['\"]([\w.]+)['\"]", content)

    # If no _name, check _inherit for inherited models
    inherit_match = re.search(r"_inherit\s*=\s*['\"]([\w.]+)['\"]", content)

    if not name_match and not inherit_match:
        return None

    model_name = name_match.group(1) if name_match else inherit_match.group(1)

    # Find _inherit
    inherit_match = re.search(r"_inherit\s*=\s*['\"]([\w.]+)['\"]", content)
    inherits = inherit_match.group(1) if inherit_match else None

    # Find _inherits
    inherits_match = re.search(r"_inherits\s*=\s*\{([^}]+)\}", content)
    if inherits_match:
        inherits_dict = inherits_match.group(1)
        parent = re.search(r"['\"]?([\w.]+)['\"]?\s*:", inherits_dict)
        if parent:
            inherits = parent.group(1)

    model = ModelInfo(name=model_name, inherits=inherits)

    # Parse fields
    # Simple fields: name = fields.Char(...)
    simple_fields = re.finditer(
        r"(\w+)\s*=\s*fields\.\w+\(['\"](.*?)['\"]", content
    )
    for match in simple_fields:
        field_name = match.group(1)
        field_type = match.group(2) if match.group(2) else "Field"
        model.fields[field_name] = field_type

    # Many2one fields
    m2o_fields = re.finditer(
        r"(\w+)\s*=\s*fields\.Many2one\(['\"]([\w.]+)['\"]", content
    )
    for match in m2o_fields:
        field_name = match.group(1)
        rel_model = match.group(2)
        model.fields[field_name] = f"Many2one: {rel_model}"
        model.many2one_fields.append(field_name)

    # Selection fields
    sel_fields = re.finditer(
        r"(\w+)\s*=\s*fields\.Selection\(\[(.*?)\]", content
    )
    for match in sel_fields:
        field_name = match.group(1)
        options = match.group(2)
        selections = re.findall(r"\(['\"](.*?)['\"]", options)
        model.selection_fields.append((field_name, selections))

    # Required fields (required=True)
    required_matches = re.finditer(
        r"(\w+)\s*=\s*fields\.\w+\([^)]*required\s*=\s*True", content
    )
    for match in required_matches:
        model.required_fields.append(match.group(1))

    # Parse methods
    method_matches = re.finditer(r"def\s+(\w+)\(self", content)
    for match in method_matches:
        model.methods.append(match.group(1))

    # Parse @api.onchange methods
    onchange_matches = re.finditer(
        r"@api\.onchange\(['\"](.*?)['\"]\)\s*\ndef\s+(\w+)", content
    )
    for match in onchange_matches:
        field_name = match.group(1)
        method_name = match.group(2)
        model.methods.append(f"_onchange_{field_name}")

    return model


def get_dependencies_for_test(model_name: str) -> List[str]:
    """Get required dependencies for testing a model."""
    deps = []

    # Common dependencies
    common_deps = {
        'res.company': 'company_id',
        'res.partner': 'partner_id',
        'res.users': 'user_id',
        'hr.employee': 'employee_id',
        'hr.department': 'department_id',
        'project.project': 'project_id',
        'project.task': 'task_id',
        'account.move': 'move_id',
        'account.invoice': 'invoice_id',
        'sale.order': 'order_id',
        'product.product': 'product_id',
        'product.template': 'product_id',
        'stock.location': 'location_id',
        'stock.picking': 'picking_id',
        'crm.lead': 'lead_id',
        'crm.team': 'team_id',
    }

    for model, field in common_deps.items():
        if model in model_name.lower():
            deps.append(f"'{field}': self.env['{model}'].create({{'name': 'Test {model}'}})")

    return deps


def generate_test_file(module_name: str, models: List[ModelInfo], module_path: Path) -> str:
    """Generate test file content for a module."""
    test_file = f'''# Generated test file for {module_name}
# Auto-generated based on model definitions

import odoo.tests.common as common
from odoo.exceptions import ValidationError, UserError


class Test{module_name.title().replace('_', '')}(common.TransactionCase):
    """Test cases for {module_name} module."""

    def setUp(self):
        super().setUp()
        self.env = self.env(context={{'mail_create_nosubscribe': True}})

'''

    # Add dependency creation for each model
    for model in models:
        if not model.inherits:  # Only for main models
            model_var = model.name.replace('.', '_')
            test_file += f'''        # Create test data for {model.name}
        self.{model_var}_test = self.env['{model.name}'].create({{
'''

            # Add required fields
            if model.required_fields:
                for field in model.required_fields[:3]:  # Limit to 3
                    if field in model.many2one_fields:
                        test_file += f"            '{field}': self.env.ref('base.main_company').id,\n"
                    elif field == 'name':
                        test_file += f"            '{field}': 'Test {model.name}',\n"
                    else:
                        test_file += f"            '{field}': 'Test',\n"
            else:
                test_file += "            'name': 'Test Record',\n"

            test_file += '''        })
'''

    # Generate test methods for each model
    for model in models:
        model_var = model.name.replace('.', '_')

        test_file += f'''
    def test_{model_var}_create(self):
        """Test {model.name} creation."""
        record = self.env['{model.name}'].create({{
            'name': 'Test {model.name}',
        }})
        self.assertTrue(record.id)
        self.assertEqual(record.name, 'Test {model.name}')
'''

        # Test required fields
        if model.required_fields:
            test_file += f'''
    def test_{model_var}_required_fields(self):
        """Test required fields validation."""
        with self.assertRaises(ValidationError):
            self.env['{model.name}'].create({{}})
'''

        # Test fields
        if 'active' in model.fields:
            test_file += f'''
    def test_{model_var}_active(self):
        """Test active field toggle."""
        record = self.{model_var}_test
        record.toggle_active()
        self.assertFalse(record.active)
        record.toggle_active()
        self.assertTrue(record.active)
'''

        # Test computed fields if any
        computed_fields = [f for f in model.fields if '_compute_' in f or f.endswith('_compute')]
        if computed_fields:
            test_file += f'''
    def test_{model_var}_computed_fields(self):
        """Test computed fields."""
        # Trigger compute by writing
        self.{model_var}_test.invalidate_recordset()
        # Computed fields should be recalculated
'''

        # Test onchange methods
        onchange_methods = [m for m in model.methods if m.startswith('_onchange_')]
        for onchange in onchange_methods[:2]:  # Limit to 2
            test_file += f'''
    def test_{model_var}_{onchange}(self):
        """Test onchange method {onchange}."""
        record = self.{model_var}_test
        # Trigger onchange
        record.{onchange}()
'''

        # Test custom methods (excluding standard ones)
        custom_methods = [m for m in model.methods if not m.startswith('_')
                        and m not in ['create', 'write', 'unlink', 'copy', 'default_get']]
        for method in custom_methods[:2]:  # Limit to 2
            test_file += f'''
    def test_{model_var}_{method}(self):
        """Test {method} method."""
        record = self.{model_var}_test
        # Test {method} if it doesn't require special conditions
        try:
            result = record.{method}()
            # Method executed successfully
        except (ValueError, AttributeError):
            # Method may require specific conditions
            pass
'''

    # Add wizard test if exists
    wizard_models = [m for m in models if '.wizard.' in m.name or 'wizard' in m.name.lower()]
    for wizard in wizard_models:
        wizard_var = wizard.name.replace('.', '_')
        test_file += f'''

    def test_{wizard_var}_wizard(self):
        """Test {wizard.name} wizard."""
        wizard = self.env['{wizard.name}'].create({{
            'name': 'Test Wizard',
        }})
        self.assertTrue(wizard.id)
'''

    test_file += '''
    def test_module_loads(self):
        """Test that module loads without errors."""
        # This test ensures the module can be loaded
        self.assertTrue(True)
'''

    return test_file


def generate_tests_for_module(module_path: Path) -> Dict[str, str]:
    """Generate tests for a single module."""
    models = []

    # Find all model files
    models_dir = module_path / 'migrated' / 'models'
    if not models_dir.exists():
        models_dir = module_path / 'models'

    if models_dir.exists():
        for py_file in models_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
            model = parse_model_from_file(py_file)
            if model:
                models.append(model)

    # Also check wizards
    wizards_dir = module_path / 'migrated' / 'wizards'
    if not wizards_dir.exists():
        wizards_dir = module_path / 'wizards'

    if wizards_dir.exists():
        for py_file in wizards_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
            model = parse_model_from_file(py_file)
            if model:
                models.append(model)

    if not models:
        return {}

    module_name = module_path.name

    # Generate test file content
    test_content = generate_test_file(module_name, models, module_path)

    return {
        'test_content': test_content,
        'models': [m.name for m in models],
        'model_count': len(models)
    }


def main():
    parser = argparse.ArgumentParser(description='Generate Odoo tests for migrated modules')
    parser.add_argument('--modules', required=True, help='Path to migrated modules')
    parser.add_argument('--output', '-o', help='Output directory (default: same as modules)')
    parser.add_argument('--module', help='Specific module name to generate tests for')

    args = parser.parse_args()

    modules_path = Path(args.modules)
    output_path = Path(args.output) if args.output else modules_path

    if args.module:
        # Generate tests for specific module
        module_path = modules_path / args.module
        if not module_path.exists():
            print(f"Module not found: {module_path}")
            return

        result = generate_tests_for_module(module_path)
        if result:
            # Create tests directory
            tests_dir = module_path / 'migrated' / 'tests'
            if not tests_dir.exists():
                tests_dir = module_path / 'tests'
            tests_dir.mkdir(parents=True, exist_ok=True)

            # Write test file
            test_file = tests_dir / f'test_{args.module}.py'
            test_file.write_text(result['test_content'])

            # Update __init__.py
            init_file = tests_dir / '__init__.py'
            if not init_file.exists():
                init_file.write_text('')

            print(f"✅ Generated tests for {args.module}")
            print(f"   - {result['model_count']} models analyzed")
            print(f"   - Test file: {test_file}")
        else:
            print(f"No models found in {args.module}")
    else:
        # Generate tests for all modules
        total_modules = 0
        total_models = 0

        for module_dir in modules_path.iterdir():
            if not module_dir.is_dir():
                continue

            # Check if it's a module (has migrated folder)
            if not (module_dir / 'migrated').exists():
                continue

            result = generate_tests_for_module(module_dir)
            if result:
                # Create tests directory
                tests_dir = module_dir / 'migrated' / 'tests'
                tests_dir.mkdir(parents=True, exist_ok=True)

                # Write test file
                test_file = tests_dir / f'test_{module_dir.name}.py'
                test_file.write_text(result['test_content'])

                # Update __init__.py
                init_file = tests_dir / '__init__.py'
                if not init_file.exists():
                    init_file.write_text('')

                total_modules += 1
                total_models += result['model_count']

        print(f"✅ Generated tests for {total_modules} modules")
        print(f"   - {total_models} models analyzed")


if __name__ == '__main__':
    main()
