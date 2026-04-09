#!/usr/bin/env python3
"""
Analyze Odoo module structure and generate Business Context Questionnaire.

This script analyzes custom Odoo modules to identify:
- Custom models (new or inherited)
- Custom fields
- Custom methods with business logic decorators
- Custom views
- Wizards

It generates a business context questionnaire for developer input.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class FieldInfo:
    name: str
    field_type: str
    is_custom: bool = True
    related: str = ""
    computed: str = ""
    default: str = ""
    ondelete: str = ""


@dataclass
class MethodInfo:
    name: str
    decorators: List[str] = field(default_factory=list)
    lines: int = 0


@dataclass
class ModelInfo:
    name: str
    inherits: str = ""
    is_custom: bool = True
    fields: List[FieldInfo] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)


@dataclass
class ViewInfo:
    name: str
    view_type: str
    custom_fields: List[str] = field(default_factory=list)


@dataclass
class WizardInfo:
    model_name: str
    view_name: str


@dataclass
class ModuleAnalysis:
    name: str
    path: str
    models: List[ModelInfo] = field(default_factory=list)
    views: List[ViewInfo] = field(default_factory=list)
    wizards: List[WizardInfo] = field(default_factory=list)
    security_files: List[str] = field(default_factory=list)
    has_api_integration: bool = False
    api_endpoints: List[str] = field(default_factory=list)


def parse_manifest(module_path: Path) -> dict:
    """Parse __manifest__.py or __openerp__.py"""
    for manifest_name in ['__manifest__.py', '__openerp__.py']:
        manifest_path = module_path / manifest_name
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                content = f.read()
                # Safe eval for manifest dict
                try:
                    # Simple regex extraction of dict
                    match = re.search(r'\{(.+)\}', content, re.DOTALL)
                    if match:
                        # Use ast for safe parsing
                        import ast
                        manifest_str = '{' + match.group(1) + '}'
                        # Actually just return basic info by parsing line by line
                        pass
                except:
                    pass

            # Simple extraction
            result = {'name': module_path.name, 'depends': []}
            # Extract depends
            depends_match = re.search(r"['\"]depends['\"]:\s*\[(.*?)\]", content, re.DOTALL)
            if depends_match:
                deps = re.findall(r"['\"](.*?)['\"]", depends_match.group(1))
                result['depends'] = deps
            # Extract name
            name_match = re.search(r"['\"]name['\"]:\s*['\"](.*?)['\"]", content)
            if name_match:
                result['name'] = name_match.group(1)
            return result
    return {'name': module_path.name, 'depends': []}


def parse_models(module_path: Path) -> List[ModelInfo]:
    """Parse all model files in the module."""
    models = []
    models_dir = module_path / 'models'
    if not models_dir.exists():
        return models

    for py_file in models_dir.glob('*.py'):
        if py_file.name.startswith('__'):
            continue

        with open(py_file, 'r') as f:
            content = f.read()

        # Find class definitions
        class_pattern = r'class\s+(\w+)\((.*?)\):'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            inherits_str = match.group(2).strip()

            # Determine if custom or inherited
            is_custom = True
            inherits = ""
            if inherits_str:
                # Check if it inherits from standard Odoo models
                base_models = ['models.Model', 'models.Model', 'models.TransientModel',
                              'models.AbstractModel', 'Model', 'TransientModel']
                if any(base in inherits_str for base in base_models):
                    is_custom = False
                # Extract parent model
                parent_match = re.search(r'models\.(\w+)', inherits_str)
                if parent_match:
                    inherits = parent_match.group(1)

            model_info = ModelInfo(name=class_name, inherits=inherits, is_custom=is_custom)

            # Find fields in this class
            # Look for field definitions
            field_pattern = r'(\w+)\s*=\s*fields\.(\w+)\('
            for field_match in re.finditer(field_pattern, content):
                field_name = field_match.group(1)
                field_type = field_match.group(2)

                # Skip internal fields
                if field_name.startswith('_'):
                    continue

                field_info = FieldInfo(name=field_name, field_type=field_type)

                # Check for related/computed
                field_def_start = field_match.end()
                # Find the rest of the field definition
                rest_match = re.search(rf'{field_name}\s*=\s*fields\.{field_type}\((.*?)\)',
                                      content[field_match.start():field_match.start() + 500])
                if rest_match:
                    field_def = rest_match.group(1)
                    if 'related' in field_def:
                        related_match = re.search(r"related\s*=\s*['\"](.*?)['\"]", field_def)
                        if related_match:
                            field_info.related = related_match.group(1)
                    if 'compute' in field_def:
                        computed_match = re.search(r"compute\s*=\s*['\"](.*?)['\"]", field_def)
                        if computed_match:
                            field_info.computed = computed_match.group(1)
                    if 'default' in field_def:
                        field_info.default = "(has default)"
                    if 'ondelete' in field_def:
                        ondelete_match = re.search(r"ondelete\s*=\s*['\"](\w+)['\"]", field_def)
                        if ondelete_match:
                            field_info.ondelete = ondelete_match.group(1)

                model_info.fields.append(field_info)

            # Find methods with decorators (handle dotted decorators like @api.depends)
            method_pattern = r'@([\w\.]+)\s+def\s+(\w+)\(self.*?\):(.*?)(?=\n    def |\n\nclass |\Z)'
            for method_match in re.finditer(method_pattern, content, re.DOTALL):
                decorator = method_match.group(1)
                method_name = method_match.group(2)
                method_body = method_match.group(3)

                # Only capture business logic decorators
                business_decorators = ['api.model', 'api.depends', 'api.constrains', 'api.onchange',
                                       'api.one', 'api.multi', 'model.multi', 'model.method']
                if decorator in business_decorators:
                    method_info = MethodInfo(
                        name=method_name,
                        decorators=[decorator],
                        lines=len(method_body.split('\n'))
                    )
                    model_info.methods.append(method_info)

            if model_info.fields or model_info.methods:
                models.append(model_info)

    return models


def parse_views(module_path: Path) -> List[ViewInfo]:
    """Parse view XML files."""
    views = []
    views_dir = module_path / 'views'
    if not views_dir.exists():
        return views

    for xml_file in views_dir.glob('*.xml'):
        with open(xml_file, 'r') as f:
            content = f.read()

        # Find view definitions
        view_patterns = [
            (r'<record id="(.*?)".*?<field name="model">(.*?)</field>.*?<field name="arch".*?>(.*?)</field>',
             'form'),
            (r'<tree string="(.*?)".*?<field name="model">(.*?)</field>', 'tree'),
            (r'<search string="(.*?)".*?<field name="model">(.*?)</field>', 'search'),
            (r'<kanban.*?<field name="model">(.*?)</field>', 'kanban'),
        ]

        for pattern, view_type in view_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                view_name = match.group(1)
                model_name = match.group(2)

                view_info = ViewInfo(name=view_name, view_type=view_type)

                # Find custom fields (non-standard fields)
                # This is a simplified check - look for field definitions in views
                field_pattern = r'<field name="(\w+)"'
                for field_match in re.finditer(field_pattern, match.group(3)):
                    field_name = field_match.group(1)
                    # Common standard fields to skip
                    if field_name not in ['id', 'name', 'active', 'create_date', 'write_date',
                                          'create_uid', 'write_uid', 'display_name']:
                        view_info.custom_fields.append(field_name)

                views.append(view_info)

    return views


def parse_wizards(module_path: Path) -> List[WizardInfo]:
    """Parse wizard files."""
    wizards = []
    wizards_dir = module_path / 'wizards'
    if not wizards_dir.exists():
        return wizards

    # Parse wizard Python files
    for py_file in wizards_dir.glob('*.py'):
        if py_file.name.startswith('__'):
            continue
        with open(py_file, 'r') as f:
            content = f.read()

        class_pattern = r'class\s+(\w+)\(.*?TransientModel.*?\):'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            # Extract model name from _name
            name_pattern = r'_name\s*=\s*["\'](.*?)["\']'
            name_match = re.search(name_pattern, content)
            if name_match:
                wizard_info = WizardInfo(
                    model_name=name_match.group(1),
                    view_name=class_name.lower()
                )
                wizards.append(wizard_info)

    return wizards


def check_api_integration(module_path: Path) -> Tuple[bool, List[str]]:
    """Check for third-party API integrations."""
    api_endpoints = []
    has_integration = False
    all_content = ""

    # Check controllers
    controllers_dir = module_path / 'controllers'
    if controllers_dir.exists():
        for py_file in controllers_dir.glob('*.py'):
            with open(py_file, 'r') as f:
                content = f.read()
                all_content += content + "\n"
            # Look for HTTP routes
            routes = re.findall(r'@http.route\([\'"](.*?)[\'"]', content)
            api_endpoints.extend(routes)

    # Also check models for integration patterns
    models_dir = module_path / 'models'
    if models_dir.exists():
        for py_file in models_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
            with open(py_file, 'r') as f:
                all_content += f.read() + "\n"

    # Check for common integration patterns
    integration_patterns = [
        r'requests\.',
        r'httpx\.',
        r'urllib\.',
        r'jsonrpc',
        r'xmlrpc',
        r'odoo\.xmlrpc',
        r'workalendar',
        r'strip',
        r'paypal',
        r'stripe',
        r'twilio',
    ]

    for pattern in integration_patterns:
        if re.search(pattern, all_content, re.IGNORECASE):
            has_integration = True

    return has_integration, api_endpoints


def generate_questionnaire(analysis: ModuleAnalysis) -> str:
    """Generate business context questionnaire."""
    questionnaire = f"""# Business Context Questionnaire: {analysis.name}

## Module Overview
- **Module Name**: {analysis.name}
- **Path**: {analysis.path}

---

## Questions for Developer

### 1. Purpose
What is the main purpose of this module?

**Answer:** _______________________________________________

---

### 2. Critical Components

#### Custom Models ({len(analysis.models)} found)
"""

    for model in analysis.models:
        questionnaire += f"""
- **{model.name}** (inherits: `{model.inherits}`)

  Fields: {', '.join([f.name for f in model.fields[:5]])}{'...' if len(model.fields) > 5 else ''}
  Methods: {', '.join([m.name for m in model.methods[:5]])}{'...' if len(model.methods) > 5 else ''}

"""

    questionnaire += """
#### Critical Fields
Which fields are critical for business operations?

| Field | Reason |
|-------|--------|
| __________ | __________ |
| __________ | __________ |

---

### 3. Custom Business Logic

Methods with business logic decorators:

"""
    for model in analysis.models:
        if model.methods:
            questionnaire += f"**{model.name}**:\n"
            for method in model.methods:
                questionnaire += f"- `{method.name}` ({', '.join(method.decorators)}) - {method.lines} lines\n"
            questionnaire += "\n"

    questionnaire += """
Which methods contain important business logic that needs careful testing?

**Answer:** _______________________________________________

---

### 4. Integrations

"""
    if analysis.has_api_integration:
        questionnaire += f"""**Detected API Integrations**: Yes

API Endpoints:
"""
        for endpoint in analysis.api_endpoints:
            questionnaire += f"- {endpoint}\n"
    else:
        questionnaire += "**Detected API Integrations**: No (or not detected)\n"

    questionnaire += """
Does this module connect to third-party services?

| API/Service | Purpose | Notes |
|-------------|---------|-------|
| __________ | __________ | __________ |

---

### 5. Data Dependencies

Are there specific data that must be migrated?

| Data Type | Description | Migration Notes |
|-----------|-------------|-----------------|
| __________ | __________ | __________ |

---

### 6. Workflows

Are there custom workflows that need manual review after migration?

| Workflow | Current Behavior | Expected After Migration |
|----------|------------------|------------------------|
| __________ | __________ | __________ |

---

## Risk Assessment

Based on the analysis:

| Business Area | Detected | Risk Level | Notes |
|---------------|----------|------------|-------|
| Custom Models | """ + str(len(analysis.models)) + """ | MEDIUM | Review inheritance |
| Custom Fields | """ + str(sum(len(m.fields) for m in analysis.models)) + """ | MEDIUM | Verify field behavior |
| Business Methods | """ + str(sum(len(m.methods) for m in analysis.models)) + """ | HIGH | Manual testing required |
| API Integrations | """ + str(analysis.has_api_integration) + """ | HIGH | Verify after migration |
| Wizards | """ + str(len(analysis.wizards)) + """ | MEDIUM | Test wizard flows |

---

## Migration Checklist

- [ ] Review custom model inheritance
- [ ] Verify critical field behavior
- [ ] Test all business logic methods
- [ ] Verify API integrations
- [ ] Test wizard flows
- [ ] Review custom views

"""

    return questionnaire


def generate_risk_matrix(analysis: ModuleAnalysis) -> str:
    """Generate risk assessment matrix."""
    risk_items = []

    # Custom models
    if analysis.models:
        custom_models = [m for m in analysis.models if m.is_custom]
        if custom_models:
            risk_items.append({
                'area': 'Custom Models',
                'detected': len(custom_models),
                'risk': 'MEDIUM',
                'mitigation': 'Review model inheritance and dependencies'
            })

    # Custom fields
    total_fields = sum(len(m.fields) for m in analysis.models)
    if total_fields > 10:
        risk_items.append({
            'area': 'Custom Fields',
            'detected': total_fields,
            'risk': 'MEDIUM',
            'mitigation': 'Create field review checklist'
        })
    elif total_fields > 0:
        risk_items.append({
            'area': 'Custom Fields',
            'detected': total_fields,
            'risk': 'LOW',
            'mitigation': 'Standard field behavior'
        })

    # Business methods
    total_methods = sum(len(m.methods) for m in analysis.models)
    if total_methods > 5:
        risk_items.append({
            'area': 'Business Methods',
            'detected': total_methods,
            'risk': 'HIGH',
            'mitigation': 'Manual testing required for each method'
        })
    elif total_methods > 0:
        risk_items.append({
            'area': 'Business Methods',
            'detected': total_methods,
            'risk': 'MEDIUM',
            'mitigation': 'Review business logic after migration'
        })

    # API integrations
    if analysis.has_api_integration:
        risk_items.append({
            'area': 'API Integrations',
            'detected': 'Yes',
            'risk': 'HIGH',
            'mitigation': 'Verify integrations after migration'
        })

    # Wizards
    if analysis.wizards:
        risk_items.append({
            'area': 'Wizards',
            'detected': len(analysis.wizards),
            'risk': 'MEDIUM',
            'mitigation': 'Test wizard flows'
        })

    # Generate markdown table
    matrix = "# Risk Assessment Matrix\n\n"
    matrix += "| Business Area | Detected | Risk Level | Mitigation |\n"
    matrix += "|---------------|----------|------------|------------|\n"

    for item in risk_items:
        matrix += f"| {item['area']} | {item['detected']} | {item['risk']} | {item['mitigation']} |\n"

    return matrix


def analyze_module(module_path: str) -> ModuleAnalysis:
    """Analyze a single module."""
    path = Path(module_path)

    if not path.exists():
        raise ValueError(f"Module path does not exist: {module_path}")

    analysis = ModuleAnalysis(
        name=path.name,
        path=str(path)
    )

    # Parse manifest
    manifest = parse_manifest(path)
    analysis.name = manifest.get('name', path.name)

    # Parse models
    analysis.models = parse_models(path)

    # Parse views
    analysis.views = parse_views(path)

    # Parse wizards
    analysis.wizards = parse_wizards(path)

    # Check for API integration
    analysis.has_api_integration, analysis.api_endpoints = check_api_integration(path)

    return analysis


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_business_context.py <module_path>")
        print("Example: python3 analyze_business_context.py /path/to/custom_module")
        sys.exit(1)

    module_path = sys.argv[1]

    try:
        analysis = analyze_module(module_path)

        # Generate outputs
        questionnaire = generate_questionnaire(analysis)
        risk_matrix = generate_risk_matrix(analysis)

        # Output directory
        output_dir = Path(module_path)
        if output_dir.exists():
            # Write business_context.md
            output_file = output_dir / 'business_context.md'
            with open(output_file, 'w') as f:
                f.write(questionnaire)
                f.write("\n\n")
                f.write(risk_matrix)
            print(f"Generated: {output_file}")

        # Also print to stdout
        print("\n" + "="*60)
        print(f"BUSINESS CONTEXT ANALYSIS: {analysis.name}")
        print("="*60)
        print(f"\nModels found: {len(analysis.models)}")
        print(f"Views found: {len(analysis.views)}")
        print(f"Wizards found: {len(analysis.wizards)}")
        print(f"API Integration: {analysis.has_api_integration}")
        print("\n" + "="*60)
        print("See business_context.md for full questionnaire")
        print("="*60)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
