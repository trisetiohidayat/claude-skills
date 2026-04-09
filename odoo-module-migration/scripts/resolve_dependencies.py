#!/usr/bin/env python3
"""
Resolve module dependencies and determine migration order.
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict


def parse_manifest(module_path: Path) -> Dict:
    """Parse module __manifest__.py to get dependencies."""
    manifest_file = module_path / "__manifest__.py"
    if not manifest_file.exists():
        manifest_file = module_path / "__openerp__.py"

    if not manifest_file.exists():
        return {"name": module_path.name, "depends": []}

    # Read manifest
    content = manifest_file.read_text()

    # Extract dependencies
    depends = []
    if "'depends'" in content:
        # Simple parsing - find depends list
        match = re.search(r"'depends'\s*:\s*\[(.*?)\]", content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            # Extract quoted strings
            deps = re.findall(r"'(\w+)'", deps_str)
            depends = deps

    return {"name": module_path.name, "depends": depends}


def build_dependency_graph(modules_path: Path) -> Dict[str, List[str]]:
    """Build dependency graph for all modules."""
    graph = {}

    for module_dir in modules_path.iterdir():
        if not module_dir.is_dir():
            continue
        if module_dir.name.startswith('.') or module_dir.name == '__pycache__':
            continue

        manifest = parse_manifest(module_dir)
        graph[manifest["name"]] = manifest.get("depends", [])

    return graph


def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """Sort modules by dependencies (modules with no deps first) using Kahn's algorithm."""
    # Calculate in-degree
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for dep in graph[node]:
            if dep in in_degree:
                in_degree[node] += 1

    # Kahn's algorithm
    queue = [node for node in graph if in_degree[node] == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)

        # Find nodes that depend on this node
        for other in graph:
            if node in graph[other]:
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)

    if len(result) != len(graph):
        # Find circular dependencies
        circular = [node for node in graph if in_degree[node] > 0]
        raise ValueError(f"Circular dependency detected: {circular}")

    return result


def categorize_dependencies(
    module_name: str,
    all_depends: List[str],
    ce_modules: List[str],
    ee_modules: List[str]
) -> Dict[str, List[str]]:
    """Categorize dependencies into custom, CE, and EE."""
    custom = []
    ce = []
    ee = []

    for dep in all_depends:
        if dep in ee_modules:
            ee.append(dep)
        elif dep in ce_modules:
            ce.append(dep)
        else:
            # Assume custom if not in known CE/EE lists
            custom.append(dep)

    return {"custom": custom, "ce": ce, "ee": ee}


def resolve_dependencies(
    modules_path: str,
    output_path: str = None,
    ce_modules: List[str] = None,
    ee_modules: List[str] = None
) -> Dict:
    """Main function to resolve dependencies."""
    modules_path = Path(modules_path)

    if not modules_path.exists():
        raise FileNotFoundError(f"Modules path not found: {modules_path}")

    # Default CE/EE modules
    if ce_modules is None:
        ce_modules = [
            'base', 'web', 'sale', 'sale_management', 'account', 'account_accountant',
            'purchase', 'purchase_requisition', 'stock', 'stock_account', 'mrp',
            'mrp_repair', 'project', 'project_timesheet', 'hr', 'hr_expense',
            'crm', 'marketing_automation', 'website', 'website_blog', 'website_sale',
            'pos', 'account_payment', 'account_invoicing', 'hr_recruitment',
            'fleet', 'maintenance', 'quality', 'repair', 'event', 'mass_mailing'
        ]

    if ee_modules is None:
        ee_modules = [
            'account_enterprise', 'sale_enterprise', 'purchase_enterprise',
            'stock_enterprise', 'project_enterprise', 'hr_enterprise',
            'account_accountant', 'account_accountant_enterprise'
        ]

    graph = build_dependency_graph(modules_path)

    try:
        migration_order = topological_sort(graph)
    except ValueError as e:
        return {
            "modules": list(graph.keys()),
            "dependency_graph": graph,
            "migration_order": [],
            "error": str(e)
        }

    # Categorize dependencies for each module
    module_deps = {}
    for module in graph:
        deps = graph.get(module, [])
        module_deps[module] = categorize_dependencies(module, deps, ce_modules, ee_modules)

    result = {
        "modules": list(graph.keys()),
        "dependency_graph": graph,
        "migration_order": migration_order,
        "module_dependencies": module_deps
    }

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Dependency resolution saved to: {output_path}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Resolve module dependencies for Odoo migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python resolve_dependencies.py /path/to/custom_modules --output deps.json
  python resolve_dependencies.py ./my_modules --output deps.json
        """
    )
    parser.add_argument("modules_path", help="Path to custom modules directory")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    result = resolve_dependencies(args.modules_path, args.output)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Migration order: {' -> '.join(result['migration_order'])}")


if __name__ == "__main__":
    main()
