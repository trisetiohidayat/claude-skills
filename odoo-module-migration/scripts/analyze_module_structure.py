#!/usr/bin/env python3
"""
Deep analyze of Odoo custom module structure.

Usage:
    python3 analyze_module_structure.py \
        --module ./module_migration/roedl/asb_project_followers \
        --output ./module_migration/roedl/asb_project_followers/blueprint.json
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Optional
from datetime import datetime


@dataclass
class FieldInfo:
    name: str
    field_type: str
    relation: Optional[str] = None
    required: bool = False
    readonly: bool = False
    default: Optional[str] = None
    compute: Optional[str] = None
    related: Optional[str] = None
    ondelete: Optional[str] = None


@dataclass
class ModelInfo:
    name: str
    inherits: Optional[str] = None
    inherits_dict: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, FieldInfo] = field(default_factory=dict)
    methods: List[str] = field(default_factory=list)
    onchange_methods: List[str] = field(default_factory=list)
    constraint_methods: List[str] = field(default_factory=list)
    sql_constraints: List[tuple] = field(default_factory=list)


@dataclass
class ViewInfo:
    name: str
    view_type: str
    model: Optional[str] = None
    inherit_id: Optional[str] = None
    arch: str = ""


@dataclass
class SecurityInfo:
    acl_file: Optional[str] = None
    record_rules: List[dict] = field(default_factory=list)
    groups: List[dict] = field(default_factory=list)


@dataclass
class WizardInfo:
    name: str
    model_name: str
    methods: List[str] = field(default_factory=list)


@dataclass
class ControllerInfo:
    name: str
    routes: List[str] = field(default_factory=list)


@dataclass
class ModuleBlueprint:
    module_name: str
    version: str
    path: str
    models: Dict[str, ModelInfo] = field(default_factory=dict)
    views: List[ViewInfo] = field(default_factory=list)
    security: SecurityInfo = field(default_factory=SecurityInfo)
    wizards: List[WizardInfo] = field(default_factory=list)
    controllers: List[ControllerInfo] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    external_ids: List[str] = field(default_factory=list)
    data_files: List[str] = field(default_factory=list)


def parse_manifest(module_path: Path) -> dict:
    """Parse __manifest__.py to extract dependencies."""
    # Check in root first
    manifest_file = module_path / '__manifest__.py'
    if not manifest_file.exists():
        manifest_file = module_path / '__openerp__.py'
    # Also check in migrated subdirectory
    if not manifest_file.exists():
        manifest_file = module_path / 'migrated' / '__manifest__.py'
    if not manifest_file.exists():
        manifest_file = module_path / 'migrated' / '__openerp__.py'

    if not manifest_file.exists():
        return {}

    content = manifest_file.read_text()

    # Extract depends
    depends_match = re.search(r"'depends'\s*:\s*\[(.*?)\]", content, re.DOTALL)
    depends = []
    if depends_match:
        depends = re.findall(r"'(\w+)'", depends_match.group(1))

    # Extract version
    version_match = re.search(r"'version'\s*:\s*['\"](.*?)['\"]", content)
    version = version_match.group(1) if version_match else "1.0"

    return {
        'depends': depends,
        'version': version,
        'name': module_path.name
    }


def parse_model_definition(content: str, file_path: str) -> Optional[ModelInfo]:
    """Parse a Python model file to extract detailed info."""
    # Find all model classes in the file (Model, TransientModel, Abstract)
    class_pattern = r'class\s+(\w+)\(.*?(?:Model|TransientModel|Abstract)\):'
    classes = re.finditer(class_pattern, content)

    models = {}

    for class_match in classes:
        class_name = class_match.group(1)
        class_start = class_match.start()

        # Find next class or end of file
        next_class = re.search(class_pattern, content[class_start + 100:])
        if next_class:
            class_end = class_start + 100 + next_class.start()
        else:
            class_end = len(content)

        class_content = content[class_start:class_end]

        # Find _name (required for new models, but may use _inherit for extensions)
        name_match = re.search(r"_name\s*=\s*['\"]([\w.]+)['\"]", class_content)
        if not name_match:
            # For inherited models, use _inherit as the model name if _name not present
            inherit_match = re.search(r"_inherit\s*=\s*['\"]([\w.]+)['\"]", class_content)
            if inherit_match:
                model_name = inherit_match.group(1)
            else:
                continue  # No _name or _inherit found
        else:
            model_name = name_match.group(1)

        # Find _inherit (separate from the fallback logic above)
        inherit_match = re.search(r"_inherit\s*=\s*['\"]([\w.]+)['\"]", class_content)
        inherits = inherit_match.group(1) if inherit_match else None

        # Find _inherits
        inherits_dict = {}
        inherits_dict_match = re.search(r"_inherits\s*=\s*\{(.*?)\}", class_content, re.DOTALL)
        if inherits_dict_match:
            dict_content = inherits_dict_match.group(1)
            for match in re.finditer(r"['\"]?([\w.]+)['\"]?\s*:\s*['\"]?([\w.]+)['\"]?", dict_content):
                inherits_dict[match.group(1)] = match.group(2)

        model = ModelInfo(
            name=model_name,
            inherits=inherits,
            inherits_dict=inherits_dict
        )

        # Parse fields
        field_pattern = r'(\w+)\s*=\s*fields\.(\w+)\('
        for field_match in re.finditer(field_pattern, class_content):
            field_name = field_match.group(1)
            field_type = field_match.group(2)

            # Extract field attributes
            field_def_start = field_match.start()
            field_def_end = class_content.find(')', field_def_start)
            field_def = class_content[field_def_start:field_def_end+1] if field_def_end > 0 else ""

            field_info = FieldInfo(
                name=field_name,
                field_type=field_type,
                required='required=True' in field_def or 'required = True' in field_def,
                readonly='readonly=True' in field_def or 'readonly = True' in field_def,
            )

            # Many2one relation
            if field_type == 'Many2one':
                rel_match = re.search(r"'([\w.]+)'", field_def)
                if rel_match:
                    field_info.relation = rel_match.group(1)

            # Default value
            default_match = re.search(r"default\s*=\s*['\"]?([^'\")]+)", field_def)
            if default_match:
                field_info.default = default_match.group(1).strip()

            # Compute
            if 'compute=' in field_def:
                field_info.compute = 'computed'

            # Related
            if 'related=' in field_def:
                field_info.related = 'related'

            model.fields[field_name] = field_info

        # Parse methods
        for method_match in re.finditer(r'def\s+(\w+)\(self', class_content):
            model.methods.append(method_match.group(1))

        # Parse onchange methods
        for onchange_match in re.finditer(r'@api\.onchange\([\'"]([\w\.]+)[\'"]\)', class_content):
            model.onchange_methods.append(onchange_match.group(1))

        # Parse constraints
        for const_match in re.finditer(r'@api\.constrains\([\'"]([\w,\s]+)[\'"]\)', class_content):
            model.constraint_methods.append(const_match.group(1))

        # SQL constraints
        for sql_match in re.finditer(r'_sql_constraints\s*=\s*\[(.*?)\]', class_content, re.DOTALL):
            sql_content = sql_match.group(1)
            for name_match in re.finditer(r'\(["\']([\w_]+)["\']\s*,\s*["\'](.*?)["\']', sql_content):
                model.sql_constraints.append((name_match.group(1), name_match.group(2)))

        models[model_name] = model

    return models if models else None


def parse_views(module_path: Path) -> List[ViewInfo]:
    """Parse all view XML files."""
    views = []

    # Check in various locations
    view_dirs = [
        module_path / 'views',
        module_path / 'migrated' / 'views',
    ]

    for view_dir in view_dirs:
        if not view_dir.exists():
            continue

        for xml_file in view_dir.glob('*.xml'):
            try:
                content = xml_file.read_text()

                # Find all view definitions
                for view_match in re.finditer(r'<(\w+)(?:\s+[^>]*)?>(.*?)</\1>', content, re.DOTALL):
                    view_type = view_match.group(1)
                    if view_type in ['form', 'tree', 'kanban', 'search', 'graph', 'pivot', 'calendar']:
                        view = ViewInfo(
                            name=xml_file.stem,
                            view_type=view_type,
                            model=None
                        )

                        # Extract model attribute
                        model_match = re.search(r'model=["\']([\w.]+)["\']', view_match.group(2))
                        if model_match:
                            view.model = model_match.group(1)

                        # Extract inherit_id
                        inherit_match = re.search(r'<field\s+name=["\']inherit_id["\']\s+ref=["\']([\w.]+)["\']', view_match.group(2))
                        if inherit_match:
                            view.inherit_id = inherit_match.group(1)

                        views.append(view)
            except Exception:
                pass

    return views


def parse_security(module_path: Path) -> SecurityInfo:
    """Parse security files."""
    security = SecurityInfo()

    security_dirs = [
        module_path / 'security',
        module_path / 'migrated' / 'security',
    ]

    for sec_dir in security_dirs:
        if not sec_dir.exists():
            continue

        # ACL files
        for acl_file in sec_dir.glob('*.csv'):
            if 'access' in acl_file.name.lower():
                security.acl_file = str(acl_file)

        # XML security files
        for xml_file in sec_dir.glob('*.xml'):
            try:
                content = xml_file.read_text()

                # Record rules
                for rule_match in re.finditer(r'<record\s+id=["\']([^"\']+)["\'].*?model=["\']([^"\']+)["\']', content, re.DOTALL):
                    security.record_rules.append({
                        'id': rule_match.group(1),
                        'model': rule_match.group(2)
                    })

                # Groups
                for group_match in re.finditer(r'<group\s+id=["\']([^"\']+)["\']', content):
                    security.groups.append({'id': group_match.group(1)})
            except Exception:
                pass

    return security


def parse_wizards(module_path: Path) -> List[WizardInfo]:
    """Parse wizard files."""
    wizards = []

    wizard_dirs = [
        module_path / 'wizards',
        module_path / 'migrated' / 'wizards',
    ]

    for wizard_dir in wizard_dirs:
        if not wizard_dir.exists():
            continue

        for py_file in wizard_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue

            try:
                content = py_file.read_text()

                # Find wizard class
                class_match = re.search(r'class\s+(\w+)\(.*?TransientModel\):', content)
                if class_match:
                    class_name = class_match.group(1)

                    # Find _name
                    name_match = re.search(r"_name\s*=\s*['\"]([\w.]+)['\"]", content)
                    model_name = name_match.group(1) if name_match else f"wizard.{py_file.stem}"

                    wizard = WizardInfo(
                        name=py_file.stem,
                        model_name=model_name
                    )

                    # Find methods
                    for method_match in re.finditer(r'def\s+(\w+)\(self', content):
                        wizard.methods.append(method_match.group(1))

                    wizards.append(wizard)
            except Exception:
                pass

    return wizards


def parse_controllers(module_path: Path) -> List[ControllerInfo]:
    """Parse controller files."""
    controllers = []

    controller_dirs = [
        module_path / 'controllers',
        module_path / 'migrated' / 'controllers',
    ]

    for controller_dir in controller_dirs:
        if not controller_dir.exists():
            continue

        for py_file in controller_dirs.glob('*.py'):
            if py_file.name.startswith('__'):
                continue

            try:
                content = py_file.read_text()

                # Find controller class
                class_match = re.search(r'class\s+(\w+)\(.*?Controller\):', content)
                if class_match:
                    controller = ControllerInfo(name=py_file.stem)

                    # Find routes
                    for route_match in re.finditer(r'@http\.route\([\'"]([^\'"]+)[\'"]', content):
                        controller.routes.append(route_match.group(1))

                    controllers.append(controller)
            except Exception:
                pass

    return controllers


def parse_external_ids(module_path: Path) -> List[str]:
    """Parse external IDs from all XML files."""
    external_ids = []

    for xml_file in module_path.glob('**/*.xml'):
        try:
            content = xml_file.read_text()
            for id_match in re.finditer(r'id=["\']([^"\']+)["\']', content):
                external_ids.append(id_match.group(1))
        except Exception:
            pass

    return list(set(external_ids))


def parse_data_files(module_path: Path) -> List[str]:
    """Parse data file references from manifest."""
    data_files = []

    # Find manifest in root or migrated
    manifest_paths = [
        module_path / '__manifest__.py',
        module_path / '__openerp__.py',
        module_path / 'migrated' / '__manifest__.py',
        module_path / 'migrated' / '__openerp__.py',
    ]

    content = ""
    for manifest_path in manifest_paths:
        if manifest_path.exists():
            content = manifest_path.read_text()
            break

    # Find data entries
    data_match = re.search(r"'data'\s*:\s*\[(.*?)\]", content, re.DOTALL)
    if data_match:
        data_files = re.findall(r'["\']([^"\']+\.xml)["\']', data_match.group(1))

    return data_files


def analyze_module(module_path: str, version: str = "15.0") -> ModuleBlueprint:
    """Main function to analyze a module."""
    module_path = Path(module_path)

    if not module_path.exists():
        raise ValueError(f"Module path does not exist: {module_path}")

    blueprint = ModuleBlueprint(
        module_name=module_path.name,
        version=version,
        path=str(module_path)
    )

    # Parse manifest
    manifest = parse_manifest(module_path)
    blueprint.dependencies['manifest'] = manifest.get('depends', [])
    if manifest.get('version'):
        blueprint.version = manifest.get('version', version)

    # Parse all model files
    model_dirs = [
        module_path / 'models',
        module_path / 'migrated' / 'models',
    ]

    for model_dir in model_dirs:
        if not model_dir.exists():
            continue

        for py_file in model_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue

            try:
                content = py_file.read_text()
                models = parse_model_definition(content, str(py_file))
                if models:
                    blueprint.models.update(models)
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")

    # Parse views
    blueprint.views = parse_views(module_path)

    # Parse security
    blueprint.security = parse_security(module_path)

    # Parse wizards
    blueprint.wizards = parse_wizards(module_path)

    # Parse controllers
    blueprint.controllers = parse_controllers(module_path)

    # Parse external IDs
    blueprint.external_ids = parse_external_ids(module_path)

    # Parse data files
    blueprint.data_files = parse_data_files(module_path)

    # Build dependency references from models
    model_refs = set()
    for model in blueprint.models.values():
        if model.inherits:
            model_refs.add(model.inherits)
        for field in model.fields.values():
            if field.relation:
                model_refs.add(field.relation)

    blueprint.dependencies['model_references'] = list(model_refs)

    return blueprint


def main():
    parser = argparse.ArgumentParser(description='Deep analyze Odoo module structure')
    parser.add_argument('--module', required=True, help='Path to module directory')
    parser.add_argument('--version', default='15.0', help='Module version')
    parser.add_argument('--output', '-o', required=True, help='Output JSON file')

    args = parser.parse_args()

    print(f"Analyzing module: {args.module}")

    blueprint = analyze_module(args.module, args.version)

    # Convert to dict
    result = {
        'module_name': blueprint.module_name,
        'version': blueprint.version,
        'path': blueprint.path,
        'generated_at': datetime.now().isoformat(),
        'models': {},
        'views': [asdict(v) for v in blueprint.views],
        'security': asdict(blueprint.security),
        'wizards': [asdict(w) for w in blueprint.wizards],
        'controllers': [asdict(c) for c in blueprint.controllers],
        'dependencies': blueprint.dependencies,
        'external_ids': blueprint.external_ids,
        'data_files': blueprint.data_files
    }

    # Convert models
    for model_name, model in blueprint.models.items():
        result['models'][model_name] = {
            'name': model.name,
            'inherits': model.inherits,
            'inherits_dict': model.inherits_dict,
            'fields': {k: asdict(v) for k, v in model.fields.items()},
            'methods': model.methods,
            'onchange_methods': model.onchange_methods,
            'constraint_methods': model.constraint_methods,
            'sql_constraints': model.sql_constraints
        }

    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Module analysis complete!")
    print(f"   - Models: {len(blueprint.models)}")
    print(f"   - Views: {len(blueprint.views)}")
    print(f"   - Wizards: {len(blueprint.wizards)}")
    print(f"   - Controllers: {len(blueprint.controllers)}")
    print(f"   - Dependencies: {len(blueprint.dependencies.get('manifest', []))}")
    print(f"   - External IDs: {len(blueprint.external_ids)}")
    print(f"   Output: {args.output}")


if __name__ == '__main__':
    main()
