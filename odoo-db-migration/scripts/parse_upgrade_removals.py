#!/usr/bin/env python3
"""
Parse upgrade.log untuk mendeteksi model yang dihapus/berubah.

Usage:
    python3 parse_upgrade_removals.py /path/to/upgrade.log [--output results.json]
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class RemovedModel:
    model_name: str
    table_name: str | None
    action: str  # removed, renamed, deprecated
    new_model: str | None = None
    reason: str | None = None
    line_number: int = 0


def parse_upgrade_log(log_path: str) -> List[RemovedModel]:
    """Parse upgrade.log untuk model removals."""
    results = []

    with open(log_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # Pattern: remove_model('model.name')
            match = re.search(r"remove_model\(['\"]([\w.]+)['\"]", line)
            if match:
                model_name = match.group(1)
                # Extract table name if present
                table_match = re.search(r"dropping (?:m2m )?table ['\"]?(\w+)['\"]?", line)
                table_name = table_match.group(1) if table_match else None

                results.append(RemovedModel(
                    model_name=model_name,
                    table_name=table_name,
                    action='removed',
                    line_number=line_num
                ))

            # Pattern: rename_model('old', 'new')
            match = re.search(r"rename_model\(['\"]([\w.]+)['\"],\s*['\"]([\w.]+)['\"]", line)
            if match:
                old_model = match.group(1)
                new_model = match.group(2)
                results.append(RemovedModel(
                    model_name=old_model,
                    table_name=None,
                    action='renamed',
                    new_model=new_model,
                    line_number=line_num
                ))

            # Pattern: deprecat* model
            if 'deprecat' in line.lower():
                match = re.search(r"(['\"]?[\w.]+['\"]?)\s+(?:is|was)\s+deprecat", line, re.IGNORECASE)
                if match:
                    model_name = match.group(1).strip("'\"")
                    if '.' in model_name:  # Only full model names
                        results.append(RemovedModel(
                            model_name=model_name,
                            table_name=None,
                            action='deprecated',
                            line_number=line_num
                        ))

    return results


def parse_module_dependencies(modules_path: str) -> dict:
    """Parse custom modules untuk dependencies."""
    deps = {}
    modules_dir = Path(modules_path)

    if not modules_dir.exists():
        return deps

    for manifest in modules_dir.glob('*/__manifest__.py'):
        module_name = manifest.parent.name
        try:
            content = manifest.read_text()
            # Simple regex untuk depends
            depends_match = re.search(r"'depends'\s*:\s*\[(.*?)\]", content, re.DOTALL)
            if depends_match:
                depends = re.findall(r"'(\w+)'", depends_match.group(1))
                deps[module_name] = depends
        except Exception:
            pass

    return deps


def find_affected_modules(removed_models: List[RemovedModel], module_deps: dict) -> dict:
    """Find modules yang depend ke removed models."""
    affected = {}

    for module, deps in module_deps.items():
        module_affected_by = []
        for removed in removed_models:
            model_short = removed.model_name.split('.')[-1]
            if model_short in deps or removed.model_name in deps:
                module_affected_by.append(removed.model_name)

        if module_affected_by:
            affected[module] = module_affected_by

    return affected


def check_model_inheritance(module_path: str, removed_models: List[RemovedModel]) -> dict:
    """
    Check Python files untuk _inherit dan _inherits.
    Returns dict of {model_name: [module_names]}
    """
    module_path = Path(module_path)
    inheritance_map = {}  # {model_name: [file_path]}

    if not module_path.exists():
        return {}

    # Get all Python files in the module
    for py_file in module_path.glob('**/*.py'):
        try:
            content = py_file.read_text()

            # Check _inherit
            inherit_match = re.search(r"_inherit\s*=\s*['\"]([\w.]+)['\"]", content)
            if inherit_match:
                parent_model = inherit_match.group(1)
                for removed in removed_models:
                    if parent_model == removed.model_name:
                        key = removed.model_name
                        if key not in inheritance_map:
                            inheritance_map[key] = []
                        inheritance_map[key].append(str(py_file))

            # Check _inherits (dict format)
            inherits_match = re.search(r"_inherits\s*=\s*\{([^}]+)\}", content)
            if inherits_match:
                inherits_content = inherits_match.group(1)
                parent_matches = re.findall(r"['\"]?([\w.]+)['\"]?\s*:", inherits_content)
                for parent_model in parent_matches:
                    for removed in removed_models:
                        if parent_model == removed.model_name:
                            key = removed.model_name
                            if key not in inheritance_map:
                                inheritance_map[key] = []
                            inheritance_map[key].append(str(py_file))
        except Exception:
            pass

    return inheritance_map


def check_xml_model_references(module_path: str, removed_models: List[RemovedModel]) -> dict:
    """Check XML files untuk model= attributes."""
    module_path = Path(module_path)
    xml_refs = {}

    if not module_path.exists():
        return {}

    for xml_file in module_path.glob('**/*.xml'):
        try:
            content = xml_file.read_text()
            for removed in removed_models:
                # Check model="..." in XML
                if f'model="{removed.model_name}"' in content or f"model=\"{removed.model_name}\"" in content:
                    if removed.model_name not in xml_refs:
                        xml_refs[removed.model_name] = []
                    xml_refs[removed.model_name].append(str(xml_file))
        except Exception:
            pass

    return xml_refs


def main():
    parser = argparse.ArgumentParser(description='Parse upgrade.log untuk model removals')
    parser.add_argument('log_path', help='Path ke upgrade.log')
    parser.add_argument('--modules', help='Path ke custom modules untuk check dependencies')
    parser.add_argument('--output', '-o', help='Output JSON file')

    args = parser.parse_args()

    # Parse
    removed_models = parse_upgrade_log(args.log_path)
    print(f"Found {len(removed_models)} removed/renamed models")

    # Find affected modules
    affected_modules = {}
    inheritance_issues = {}
    xml_references = {}

    if args.modules:
        # Check manifest dependencies
        module_deps = parse_module_dependencies(args.modules)
        affected_modules = find_affected_modules(removed_models, module_deps)
        print(f"Affected modules (manifest depends): {list(affected_modules.keys())}")

        # Check _inherit in Python files
        modules_path = Path(args.modules)
        for module_dir in modules_path.iterdir():
            if module_dir.is_dir():
                inheritance = check_model_inheritance(str(module_dir), removed_models)
                if inheritance:
                    for model, files in inheritance.items():
                        if model not in inheritance_issues:
                            inheritance_issues[model] = []
                        inheritance_issues[model].extend(files)

        # Check XML model references
        for module_dir in modules_path.iterdir():
            if module_dir.is_dir():
                xml_refs = check_xml_model_references(str(module_dir), removed_models)
                if xml_refs:
                    for model, files in xml_refs.items():
                        if model not in xml_references:
                            xml_references[model] = []
                        xml_references[model].extend(files)

    # Output
    result = {
        'removed_models': [asdict(m) for m in removed_models],
        'affected_modules': affected_modules,
        'inheritance_issues': inheritance_issues,
        'xml_references': xml_references
    }

    # Print summary
    if inheritance_issues:
        print(f"\n⚠️  Found {len(inheritance_issues)} models with inheritance issues:")
        for model, files in inheritance_issues.items():
            print(f"   - {model}: {len(files)} file(s)")

    if xml_references:
        print(f"\n⚠️  Found {len(xml_references)} models with XML references:")
        for model, files in xml_references.items():
            print(f"   - {model}: {len(files)} file(s)")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
