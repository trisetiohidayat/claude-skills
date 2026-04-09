#!/usr/bin/env python3
"""
Classifies modules as custom/standard/overridden based on paths.
"""
import os
import sys
import json
import ast
from pathlib import Path


def safe_parse_manifest(path):
    """Parse __manifest__.py safely using ast.literal_eval."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the dictionary assignment
        # Manifest can be: {'key': 'value'} or manifest = {'key': 'value'}
        manifest_dict = {}

        if '=' in content:
            # Has variable assignment like: manifest = {...}
            for line in content.split('\n'):
                if '=' in line and '{' in line:
                    # Extract dict content after =
                    dict_str = line.split('=', 1)[1].strip()
                    break
            else:
                dict_str = content
        else:
            dict_str = content

        # Use ast.literal_eval for safe parsing
        manifest = ast.literal_eval(dict_str.strip())
        return manifest

    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return {}


def find_module_path(module_name, search_paths):
    """Find where a module exists in the given paths."""
    for base_path in search_paths:
        module_path = os.path.join(base_path, module_name)
        if os.path.isdir(module_path):
            manifest_path = os.path.join(module_path, '__manifest__.py')
            openerp_path = os.path.join(module_path, '__openerp__.py')

            if os.path.exists(manifest_path):
                return base_path, manifest_path, 'manifest'
            elif os.path.exists(openerp_path):
                return base_path, openerp_path, 'openerp'

    return None, None, None


def classify_module(module_name, custom_paths, ce_path, ee_path):
    """Classify a module as custom/standard/overridden/external."""
    all_paths = custom_paths.copy()
    if ce_path:
        all_paths.append(ce_path)
    if ee_path:
        all_paths.append(ee_path)

    base_path, manifest_path, manifest_type = find_module_path(module_name, all_paths)

    if base_path is None:
        return 'external', None, None

    # Check where it exists
    in_custom = any(os.path.exists(os.path.join(p, module_name)) for p in custom_paths)
    in_ce = ce_path and os.path.exists(os.path.join(ce_path, module_name))
    in_ee = ee_path and os.path.exists(os.path.join(ee_path, module_name))

    if in_custom and not in_ce and not in_ee:
        return 'custom', base_path, manifest_path
    elif in_custom and (in_ce or in_ee):
        return 'overridden', base_path, manifest_path
    elif in_ce or in_ee:
        return 'standard', base_path, manifest_path
    else:
        return 'external', base_path, manifest_path


def get_module_info(manifest_path):
    """Get module info from manifest."""
    if not manifest_path or not os.path.exists(manifest_path):
        return {}

    manifest = safe_parse_manifest(manifest_path)

    return {
        'name': manifest.get('name', ''),
        'version': manifest.get('version', ''),
        'description': manifest.get('description', ''),
        'author': manifest.get('author', ''),
        'depends': manifest.get('depends', []),
        'category': manifest.get('category', ''),
    }


def classify_all_modules(installed_modules, custom_paths, ce_path, ee_path):
    """Classify all installed modules."""
    results = {
        'custom': [],
        'standard': [],
        'overridden': [],
        'external': [],
        'not_found': []
    }

    for module in installed_modules:
        module_name = module['name']

        classification, base_path, manifest_path = classify_module(
            module_name, custom_paths, ce_path, ee_path
        )

        module_info = get_module_info(manifest_path) if manifest_path else {}

        result = {
            'name': module_name,
            'state': module.get('state', 'unknown'),
            'version': module.get('version', ''),
            'depends': module.get('depends', []),
            'location': base_path,
            'manifest': manifest_path,
            'manifest_info': module_info
        }

        if classification == 'not_found':
            results['not_found'].append(result)
        else:
            results[classification].append(result)

    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python module_classifier.py <modules_json> <custom_path> [ce_path] [ee_path]")
        print("")
        print("Example:")
        print("  python module_classifier.py modules.json /path/to/custom /path/to/odoo/addons")
        sys.exit(1)

    modules_json = sys.argv[1]
    custom_path = sys.argv[2]
    ce_path = sys.argv[3] if len(sys.argv) > 3 else None
    ee_path = sys.argv[4] if len(sys.argv) > 4 else None

    # Load modules from JSON (created by db_connect.py)
    with open(modules_json, 'r') as f:
        data = json.load(f)

    installed = data.get('modules', [])

    # Build custom paths list
    custom_paths = [custom_path]
    if os.path.isdir(custom_path):
        # Also check subdirectories
        for item in os.listdir(custom_path):
            item_path = os.path.join(custom_path, item)
            if os.path.isdir(item_path):
                custom_paths.append(item_path)

    print(f"Classifying {len(installed)} installed modules...")
    print(f"Custom path: {custom_path}")
    print(f"CE path: {ce_path}")
    print(f"EE path: {ee_path}")

    results = classify_all_modules(installed, custom_paths, ce_path, ee_path)

    print("\n=== Classification Results ===")
    print(f"Custom modules: {len(results['custom'])}")
    print(f"Overridden modules: {len(results['overridden'])}")
    print(f"Standard modules: {len(results['standard'])}")
    print(f"External modules: {len(results['external'])}")
    print(f"Not found in filesystem: {len(results['not_found'])}")

    # Save results
    output_path = modules_json.replace('.json', '_classified.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Show custom modules
    if results['custom']:
        print("\n=== Custom Modules ===")
        for m in results['custom']:
            deps = m.get('depends', [])
            deps_str = f" (depends: {', '.join(deps)})" if deps else ""
            print(f"  - {m['name']}{deps_str}")

    # Show overridden modules
    if results['overridden']:
        print("\n=== Overridden Modules ===")
        for m in results['overridden']:
            print(f"  - {m['name']} (at {m.get('location')})")


if __name__ == '__main__':
    main()
