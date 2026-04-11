# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository is a **Claude Code skills library** for Odoo 19 development, migration, and operations. Each directory is a standalone skill with a `SKILL.md` file that gets loaded via the `/skill-name` slash command.

## Skill Architecture

```
skill-name/
├── SKILL.md              # Main skill file (required)
└── [bundled files]       # Reference docs, scripts, themes (optional)
```

Skills are invoked via slash commands (e.g., `/odoo19-model-new`). Skills with subdirectories indicate bundled reference files alongside the skill.

## Key Skill Groups

| Prefix | Purpose |
|--------|---------|
| `odoo19-*` | Generate Odoo 19 models, views, controllers, reports, security, tests |
| `odoo-*-migration` | Migration (module code + database) between Odoo versions |
| `odoo-*-context` | Provide context for Odoo operations (must activate first) |
| `odoo-*-vault-*` | Obsidian vault documentation for Odoo |
| `autorel*` | AutoResearch automation (log, restart, status, stop, verify) |
| `gitnexus-*` | Git version control operations |
| `superpowers:*` | Core development workflows (brainstorming, debugging, TDD, planning) |

## Important Conventions

**Always activate `odoo-vault-base-context` first** before working with Odoo:
```
Use /odoo-vault-base-context skill FIRST before any Odoo task.
```

**Odoo 19 skills follow this pattern** for model naming:
- `_name` = external ID (e.g., `x_awesome_model`)
- `model/` = Python logical path (e.g., `awesome.model`)

**Migration workflow** (two separate skills):
1. `odoo-module-migration` — code syntax migration only
2. `odoo-db-migration` — database upgrade via upgrade.odoo.com

## No Build or Test Commands

This is a skills library, not a running application. There are no build, lint, or test commands. Each skill is self-contained instructions that guide code generation or operations.
