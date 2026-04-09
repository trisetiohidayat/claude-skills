---
name: odoo-custom-docs
description: >
  Create comprehensive documentation for Odoo customizations by analyzing both source code
  AND live database. Use when user wants to document what customizations exist in their
  Odoo installation with ACTUAL data from database - including installed modules, dependencies,
  custom models, views, business logic, security rules, and menu structure.
  MUST use this skill when user provides odoo.conf path, database connection details,
  or asks about "module apa saja yang terinstall" / "apa yang active di Odoo saya".
  This skill is essential for understanding Odoo business process and module relationships.
---

# Odoo Custom Documentation Skill (Enhanced with DB Access)

## When to Use

Use this skill when:
- User asks to document Odoo customizations
- User wants to know what custom modules are **actually installed/enabled**
- User asks "module apa saja yang terinstall?" or "apa yang active di Odoo?"
- User provides `odoo.conf` path or database connection details
- User provides paths to both custom modules AND CE/EE addons
- User needs to understand dependencies between modules
- User asks about business process and module relationships in Odoo

## Input Requirements

User MUST provide ONE of these:
- `custom_modules_path`: Path to folder containing custom modules
- **OR** `odoo_conf_path`: Path to odoo.conf file (to auto-detect addons_path and DB)
- **OR** database connection details (host, db, user, password)

User CAN provide:
- `odoo_ce_path`: Path to Odoo CE addons (for comparison/identification)
- `odoo_ee_path`: Path to Odoo EE addons (for comparison/identification)
- `output_dir`: Output directory (default: `./odoo-custom-docs`)

## New Capability: DB Connection

### Connection Methods (Priority Order)

1. **From odoo.conf** (recommended):
   - Read `odoo.conf` to get:
     - `addons_path` - list of addon directories
     - `db_host`, `db_port`, `db_user`, `db_password`, `db_name`
   - Use these to connect to the database

2. **Direct connection** (if provided):
   - Use provided DB credentials directly

3. **Without DB** (fallback):
   - Only analyze source code (limited to what's in filesystem)

### Database Queries to Execute

```sql
-- Get ALL installed modules (including dependencies)
SELECT name, state, version, depends
FROM ir_module_module
WHERE state IN ('installed', 'to upgrade', 'to install')
ORDER BY name;

-- Get module dependencies
SELECT name, depends
FROM ir_module_module
WHERE state = 'installed';

-- Get custom fields added by modules
SELECT m.name as module, f.name as field, f.model, f.field_description
FROM ir_model_fields f
JOIN ir_module_module m ON f.module = m.name
WHERE f.module IS NOT NULL
ORDER BY m.name, f.name;

-- Get views and their modules
SELECT m.name as module, v.type, v.model, v.name, v.arch
FROM ir_ui_view v
JOIN ir_model_data m ON m.model = 'ir.ui.view' AND m.res_id = v.id
WHERE m.module IS NOT NULL;

-- Get security rules
SELECT m.name as module, a.model_id, a.group_id, a.perm_read, a.perm_write, a.perm_create, a.perm_unlink
FROM ir_model_access a
JOIN ir_module_module m ON a.group_id IS NULL OR m.id = (
    SELECT id FROM res_groups WHERE id = a.group_id LIMIT 1
);

-- Get menu structure
SELECT m.name as module, m.parent_path, m.action
FROM ir_ui_menu m
JOIN ir_model_data d ON d.model = 'ir.ui.menu' AND d.res_id = m.id
WHERE d.module IS NOT NULL;
```

## Process

### Step 0: DB Connection (NEW)

1. **Parse odoo.conf** if provided:
   - Read addons_path to find all addon directories
   - Extract DB connection parameters
   - Connect to PostgreSQL using psycopg2 or odoo tools

2. **Query installed modules** from DB:
   - Get list of ALL installed modules (including dependencies)
   - Get version info from DB
   - Get dependency information

3. **Store DB data** for later use in analysis

### Step 1: Discover Modules (Enhanced)

**With DB access:**
1. Query `ir_module_module` to get ALL installed modules from DB
2. For each installed module, find its location in addons_path
3. Identify which are custom vs. standard:
   - If module exists in CE/EE path → standard module
   - If module exists ONLY in custom path → custom module
   - If module in both → overridden/customized

**Without DB access:**
1. List all directories in custom_modules_path
2. Check for `__manifest__.py` or `__openerp__.py`
3. Parse manifest for dependencies

### Step 2: Identify Custom Modules

Compare modules found with CE/EE:

```
Classification:
├── Standard (CE/EE only)
│   └── Exists in odoo/addons or ee/addons
├── Custom (user-developed)
│   └── Only exists in custom_modules_path
├── Overridden (standard modified)
│   └── Exists in both custom_path and CE/EE
└── External/Third-party
    └── Exists in neither (community modules)
```

### Step 3: Analyze Each Module with Subagents

For each custom module, launch subagent with **additional DB context**:

**Subagent prompt template:**

```

Analyze Odoo module at {module_path} and extract:

## Module Info
- Name: {module_name}
- Version: from manifest
- Description: from manifest
- Dependencies: {dependencies_from_manifest}
- DB Dependencies: {dependencies_from_db}

## Module Status (from DB)
- State: {installed/to_install/uninstalled}
- Is Custom: {yes/no/overridden}
- Dependencies: {list from DB}

## Custom Models
List all models defined in models/*.py files:
- Model name (e.g., 'custom.model')
- Model description
- Fields:
  - Field name
  - Field type (Char, Many2one, etc.)
  - Required, Readonly, Default values
- Methods defined (just names, not full code)

## Custom Views
List all views in views/*.xml:
- View type (form, tree, kanban, etc.)
- View ID/name
- Model being extended
- Key field definitions

## Business Logic
- Custom methods in models
- Onchange methods (@api.onchange)
- Constraints (@api.constrains)
- Computed fields (@api.depends)

## Security
- ACL files (security/*.csv)
- ir.rule definitions
- Group definitions

## Menus
- Menu items in views/*.xml
- Window actions

## Dependency Impact (NEW)
- What modules depend on this module?
- What modules does this module depend on?
- Is this a base module (many dependencies)?

Return results in structured format for aggregation.
```

### Step 4: Aggregate Results (Enhanced)

After all subagents complete:

1. Read all subagent outputs
2. Group by category
3. Generate `01_overview.md` with **DB-verified data**:
   - Total modules installed (from DB)
   - Custom modules identified (from source + DB)
   - Dependencies between custom modules
   - Impact analysis (what breaks if custom module is removed)

### Step 5: Generate Dependency Graph (NEW)

Create additional output showing:
- Which standard modules depend on custom modules
- Which custom modules depend on each other
- Critical custom modules (many dependencies)

## Output Format (Enhanced)

#### 01_overview.md
```markdown
# Odoo Custom Modules Documentation

Generated: {date}
Database: {db_name}@{db_host}

## Summary

| Category | Count |
|----------|-------|
| Installed Modules (DB) | {n} |
| Custom Modules | {n} |
| Overridden Modules | {n} |
| External Modules | {n} |
| Custom Models | {n} |
| Custom Views | {n} |
| Business Logic | {n} |
| Security Rules | {n} |
| Menu Items | {n} |

## Module Classification

### Custom Modules (User-Developed)
{modelist}

### Overridden Modules (Modified Standard)
{modelist}

### External/Third-Party
{modelist}

## Dependency Analysis

### Critical Custom Modules
These custom modules are dependencies for multiple other modules:
- {module_name}: required by {dependent_modules}

### Module Dependency Graph
{graph_visualization}
```

#### 02_custom_models.md
(Same as before, but mark if model exists in DB)

#### 07_dependency_analysis.md (NEW)
```markdown
# Module Dependencies

## Custom Module Dependencies

### {module_name}
- **Status:** Installed/Uninstalled
- **Depends On:** {list}
- **Required By:** {list}
- **Is Critical:** Yes/No (if required by many)

## Dependency Tree

```
custom.module.a
├── standard.module.b
└── custom.module.c
    └── standard.module.d
```

## Impact Analysis

If you uninstall {custom_module}:
- Will break: {list of dependent modules}
- Will affect: {list of menu items, views, etc.}
```

## Bundled Scripts

Create helper scripts in `scripts/` directory:

### scripts/db_connect.py
```python
#!/usr/bin/env python3
"""
Odoo Database Connection Helper
Connects to Odoo PostgreSQL database to get module information.
"""
import os
import sys
import json
import configparser

def parse_odoo_conf(conf_path):
    """Parse odoo.conf file and extract connection parameters."""
    config = configparser.ConfigParser()
    config.read(conf_path)

    db_config = {}
    if 'options' in config:
        opts = config['options']
        db_config['host'] = opts.get('db_host', 'localhost')
        db_config['port'] = opts.get('db_port', '5432')
        db_config['user'] = opts.get('db_user', 'odoo')
        db_config['password'] = opts.get('db_password', 'odoo')
        db_config['database'] = opts.get('db_name', 'odoo')
        db_config['addons_path'] = opts.get('addons_path', '').split(',')

    return db_config

def get_installed_modules(db_config):
    """Query installed modules from database."""
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        return None

    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        cur = conn.cursor()

        cur.execute("""
            SELECT name, state, version, depends
            FROM ir_module_module
            WHERE state IN ('installed', 'to upgrade', 'to install')
            ORDER BY name
        """)

        modules = []
        for row in cur.fetchall():
            modules.append({
                'name': row[0],
                'state': row[1],
                'version': row[2],
                'depends': row[3] or []
            })

        cur.close()
        conn.close()

        return modules
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python db_connect.py <odoo.conf>")
        sys.exit(1)

    conf = parse_odoo_conf(sys.argv[1])
    print(json.dumps(conf, indent=2))

    modules = get_installed_modules(conf)
    if modules:
        print(f"\nFound {len(modules)} installed modules:")
        for m in modules[:10]:  # Show first 10
            print(f"  - {m['name']} ({m['state']})")
</script>

### scripts/module_classifier.py
```python
#!/usr/bin/env python3
"""
Classifies modules as custom/standard/overridden based on paths.
"""
import os
import json
import ast

def parse_manifest(path):
    """Parse __manifest__.py safely."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            # Simple parsing - extract dict content
            # In production, use ast.literal_eval
            manifest = {}
            exec(manifest_var := f"manifest = {content.split('=')[1] if '=' in content else content}", {}, manifest)
            return manifest.get('manifest', {})
    except Exception as e:
        return {}

def classify_module(module_name, custom_paths, ce_path, ee_path):
    """Classify a module as custom/standard/overridden."""
    in_custom = any(os.path.exists(os.path.join(p, module_name)) for p in custom_paths)
    in_ce = ce_path and os.path.exists(os.path.join(ce_path, module_name))
    in_ee = ee_path and os.path.exists(os.path.join(ee_path, module_name))

    if in_custom and not in_ce and not in_ee:
        return 'custom'
    elif in_custom and (in_ce or in_ee):
        return 'overridden'
    elif in_ce or in_ee:
        return 'standard'
    else:
        return 'external'

if __name__ == '__main__':
    # Example usage
    print("Module classifier ready")
</script>

## Error Handling (Enhanced)

### Additional Edge Cases

11. **No DB access** - Continue with source-only analysis, note limitation in output
12. **Invalid odoo.conf** - Try alternative connection methods or warn user
13. **DB connection failed** - Log error, continue without DB data
14. **Empty module list from DB** - Likely wrong database, warn user
15. **Module in DB but not in filesystem** - Note as "missing from addons_path"

### Error Handling Approach

Same as before, plus:
- If DB connection fails: log warning, continue with source-only analysis
- If odoo.conf not found: ask user for direct DB connection or paths

## User Feedback (Enhanced)

During execution:
1. "Connecting to database: {db_name}@{db_host}"
2. "Found {n} installed modules in database"
3. "Discovered {n} custom modules in {path}"
4. "Classifying modules using CE: {ce_path}, EE: {ee_path}"
5. "Analyzing module {i}/{n}: {module_name}"
6. "Generating dependency analysis..."
7. "Complete! Generated {n} files"

## Example Usage

### Full Analysis (with DB)
```
/odoo-custom-docs --conf /etc/odoo/odoo.conf --ce /path/to/odoo/addons --ee /path/to/enterprise
```

### Source Only (no DB)
```
/odoo-custom-docs /path/to/custom_addons
```

### Custom + CE + EE Comparison
```
/odoo-custom-docs /path/to/custom --ce /odoo/addons --ee /enterprise
```
