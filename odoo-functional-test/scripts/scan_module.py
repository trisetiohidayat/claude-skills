#!/usr/bin/env python3
"""
Odoo Module Scanner
Scans an Odoo module and generates module_scan.json with feature inventory.
Usage: python scan_module.py <module_path> [output_dir]
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

def extract_model_info(py_file_path: str) -> dict:
    """Extract model information from a Python model file."""
    model_info = {
        "model_name": "",
        "inherit": [],
        "fields": [],
        "methods": [],
        "states": [],
        "onchanges": [],
        "constraints": [],
        "defaults": {}
    }

    try:
        with open(py_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return model_info

    # Extract model name
    model_match = re.search(r'_name\s*=\s*["\']([^"\']+)["\']', content)
    if model_match:
        model_info["model_name"] = model_match.group(1)

    # Extract inherits
    inherits_matches = re.findall(r'_inherit\s*=\s*["\']([^"\']+)["\']', content)
    model_info["inherit"] = inherits_matches

    # Extract field definitions (simplified)
    field_pattern = re.compile(
        r'(\w+)\s*=\s*fields\.(?:'
        r'Char|Text|Integer|Float|Boolean|Date|Datetime|'
        r'Many2one|One2many|Many2many|Selection|Binary|HTML|'
        r'Monetary|Reference'
        r')',
        re.IGNORECASE
    )
    for match in field_pattern.finditer(content):
        field_name = match.group(1)
        field_type = match.group(2).lower()
        if not field_name.startswith('_') and field_name not in ['id', 'create_uid', 'write_uid', 'create_date', 'write_date']:
            model_info["fields"].append({
                "name": field_name,
                "type": field_type,
                "required": False,
                "readonly": False
            })

    # Extract selection fields for state
    selection_pattern = re.compile(
        r'(\w+)\s*=\s*fields\.Selection\s*\(\s*\[([^\]]+)\]',
        re.MULTILINE
    )
    for match in selection_pattern.finditer(content):
        field_name = match.group(1)
        options_str = match.group(2)
        if field_name in ['state', 'status']:
            options = re.findall(r'["\']([^"\']+)["\']', options_str)
            model_info["states"] = options

    # Extract onchange methods
    onchange_pattern = re.compile(r'@api\.onchange\s*\([\'"]?(\w+)[\'"]?\)', re.MULTILINE)
    model_info["onchanges"] = onchange_pattern.findall(content)

    # Extract constrains
    constrain_pattern = re.compile(r'@api\.constrains\s*\(([^)]+)\)', re.MULTILINE)
    for match in constrain_pattern.finditer(content):
        model_info["constraints"].append(match.group(1))

    # Extract method names (def functions)
    method_pattern = re.compile(r'\n    def (\w+)\s*\(', re.MULTILINE)
    model_info["methods"] = method_pattern.findall(content)

    return model_info


def extract_view_info(xml_file_path: str) -> list:
    """Extract view information from XML file."""
    views = []
    try:
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return views

    # Find all view tags
    view_patterns = [
        ('form', r'<form[^>]*name=["\']([^"\']+)["\'][^>]*>', '<form'),
        ('tree', r'<tree[^>]*name=["\']([^"\']+)["\'][^>]*>', '<tree'),
        ('kanban', r'<kanban[^>]*name=["\']([^"\']+)["\'][^>]*>', '<kanban'),
        ('pivot', r'<pivot[^>]*name=["\']([^"\']+)["\'][^>]*>', '<pivot'),
        ('graph', r'<graph[^>]*name=["\']([^"\']+)["\'][^>]*>', '<graph'),
        ('calendar', r'<calendar[^>]*name=["\']([^"\']+)["\'][^>]*>', '<calendar'),
        ('search', r'<search[^>]*name=["\']([^"\']+)["\'][^>]*>', '<search'),
    ]

    for view_type, name_pattern, _ in view_patterns:
        matches = re.finditer(name_pattern, content)
        for match in matches:
            view_name = match.group(1)
            # Find associated model
            model_match = re.search(r'model\s*=\s*["\']([^"\']+)["\']', match.group(0))
            model = model_match.group(1) if model_match else ""

            # Find buttons in this view
            buttons = []
            button_pattern = re.compile(r'<button[^>]*type=["\'](\w+)["\'][^>]*>', re.MULTILINE)
            for btn in button_pattern.finditer(content[match.start():match.end()+2000]):
                buttons.append(btn.group(1))

            # Find fields
            fields = re.findall(r'name=["\']([^"\']+)["\']', match.group(0))

            views.append({
                "view_type": view_type,
                "view_name": view_name,
                "model": model,
                "file": os.path.basename(xml_file_path),
                "buttons": list(set(buttons)),
                "fields": list(set(fields))[:10]  # Limit fields
            })

    return views


def extract_action_info(xml_file_path: str) -> list:
    """Extract action and menu information from XML."""
    actions = []
    menus = []

    try:
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return actions, menus

    # Act window actions
    act_pattern = re.compile(
        r'<act_window\s+([^>]+)/?>',
        re.MULTILINE | re.DOTALL
    )
    for match in act_pattern.finditer(content):
        attrs = match.group(1)
        action = {
            "name": re.search(r'name=["\']([^"\']+)["\']', attrs),
            "id": re.search(r'id=["\']([^"\']+)["\']', attrs),
            "model": re.search(r'res_model=["\']([^"\']+)["\']', attrs),
            "view_mode": re.search(r'view_mode=["\']([^"\']+)["\']', attrs),
            "xmlid": os.path.basename(xml_file_path).replace('.xml', '') + '.' + (
                re.search(r'id=["\']([^"\']+)["\']', attrs).group(1)
                if re.search(r'id=["\']([^"\']+)["\']', attrs) else 'unknown'
            )
        }
        if action["name"]:
            actions.append({
                "name": action["name"].group(1),
                "id": action["id"].group(1) if action["id"] else "",
                "model": action["model"].group(1) if action["model"] else "",
                "view_mode": action["view_mode"].group(1) if action["view_mode"] else "",
                "xmlid": action["xmlid"]
            })

    # Menu items
    menu_pattern = re.compile(
        r'<menuitem\s+([^>]+)/?>',
        re.MULTILINE
    )
    for match in menu_pattern.finditer(content):
        attrs = match.group(1)
        menu = {
            "name": re.search(r'name=["\']([^"\']+)["\']', attrs),
            "id": re.search(r'id=["\']([^"\']+)["\']', attrs),
            "parent": re.search(r'parent=["\']([^"\']+)["\']', attrs),
            "action": re.search(r'action=["\']([^"\']+)["\']', attrs),
            "xmlid": os.path.basename(xml_file_path).replace('.xml', '') + '.' + (
                re.search(r'id=["\']([^"\']+)["\']', attrs).group(1)
                if re.search(r'id=["\']([^"\']+)["\']', attrs) else 'unknown'
            )
        }
        if menu["name"]:
            menus.append({
                "name": menu["name"].group(1),
                "id": menu["id"].group(1) if menu["id"] else "",
                "parent": menu["parent"].group(1) if menu["parent"] else "",
                "action": menu["action"].group(1) if menu["action"] else "",
                "xmlid": menu["xmlid"]
            })

    return actions, menus


def extract_wizard_info(wizard_path: str) -> list:
    """Extract wizard (transient model) information."""
    wizards = []
    py_files = list(Path(wizard_path).glob("*.py")) if os.path.isdir(wizard_path) else []

    for py_file in py_files:
        info = extract_model_info(str(py_file))
        if info["model_name"]:
            wizards.append({
                "model_name": info["model_name"],
                "file": py_file.name,
                "fields": [f for f in info["fields"] if f["name"] not in ["id", "create_uid", "write_uid"]],
                "methods": [m for m in info["methods"] if not m.startswith('_')]
            })

    # Wizard views
    if os.path.isdir(wizard_path):
        xml_files = list(Path(wizard_path).glob("*.xml"))
        for xml_file in xml_files:
            views = extract_view_info(str(xml_file))
            if views:
                for v in views:
                    for w in wizards:
                        if v["model"].replace('.', '_') in w["model_name"] or w["model_name"].replace('.', '_') in v["model"]:
                            w["views"] = w.get("views", []) + [v["view_name"]]

    return wizards


def extract_security_info(security_path: str) -> list:
    """Extract access control list from ir.model.access.csv."""
    acls = []
    csv_file = os.path.join(security_path, 'ir.model.access.csv')
    if os.path.isfile(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:  # Skip header
                parts = line.strip().split(',')
                if len(parts) >= 6:
                    acls.append({
                        "id": parts[0],
                        "model": parts[1],
                        "name": parts[2],
                        "perm_read": parts[3] == '1',
                        "perm_write": parts[4] == '1',
                        "perm_create": parts[5] == '1',
                        "perm_unlink": parts[6] == '1' if len(parts) > 6 else False
                    })
    return acls


def infer_features(models: list, views: list, wizards: list) -> list:
    """Infer testable features from models, views, and wizards."""
    features = []

    # Core CRUD for each model
    for model in models:
        model_name = model["model_name"]
        short_name = model_name.split('.')[-1]

        # Create
        features.append({
            "id": f"FEAT-{short_name}-CREATE",
            "feature": f"Create new {short_name}",
            "model": model_name,
            "view": "form",
            "priority": 1,
            "category": "create"
        })

        # Read (navigate)
        features.append({
            "id": f"FEAT-{short_name}-READ",
            "feature": f"View existing {short_name} record",
            "model": model_name,
            "view": "form",
            "priority": 1,
            "category": "read"
        })

        # Edit
        features.append({
            "id": f"FEAT-{short_name}-EDIT",
            "feature": f"Edit existing {short_name}",
            "model": model_name,
            "view": "form",
            "priority": 1,
            "category": "edit"
        })

        # Delete
        features.append({
            "id": f"FEAT-{short_name}-DELETE",
            "feature": f"Delete {short_name} record",
            "model": model_name,
            "view": "form",
            "priority": 1,
            "category": "delete"
        })

        # State transitions
        if model["states"]:
            for state in model["states"]:
                features.append({
                    "id": f"FEAT-{short_name}-STATE-{state.upper()}",
                    "feature": f"Change state to {state}",
                    "model": model_name,
                    "action": state,
                    "priority": 1,
                    "category": "workflow"
                })

        # Onchanges
        for onchange in model.get("onchanges", []):
            features.append({
                "id": f"FEAT-{short_name}-ONCHANGE-{onchange.upper()}",
                "feature": f"Trigger onchange: {onchange}",
                "model": model_name,
                "action": f"onchange_{onchange}",
                "priority": 2,
                "category": "onchange"
            })

    # View-specific features
    for view in views:
        if view["view_type"] == "kanban":
            features.append({
                "id": f"FEAT-{view['model'].split('.')[-1]}-KANBAN",
                "feature": f"Kanban view: {view['view_name']}",
                "model": view["model"],
                "view": "kanban",
                "priority": 2,
                "category": "view"
            })
        elif view["view_type"] == "pivot":
            features.append({
                "id": f"FEAT-{view['model'].split('.')[-1]}-PIVOT",
                "feature": f"Pivot view: {view['view_name']}",
                "model": view["model"],
                "view": "pivot",
                "priority": 3,
                "category": "view"
            })
        elif view["view_type"] == "graph":
            features.append({
                "id": f"FEAT-{view['model'].split('.')[-1]}-GRAPH",
                "feature": f"Graph view: {view['view_name']}",
                "model": view["model"],
                "view": "graph",
                "priority": 3,
                "category": "view"
            })
        elif view["view_type"] == "calendar":
            features.append({
                "id": f"FEAT-{view['model'].split('.')[-1]}-CALENDAR",
                "feature": f"Calendar view: {view['view_name']}",
                "model": view["model"],
                "view": "calendar",
                "priority": 3,
                "category": "view"
            })

    # Search features
    for view in views:
        if view["view_type"] in ["tree", "kanban"]:
            features.append({
                "id": f"FEAT-{view['model'].split('.')[-1]}-SEARCH",
                "feature": f"Search and filter {view['model'].split('.')[-1]}",
                "model": view["model"],
                "view": "search",
                "priority": 2,
                "category": "search"
            })

    # Wizard features
    for wizard in wizards:
        features.append({
            "id": f"FEAT-WIZARD-{wizard['model_name'].split('.')[-1]}",
            "feature": f"Wizard: {wizard['model_name'].split('.')[-1]}",
            "model": wizard["model_name"],
            "view": "wizard",
            "priority": 2,
            "category": "wizard"
        })

    return features


def scan_module(module_path: str, output_dir: str = ".") -> dict:
    """Full module scan."""
    module_name = os.path.basename(module_path.rstrip('/'))

    result = {
        "module_name": module_name,
        "module_path": module_path,
        "scanned_at": datetime.now().isoformat() + "Z",
        "odoo_version": "19",  # Default assumption
        "models": [],
        "views": [],
        "actions": [],
        "menus": [],
        "wizards": [],
        "access_controls": [],
        "features": []
    }

    # Scan models
    models_dir = os.path.join(module_path, 'models')
    if os.path.isdir(models_dir):
        for py_file in Path(models_dir).glob("*.py"):
            info = extract_model_info(str(py_file))
            if info["model_name"]:
                info["file"] = py_file.name
                result["models"].append(info)

    # Scan views
    views_dir = os.path.join(module_path, 'views')
    if os.path.isdir(views_dir):
        for xml_file in Path(views_dir).glob("*.xml"):
            views = extract_view_info(str(xml_file))
            result["views"].extend(views)
            actions, menus = extract_action_info(str(xml_file))
            result["actions"].extend(actions)
            result["menus"].extend(menus)

    # Scan wizards
    wizards_dir = os.path.join(module_path, 'wizards')
    if os.path.isdir(wizards_dir):
        result["wizards"] = extract_wizard_info(wizards_dir)

    # Scan security
    security_dir = os.path.join(module_path, 'security')
    if os.path.isdir(security_dir):
        result["access_controls"] = extract_security_info(security_dir)

    # Infer features
    result["features"] = infer_features(result["models"], result["views"], result["wizards"])

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_module.py <module_path> [output_dir]")
        sys.exit(1)

    module_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if not os.path.isdir(module_path):
        print(f"Error: {module_path} is not a valid directory")
        sys.exit(1)

    print(f"Scanning module: {module_path}")
    result = scan_module(module_path, output_dir)

    output_file = os.path.join(output_dir, 'module_scan.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Scan complete. Results saved to: {output_file}")
    print(f"  Models: {len(result['models'])}")
    print(f"  Views: {len(result['views'])}")
    print(f"  Actions: {len(result['actions'])}")
    print(f"  Menus: {len(result['menus'])}")
    print(f"  Wizards: {len(result['wizards'])}")
    print(f"  Features: {len(result['features'])}")

    return result


if __name__ == "__main__":
    main()
