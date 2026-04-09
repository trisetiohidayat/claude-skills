#!/usr/bin/env python3
"""
Generate migration plan for a single module based on knowledge base.
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


def analyze_python_file(file_path: Path, breaking_changes: List[Dict]) -> List[Dict]:
    """Analyze Python file for modifications needed."""
    modifications = []

    if not file_path.exists():
        return modifications

    content = file_path.read_text()
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue

        # Check each breaking change pattern
        for change in breaking_changes:
            item = change.get("item", "")
            if not item:
                continue

            # Only process string-based changes
            if item in line:
                # Determine new code
                replacement = change.get("replacement", "")

                modifications.append({
                    "file": str(file_path),
                    "line": i,
                    "type": change.get("type", "unknown"),
                    "old_code": line.strip(),
                    "new_code": line.replace(item, replacement),
                    "reason": change.get("description", "")
                })

    return modifications


def analyze_xml_file(file_path: Path, breaking_changes: List[Dict]) -> List[Dict]:
    """Analyze XML file for modifications needed."""
    modifications = []

    if not file_path.exists():
        return modifications

    content = file_path.read_text()
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('<!--'):
            continue

        # Check for model name changes in XML
        for change in breaking_changes:
            if change.get("type") == "model_rename":
                old_model = change.get("old_model", "")
                new_model = change.get("new_model", "")

                if old_model and old_model in line:
                    modifications.append({
                        "file": str(file_path),
                        "line": i,
                        "type": "model_rename",
                        "old_code": line.strip(),
                        "new_code": line.replace(old_model, new_model),
                        "reason": change.get("note", "Model renamed")
                    })

    return modifications


def get_module_dependencies(module_path: Path) -> Dict[str, List[str]]:
    """Extract dependencies from module manifest."""
    manifest_file = module_path / "__manifest__.py"
    if not manifest_file.exists():
        manifest_file = module_path / "__openerp__.py"

    if not manifest_file.exists():
        return {"custom": [], "ce": [], "ee": []}

    content = manifest_file.read_text()

    # Extract depends
    all_deps = re.findall(r"'(\w+)'", content)

    # Default CE/EE lists
    ce_modules = [
        'base', 'web', 'sale', 'sale_management', 'account', 'account_accountant',
        'purchase', 'purchase_requisition', 'stock', 'stock_account', 'mrp',
        'mrp_repair', 'project', 'project_timesheet', 'hr', 'hr_expense',
        'crm', 'marketing_automation', 'website', 'website_blog', 'website_sale',
        'pos', 'account_payment', 'account_invoicing', 'hr_recruitment',
        'fleet', 'maintenance', 'quality', 'repair', 'event', 'mass_mailing'
    ]

    ee_modules = [
        'account_enterprise', 'sale_enterprise', 'purchase_enterprise',
        'stock_enterprise', 'project_enterprise', 'hr_enterprise'
    ]

    # Categorize
    custom = [d for d in all_deps if d not in ce_modules and d not in ee_modules]
    ce = [d for d in all_deps if d in ce_modules]
    ee = [d for d in all_deps if d in ee_modules]

    return {"custom": custom, "ce": ce, "ee": ee}


def generate_migration_plan(
    module_path: str,
    knowledge_base_path: str,
    output_path: str = None
) -> Dict[str, Any]:
    """Generate migration plan for a module."""

    module_path = Path(module_path)
    kb_path = Path(knowledge_base_path)

    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base not found: {knowledge_base_path}")

    kb = json.loads(kb_path.read_text())

    all_files = []
    modifications = []

    breaking_changes = kb.get("breaking_changes", [])
    model_replacements = kb.get("model_replacements", {})

    # Analyze models/
    models_dir = module_path / "models"
    if models_dir.exists():
        for py_file in models_dir.glob("*.py"):
            all_files.append(str(py_file))
            mods = analyze_python_file(py_file, breaking_changes)
            modifications.extend(mods)

            # Also check for model name references
            content = py_file.read_text()
            for old_model, replacement_info in model_replacements.items():
                new_model = replacement_info.get("new", "")
                if old_model in content and old_model != new_model:
                    # Found model reference - add as modification
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if f"'{old_model}'" in line or f'"{old_model}"' in line:
                            modifications.append({
                                "file": str(py_file),
                                "line": i,
                                "type": "model_reference",
                                "old_code": line.strip(),
                                "new_code": line.replace(old_model, new_model),
                                "reason": replacement_info.get("note", "Model replaced")
                            })

    # Analyze views/
    views_dir = module_path / "views"
    if views_dir.exists():
        for xml_file in views_dir.glob("*.xml"):
            all_files.append(str(xml_file))
            mods = analyze_xml_file(xml_file, breaking_changes)
            modifications.extend(mods)

    # Analyze wizards/
    wizards_dir = module_path / "wizards"
    if wizards_dir.exists():
        for py_file in wizards_dir.glob("*.py"):
            all_files.append(str(py_file))
            mods = analyze_python_file(py_file, breaking_changes)
            modifications.extend(mods)

        for xml_file in wizards_dir.glob("*.xml"):
            all_files.append(str(xml_file))
            mods = analyze_xml_file(xml_file, breaking_changes)
            modifications.extend(mods)

    # Analyze controllers/
    controllers_dir = module_path / "controllers"
    if controllers_dir.exists():
        for py_file in controllers_dir.glob("*.py"):
            all_files.append(str(py_file))
            mods = analyze_python_file(py_file, breaking_changes)
            modifications.extend(mods)

    # Analyze security/
    security_dir = module_path / "security"
    if security_dir.exists():
        for xml_file in security_dir.glob("*.xml"):
            all_files.append(str(xml_file))
            mods = analyze_xml_file(xml_file, breaking_changes)
            modifications.extend(mods)

    # Get dependencies
    dependencies = get_module_dependencies(module_path)

    # Determine status
    if modifications:
        status = "ready"
    else:
        status = "no_changes_needed"

    plan = {
        "module_name": module_path.name,
        "files_analyzed": all_files,
        "modifications": modifications,
        "dependencies": dependencies,
        "status": status
    }

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(plan, f, indent=2)
        print(f"Migration plan saved to: {output_path}")

    return plan


def main():
    parser = argparse.ArgumentParser(
        description="Generate migration plan for a single module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_migration_plan.py /path/to/module knowledge_base.json --output plan.json
  python generate_migration_plan.py ./my_module ../kb.json -o plan.json
        """
    )
    parser.add_argument("module_path", help="Path to module directory")
    parser.add_argument("knowledge_base", help="Path to knowledge base JSON")
    parser.add_argument("--output", "-o", help="Output JSON path")

    args = parser.parse_args()

    plan = generate_migration_plan(args.module_path, args.knowledge_base, args.output)
    print(f"Module: {plan['module_name']}")
    print(f"Files analyzed: {len(plan['files_analyzed'])}")
    print(f"Modifications needed: {len(plan['modifications'])}")
    print(f"Status: {plan['status']}")


if __name__ == "__main__":
    main()
