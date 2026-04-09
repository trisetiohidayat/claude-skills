---
name: odoo-module
description: Create new Odoo module with correct structure - Odoo 17/18/19 compatible. Use when user asks to "create module", "new addon", "add new module", or "initialize module"
---

# Odoo Module Creation Guide

You are helping the user create a new Odoo module with correct structure and best practices.

## Steps

1. **Parse module name** from user input:
   - Extract module technical name (e.g., "custom_feature", "module_name")
   - Parse optional flags: --category, --depends, --application, --version

2. **Ask for missing required information**:
   - Module name (if not provided)
   - Category: Sales, Purchase, Accounting, Inventory, Base, Other
   - Dependencies: comma-separated list (default: base)
   - Is it an application? (default: No)
   - Odoo version (default: from project CLAUDE.md or Odoo 17)

3. **Verify module doesn't exist**:
   - Check if module folder already exists in addons path
   - If exists, ask to confirm overwrite or choose different name

4. **Create module structure** in project addons directory:
   ```
   {module_name}/
   ├── __init__.py
   ├── __manifest__.py
   ├── models/
   │   ├── __init__.py
   │   └── {model}.py
   ├── views/
   │   ├── {model}_views.xml
   │   └── menu.xml
   ├── security/
   │   └── ir.model.access.csv
   ├── data/
   │   └── data.xml
   ├── controllers/
   │   ├── __init__.py
   │   └── main.py
   └── static/
       └── src/
           ├── js/
           └── xml/
   ```

5. **Generate __manifest__.py**:
   ```python
   {
       "name": "{Module Name}",
       "summary": "{Brief description}",
       "author": "{Author Name}",
       "website": "{Website URL}",
       "category": "{category}",
       "version": "{version}",
       "license": "LGPL-3",
       "depends": ["base"{additional_deps}],
       "data": [
           "security/ir.model.access.csv",
           "views/{model}_views.xml",
       ],
       "assets": {},
       "installable": True,
       "application": {is_app},
       "auto_install": False,
   }
   ```

6. **Create placeholder files**:
   - `models/__init__.py`: `from . import {model}`
   - `models/{model}.py`: Base model class
   - `views/{model}_views.xml`: Empty `<odoo>` structure
   - `security/ir.model.access.csv`: Header row
   - `controllers/__init__.py`: Empty
   - `controllers/main.py`: Empty controller
   - `__init__.py`: Empty

7. **Create security file** (ir.model.access.csv):
   ```csv
   id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
   access_{model}_user,{model} user,model_{model},base.group_user,1,0,0,0
   access_{model}_manager,{model} manager,model_{model},base.group_system,1,1,1,1
   ```

8. **Show summary**:
   - Module path
   - Dependencies
   - Next steps (add models, views, install module)

9. **Offer to create initial model** or view if user wants.

## Example Usage

```
/odoo-module create "custom_feature" --category="Inventory" --depends="stock" --application=True
```

```
Create module for product management:
- Name: product_management
- Category: Inventory
- Depends: base, stock
- Version: 17.0.1.0.0
```

## Module Naming Conventions

- Use snake_case for module name (e.g., `sale_order_merge`)
- Use singular nouns for model names (e.g., `sale.order`, not `sale.orders`)
- Prefix custom modules to avoid conflicts (e.g., `custom_`, `module_`)
- Version format: `{major}.{minor}.0.0` (Odoo standard)

## Manifest Best Practices

```python
{
    "name": "Module Name",
    "summary": "Brief one-line description",
    "description": """
        Longer description (optional)
        Can be multi-line
    """,
    "author": "Your Company",
    "website": "https://example.com",
    "category": "Category",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "data/data.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
```

## Important Notes

- Version format: `{major}.{minor}.{patch}.{revision}`
- For Odoo 17+: Use `"license": "LGPL-3"` or `"OPL-1"`
- Include all data files that must be loaded
- Set `application=True` only for standalone apps
- Use `auto_install=True` only for base/mixin modules
- Always add proper access rights in ir.model.access.csv
