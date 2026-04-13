---
name: odoo-vault-researcher
description: |
  Autonomous documentation researcher for Odoo source code vaults. TRIGGER ONLY
  when the topic or context is specifically about Odoo ERP. This skill reads actual
  Odoo source code and creates Obsidian documentation vaults.

  DO NOT TRIGGER for general topics, non-Odoo frameworks, or generic autoresearch.
  Only use this skill when Odoo is explicitly mentioned.

  Specific triggers (Odoo must appear in the request):
  - "Start vault research for Odoo 17" or "/vault-research odoo-17"
  - "Create documentation vault for Odoo 18"
  - "Research Odoo 17 stock module" or "Research Odoo [version] [module]"
  - "Begin research on [module] for [version]" where [version] is Odoo
  - "Build Odoo [version] vault"
  - "Populate vault for Odoo [version]"
  - "Continue research for Odoo 19"
  - "Verify Odoo 17 purchase module"
  - "Do autoresearch on Odoo [topic]" — ONLY when Odoo is specified
  - "Build Odoo [version] vault for [module]" — ONLY when Odoo is specified

  Non-Odoo topics that should NOT trigger this skill:
  - "autoresearch on building an app" — ❌ NO Odoo
  - "do a deep dive on LLM patterns" — ❌ NO Odoo
  - "research this topic" without Odoo mention — ❌ NO Odoo
  - "create a vault for Python FastAPI" — ❌ NO Odoo

  If the user says "autoresearch" without specifying Odoo, use the general
  autoresearch-planner skill instead (not this one).
commands:
  - /vault-research [version] [options] - Start research for specified version
  - /vault-stop - Stop current research
  - /vault-status - Show current research status
  - /vault-log [lines=50] - Show activity log
  - /vault-verify module=X [version=Y] - Verify module documentation against code
  - /vault-list - List all Odoo vaults and their status
  - /vault-resume [version] - Resume interrupted research
---

# Odoo Vault Researcher

Generic, version-agnostic autonomous documentation researcher. Creates and
populates Obsidian vaults for any Odoo version by reading actual source code
and cross-referencing with existing documentation patterns.

## Path Resolution

The skill dynamically resolves paths based on target Odoo version:

```
# Odoo version → vault path
Odoo 17 → ~/odoo-vaults/odoo-17
Odoo 18 → ~/odoo-vaults/odoo-18
Odoo 19 → ~/odoo-vaults/odoo-19
Odoo 20 → ~/odoo-vaults/odoo-20

# Odoo version → source code path
Odoo 17 → ~/odoo/odoo17/odoo
Odoo 18 → ~/odoo/odoo18/odoo
Odoo 19 → ~/odoo/odoo19/odoo
Odoo 19-suqma → ~/odoo/odoo19-suqma/odoo
Odoo 13 → ~/odoo/odoo13-mg/odoo

# Source code modules location
addons/  (standard modules)
enterprise/  (enterprise modules, if available)
```

### Detection Rules (in priority order)

1. **Explicit version**: User specifies `--version=17` or "Odoo 17"
   → Use `~/odoo/odoo17/` and `~/Obsidian Vault/Odoo-17`

2. **Vault-first**: User specifies vault path directly
   → Extract version from vault name (e.g., "Odoo-17" → version 17)
   → Set source path accordingly

3. **Source-first**: User provides Odoo source path
   → Detect version from path (e.g., "odoo19" in path → version 19)
   → Set vault path accordingly

4. **Auto-detect**: If only one version exists in ~/odoo/, use that

5. **Conflict**: If multiple versions exist, ask user to specify

## Vault Structure

All vaults use identical folder structure (consistent with Odoo 19 vault):

```
Odoo-{version}/
├── 00 - Index.md              # Root navigation hub
├── CLAUDE.md                   # Claude Code instructions
├── Core/                      # ORM framework fundamentals
│   ├── BaseModel.md           # _name, _inherit, CRUD, _rec_name
│   ├── Fields.md              # Field types, parameters, comodel
│   ├── API.md                 # @api.depends, @api.onchange, @api.constrains
│   ├── HTTP Controller.md     # @http.route, auth types
│   └── Exceptions.md          # ValidationError, UserError, AccessError
├── Patterns/                  # Architectural patterns
│   ├── Inheritance Patterns.md
│   ├── Workflow Patterns.md
│   └── Security Patterns.md
├── Tools/
│   ├── ORM Operations.md      # search(), browse(), domain operators
│   └── Modules Inventory.md   # All available modules catalog
├── Snippets/
│   ├── Model Snippets.md
│   ├── Controller Snippets.md
│   └── method-chain-example.md
├── New Features/              # Version-specific changes
│   ├── What's New.md
│   ├── API Changes.md
│   └── New Modules.md
├── Modules/                   # Per-module documentation (all addons)
│   ├── 00 - DOC PLAN.md
│   ├── TEMPLATE-module-entry.md
│   ├── {module}.md           # Main modules: stock, purchase, sale, account, etc.
│   ├── {submodule}.md        # All other modules as individual files
│   └── l10n_{country}.md    # Country localization modules
├── Business/                 # End-user guides
│   ├── TEMPLATE-guide.md
│   ├── Sale/
│   ├── Purchase/
│   ├── Stock/
│   ├── Account/
│   └── [department]/...
├── Flows/                     # Business process flows
│   ├── TEMPLATE-flow.md
│   ├── Sale/
│   ├── Purchase/
│   ├── Stock/
│   ├── Cross-Module/
│   └── [category]/...
├── Documentation/             # Progress tracking
│   ├── Checkpoints/
│   └── Upgrade-Plan/
├── Research-Log/              # Research state management
│   ├── active-run/
│   ├── completed-runs/
│   ├── backlog.md
│   └── verified-status.md
└── docs/plans/                # Implementation plans (if any)
```

## Research Options

```
--version={N}     Target Odoo version (17, 18, 19, 20)
--modules=...     Comma-separated modules to research (default: all)
--mode=deep       deep (L4) | medium (L3) | quick (L2)
--limit=60m       Time limit (m=minutes, h=hours)
--checkpoint=10m  Save checkpoint every N minutes
--vault=path      Custom vault path (overrides default)
--source=path     Custom Odoo source path (overrides default)
```

## Depth Levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Surface | Field/method names, signatures, basic types |
| L2 | Context | Defaults, constraints, onchanges, why it exists |
| L3 | Edge Cases | Cross-model relations, workflow triggers, failure modes |
| L4 | Historical | Performance, overrides, version changes (vs Odoo N-1) |

Mode mapping:
- `--mode=quick` → L2 (Surface + Context)
- `--mode=medium` → L3 (adds Edge Cases)
- `--mode=deep` → L4 (adds Historical)

## Research Loop (Per Module)

### 1. Discover
```
- Scan: ~/odoo/odoo{ver}/odoo/addons/{module}/models/*.py
- Extract: model classes, _name, _inherit, fields, methods
- Build: initial structure map
```

### 2. Verify + Depth (parallel)
```
- Code vs Doc: Read actual source, confirm documented behavior
- Record: exact file path and line numbers for all claims
- Cross-check: parent models, mixins, depends
```

### 3. Document
```
- Write: verified + deep doc to vault (Modules/{module}.md)
- Follow: vault structure and wikilink conventions
- Cross-link: to Core/, Patterns/, and related Modules/
```

### 4. Track
```
- Update: Research-Log/backlog.md (gaps found)
- Update: Research-Log/verified-status.md (verified entries)
- Log: Research-Log/active-run/log.md (activity timeline)
```

### 5. Checkpoint
```
- Trigger: every N minutes OR after each module
- Save: run_id, current position, verified count, gaps
- Enable: clean resume on interruption
```

## Module Discovery Priority

Research order based on dependency graph:

```
Tier 1 (Foundation):
  base, mail, ir_actions, ir_rule

Tier 2 (Core Business):
  sale, purchase, stock, account, product

Tier 3 (Extended Business):
  crm, project, hr, mrp, quality, repair

Tier 4 (Ecosystem):
  website, sale_management, purchase_requisition, etc.

Tier 5 (Integrations):
  payment_*, l10n_*, auth_*, google_*, microsoft_*

Tier 6 (Advanced):
  mrp_subcontracting_*, pos_self_order_*, etc.
```

## Verification (/vault-verify)

Compare vault documentation against actual source code:

```
/vault-verify module=stock [model=stock.quant] [version=17] [deep|quick]
```

1. Load vault documentation
2. Load source code for module/model
3. Check each documented field/method against code
4. Report discrepancies (missing, wrong type, outdated)
5. Flag entries needing update
6. Add to backlog if gaps found

## Output Files

| File | Purpose |
|------|---------|
| `Modules/{module}.md` | Main module documentation |
| `Research-Log/backlog.md` | Pending gaps to document |
| `Research-Log/verified-status.md` | Verified module entries |
| `Research-Log/active-run/log.md` | Current session activity |
| `Research-Log/completed-runs/run-{timestamp}/` | Completed run snapshots |

## Error Handling

| Situation | Response |
|-----------|----------|
| Odoo path invalid | Flag error, list available versions |
| No write permission on vault | Create vault if needed, or error |
| Module not found in source | Log gap, skip module |
| Source path differs from expected | Auto-detect from actual path |
| Interrupted research | Save checkpoint, offer resume |
| Version already has vault | Ask: "Overwrite? Append? Skip?" |

## WikiLink Conventions

Follow Obsidian Flavored Markdown consistently:

```
Core links:      [[Core/BaseModel]], [[Core/API]]
Module links:    [[Modules/Stock]], [[Modules/sale_stock]]
Pattern links:   [[Patterns/Workflow Patterns]]
Flow links:      [[Flows/Stock/receipt-flow]]
Business links:  [[Business/Stock/warehouse-setup-guide]]
Python models:   `account.move`, `stock.picking` (backticks, NOT wikilinks)
```

**Never use bare names**: `[[Sale]]` → `[[Modules/Sale]]`
**Never link to Python model names**: `[[sale.order]]` → `` `sale.order` ``

## Commands Reference

```
/vault-research odoo-17
  → Start research for Odoo 17, auto-detect paths

/vault-research --version=18 --modules=stock,sale,purchase --mode=deep
  → Deep research on 3 modules for Odoo 18

/vault-research --vault="~/Obsidian Vault/MyOdoo18" --source=~/odoo/odoo18/
  → Custom paths for research

/vault-list
  → Show all vaults: Odoo-17 (empty), Odoo-18 (partial), Odoo-19 (complete)

/vault-verify module=purchase version=17
  → Verify existing Odoo 17 purchase module docs

/vault-stop
  → Graceful stop, save checkpoint

/vault-resume odoo-17
  → Resume from last checkpoint
```
