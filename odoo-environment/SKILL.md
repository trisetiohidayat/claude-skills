---
name: odoo-environment
description: Use when user asks to check, verify, or examine Odoo environment, configuration, or setup status. Use when needing Odoo connection details, port numbers, database info, or module locations. Use when user mentions "odoo.conf", configuration file selection, or environment setup. Automatically searches for odoo.conf files in the project and asks for confirmation if multiple found, unless session context already specifies which configuration to use.
skills:
  - odoo-path-resolver
---

# Odoo Environment Checker

## Overview

Use `odoo-path-resolver` to get all paths dynamically, then verify with runtime checks. This skill provides a higher-level abstraction for environment status reporting.

## Why This Matters

Using `odoo-path-resolver` ensures consistent path resolution across all skills. Runtime checks catch issues config files miss.

## When to Use

```dot
digraph odoo_check {
    "User asks about Odoo?" [shape=diamond];
    "Need config before task?" [shape=diamond];
    "Verify env status?" [shape=diamond];
    "Use odoo-env-checker" [shape=box];

    "User asks about Odoo?" -> "Use odoo-env-checker" [label="yes"];
    "Need config before task?" -> "Use odoo-env-checker" [label="yes"];
    "Verify env status?" -> "Use odoo-env-checker" [label="yes"];
}
```

**Use when:**
- User says "periksa environment", "check odoo", "cek konfigurasi"
- Need port, database, or connection details
- Verifying Odoo is running before starting work
- Debugging Odoo connection issues

**Don't use for:**
- Reading specific Odoo model definitions (use Read tool directly)
- Running Odoo commands (just run them)

## Quick Reference

| Source | What to Extract | How to Get |
|--------|-----------------|------------|
| `odoo-path-resolver` | All paths (bin, python, db, port) | `paths = resolve()` |
| Runtime | running processes, db connection | `ps aux \| grep odoo-bin`, `pg_isready` |

## Implementation

### Step 0: Load odoo-path-resolver First

Since this skill declares `odoo-path-resolver` as a dependency, use `resolve()` to get all paths:

```python
# Get all paths dynamically
paths = resolve()

# Access values:
# paths['project']['root']        # /path/to/project
# paths['project']['config']       # /path/to/odoo19.conf
# paths['odoo']['bin']             # /path/to/odoo-bin
# paths['odoo']['python']          # /path/to/python
# paths['odoo']['version']         # 19
# paths['database']['host']         # localhost
# paths['database']['port']        # 5432
# paths['database']['user']        # odoo
# paths['database']['password']    # odoo
# paths['database']['name']        # roedl
# paths['server']['http_port']     # 8133
# paths['addons']['ce']            # /path/to/odoo/addons
# paths['addons']['ee']            # /path/to/enterprise
# paths['addons']['custom']        # ['/path/to/custom1', ...]
```

### Step 1: Check Session Context

Check if session context already specifies which Odoo configuration to use:
- Previous mentions of specific odoo.conf paths
- Database names specified in conversation
- Port numbers mentioned

If session context already specifies the config, use that. Otherwise, use `resolve()` which auto-detects the best config.

### Step 2: Verify with launch.json (Optional Override)

For debugging scenarios, launch.json may override config file settings:

```bash
# Find launch.json
find . -name "launch.json" -path "*/.vscode/*" 2>/dev/null
```

Extract from JSON:
- `args`: Look for `--http-port=`, `--database=`, `--config=`
- `program`: Path to odoo-bin
- `python`: Interpreter path

**Note:** Use values from `resolve()` as defaults, but launch.json takes precedence for debugging.

### Step 3: Runtime Checks

```bash
# Check if Odoo running
ps aux | grep "[o]doo-bin"

# Check PostgreSQL
pg_isready -h <db_host> -p <db_port> -U <db_user>

# Check Python version
python3 --version
```

### Step 4: Consolidate and Report

Report using values from `resolve()` with runtime verification:

```markdown
## Odoo Environment Status
### Configuration (from odoo-path-resolver)
- Port: 8133
- Database: roedl
- Odoo Bin: /path/to/odoo-bin
- Python: /path/to/python

### Database (from resolve())
- Host: localhost:5432
- User: odoo
- Password: odoo

### Runtime Status
- Odoo: ✅ Running (PID 12345)
- PostgreSQL: ✅ Connected
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Don't use resolve() | Always use `paths = resolve()` for path resolution |
| Only read config files | Add runtime checks (ps, pg_isready) |
| Trust static docs | Use odoo-path-resolver for dynamic resolution |

## Rationalization Counter-Measures

| Excuse | Reality |
|--------|---------|
| "I know the paths" | Use resolve() - paths may change |
| "Manual config lookup is faster" | resolve() auto-detects, faster than guessing |
| "Runtime checks take too long" | `ps` and `pg_isready` take <2 seconds. |

**Red Flags - You're Rationalizing:**
- Hardcoding paths
- Skipping runtime status checks
- "This is just a quick check"

**All of these mean: You're not done. Use resolve() + runtime checks.**
