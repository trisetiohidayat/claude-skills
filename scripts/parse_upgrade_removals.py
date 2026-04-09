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
    if args.modules:
        module_deps = parse_module_dependencies(args.modules)
        affected_modules = find_affected_modules(removed_models, module_deps)
        print(f"Affected modules: {list(affected_modules.keys())}")

    # Output
    result = {
        'removed_models': [asdict(m) for m in removed_models],
        'affected_modules': affected_modules
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
