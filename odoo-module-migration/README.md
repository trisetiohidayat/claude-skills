# Odoo Module Migration Skill

Claude Code skill for migrating Odoo custom module code between versions with intelligent breaking changes analysis.

## Features

- **Version Comparison** - Compare old vs new Odoo/Enterprise code to identify breaking changes
- **Per-Module Migration** - Migrate each module individually with dependency tracking
- **Knowledge Base** - Generate comprehensive breaking changes documentation
- **Manual Review Guide** - Create per-module checklist for business process changes
- **CLAUDE.md Generation** - Create context file for ongoing migration
- **Migration Tracking** - Track progress per module (COMPLETED/NEEDS REVIEW/FAILED)

## Scope

This skill handles **module code migration only**. For database migration, use the separate `odoo-db-migration` skill.

## Installation

1. Install odoo-module-migrator:
   ```bash
   pip3 install odoo-module-migrator
   ```

2. Copy this skill to your Claude Code skills directory:
   ```bash
   cp -r odoo-module-migration ~/.claude/skills/
   ```

## Usage

### Invoke via Skill tool:
```
/odoo-migration
```

Or describe your migration needs:
- "Migrate my custom modules from Odoo 15 to 17"
- "Port this module to Odoo 17, I have old Odoo at /path/odoo15 and new at /path/odoo17"
- "Help me migrate module_a and module_b from Odoo 16 to 18"

## Complete Workflow

The skill performs these steps automatically:

```
STEP 1: Ask user for paths
  - Path to old Odoo/Enterprise source code
  - Path to new Odoo/Enterprise source code
  - Source/target version
  - List of modules to migrate

STEP 2: Version Comparison
  - Analyze Odoo code from both versions
  - Identify breaking changes
  - Generate knowledge base

STEP 3: Per-Module Migration (iterate for each module)
  - Analyze module dependencies
  - Migrate module using odoo-module-migrator
  - Check for breaking changes
  - Generate module-specific fixes
  - Create module review checklist
  - Mark module status

STEP 4: Generate Output
  - CLAUDE.md with breaking changes
  - Per-module review checklists
  - Migration summary

STEP 5: Recommend odoo-db-migration skill for database
```

## Supported Versions

The skill supports migration from any version to any higher version (8.0 to 19.0):
- 8.0 → 19.0 (direct!)
- 15.0 → 17.0 (direct!)
- 15.0 → 16.0 (consecutive)

The tool runs all intermediate migration steps internally.

## Scripts

### compare_odoo_versions.py
Compare old and new Odoo versions to identify breaking changes:
```bash
python3 scripts/compare_odoo_versions.py /path/to/odoo-15.0 /path/to/odoo-17.0 15.0 17.0
```

### generate_context.py
Generate CLAUDE.md for migration:
```bash
python3 scripts/generate_context.py 15.0 17.0 module_a module_b

# With breaking changes from comparison
python3 scripts/generate_context.py 15.0 17.0 module_a -b breaking_changes_15.0_17.0.json
```

### validate_versions.py
Validate if migration path is supported:
```bash
python3 scripts/validate_versions.py 15.0 17.0
```

### odoo_upgrade.sh
For database upgrade, use the separate `odoo-db-migration` skill.

## File Structure

```
project/
├── CLAUDE.md                 # Migration context (generated)
├── migration_knowledge/      # Breaking changes (generated)
│   └── breaking_changes_*.md
├── module_migration/         # Per-module migration results
│   ├── module_a/
│   │   ├── migrated/
│   │   └── review_checklist.md
│   └── module_b/
│       ├── migrated/
│       └── review_checklist.md
└── scripts/
    ├── compare_odoo_versions.py   # Version comparison
    ├── validate_versions.py         # Version validation
    └── generate_context.py          # CLAUDE.md generator

odoo-15.0/                   # Old Odoo source (provided by user)
odoo-17.0/                   # New Odoo source (provided by user)
custom_modules/              # Modules to migrate
```

## Breaking Changes Knowledge Base

The skill maintains knowledge of breaking changes for each Odoo version:

| Version | Key Changes |
|---------|-------------|
| 12+ | @api.multi deprecated, workflow removed |
| 16+ | Many2one ondelete changes, mail updates |
| 17+ | request.cr deprecated, osv.Model removed |
| 18+ | XMLRPC deprecated |

## Database Migration

For database migration, use the separate `odoo-db-migration` skill:
- Trigger: `/odoo-db-migration` or "migrate database Odoo"
- Handles: dump analysis, upgrade.odoo.com integration, SQL fixes

## Requirements

- Python 3.8+
- odoo-module-migrator
- Git
- Access to old and new Odoo/Enterprise source code
