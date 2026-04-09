---
name: odoo-master-index
description: Master index for ALL Odoo development skills - use this to find the right skill for any Odoo task. Automatically loaded for any Odoo-related request to guide skill selection.
---

# Odoo Development Skills - Master Index

This is the master index for all Odoo skills. Use this to find the right skill for your task.

## Quick Reference

| Task | Use Skill |
|------|-----------|
| **DEBUGGING & ERRORS** | |
| Debug Python/ORM errors | `odoo-debug.md` |
| Fix Odoo bugs with TDD | `odoo-debug-tdd` |
| Fix specific issues | `odoo-fix-guide.md` |
| Investigate before fixing | `odoo-investigate-before-fix` |
| Error analysis | `odoo-error-analysis` |
| **MODULE CREATION** | |
| Create new module | `odoo19-module-new` or `odoo-module.md` |
| Add fields to model | `odoo19-field-add` or `odoo-field.md` |
| Create model | `odoo19-model-new` or `odoo-model.md` |
| Create wizard | `odoo19-wizard-new` or `odoo-wizard.md` |
| Create API endpoint | `odoo19-api-rest` or `odoo-api.md` |
| **TESTING & QA** | |
| Write unit tests | `odoo-testing.md` or `odoo19-test-unit` |
| Test strategy | `odoo-testing-strategy` |
| Test specific module | `odoo-module-test` |
| Click-all JS testing | `odoo-click-anywhere-test` |
| **VIEWS & UI** | |
| Create views | `odoo-view.md` or `odoo19-view-*` (tree, form, kanban, etc.) |
| Fix view errors | `odoo-debug.md` (view errors section) |
| **WORKFLOWS & AUTOMATION** | |
| Create workflow | `odoo19-flow-state` or `odoo19-flow-approval` |
| Server actions | `odoo19-automation-server-action` |
| Scheduled jobs | `odoo19-automation-cron` |
| Workflow analysis | `odoo-workflow-analysis` |
| **SECURITY** | |
| Security audit | `odoo-security-analysis` |
| Access control | `odoo19-security-*` (xml, rule, group, field) |
| Security review | `odoo-security-review` |
| **PERFORMANCE** | |
| Performance optimization | `odoo-performance-guide` |
| Performance analysis | `odoo-performance-analysis` |
| N+1 query detection | `odoo-performance-analysis` |
| **BATCH OPERATIONS** | |
| Mass updates | `odoo-batch.md` |
| Data import/export | `odoo-batch.md` |
| **MIGRATION** | |
| Module migration | `odoo-module-migration` |
| Model migration | `odoo19-migrate-model` |
| View migration | `odoo19-migrate-view` |
| Manifest migration | `odoo19-migrate-manifest` |
| Migration analysis | `odoo-migration-analysis` |
| **ARCHITECTURE & ANALYSIS** | |
| Module architecture | `odoo-architecture.md` or `odoo-architecture-analysis` |
| Business process | `odoo-business-process` |
| Cross-module analysis | `odoo-cross-module-analysis` |
| Integration analysis | `odoo-integration-analysis` |
| Data model analysis | `odoo-data-model-analysis` |
| **DOCUMENTATION** | |
| Functional docs | `odoo-functional-doc.md` |
| Custom module docs | `superpowers:odoo-custom-docs` |
| **ENVIRONMENT** | |
| Initialize project | `odoo-init` |
| Environment setup | `odoo-environment` or `odoo-environment-detector` |
| Service management | `odoo-odoo-service` |
| Module install/upgrade | `odoo-module-install` |
| Database management | `odoo-db-management` |

## Skills by Category

### Core Development
- `odoo-debug.md` - Error debugging & fixing
- `odoo-testing.md` - Unit & integration testing
- `odoo-batch.md` - Batch operations
- `odoo-architecture.md` - Module architecture
- `odoo-module.md` - Module creation
- `odoo-model.md` - Model generation
- `odoo-field.md` - Field operations
- `odoo-api.md` - API development
- `odoo-wizard.md` - Wizard creation

### Views & UI
- `odoo-view.md` - View creation
- `odoo19-view-tree` / `odoo19-view-list`
- `odoo19-view-form`
- `odoo19-view-search`
- `odoo19-view-kanban`
- `odoo19-view-pivot`
- `odoo19-view-graph`
- `odoo19-view-calendar`
- `odoo19-view-activity`

### Workflows & Automation
- `odoo19-flow-state` - State machine
- `odoo19-flow-approval` - Approval workflows
- `odoo19-automation-server-action`
- `odoo19-automation-cron`
- `odoo-workflow-analysis`

### Security
- `odoo-security-analysis`
- `odoo19-security-xml`
- `odoo19-security-rule`
- `odoo19-security-group`
- `odoo19-security-field`
- `odoo-security-review`

### Performance
- `odoo-performance-guide`
- `odoo-performance-analysis`

### Reports
- `odoo19-report-qweb`
- `odoo19-report-xlsx`
- `odoo-reporting-analysis`

### External Integration
- `odoo19-api-rest`
- `odoo19-api-external`
- `odoo-integration-analysis`

### Data & Migration
- `odoo-module-migration`
- `odoo19-migrate-model`
- `odoo19-migrate-view`
- `odoo19-migrate-manifest`
- `odoo-migration-analysis`
- `odoo-batch.md` - Import/export

### Documentation
- `odoo-functional-doc.md`
- `odoo-business-process`
- `superpowers:odoo-custom-docs`

## Odoo Version Compatibility

| Skill | 17 | 18 | 19 |
|-------|-----|-----|-----|
| Generic skills (root) | ✓ | ✓ | ✓ |
| odoo19-* skills | Compatible | Compatible | ✓ Primary |
| Version-specific | ✓ Primary | Compatible | Compatible |

## How to Use

1. **Identify your task** from the table above
2. **Use the matching skill** via Skill tool
3. **For complex tasks**, chain multiple skills as needed
4. **For project-specific needs**, add to CLAUDE.md

## Version-Specific Notes

### Odoo 17 Breaking Changes
- `<tree>` view → `<list>` view
- `attrs` → direct `invisible` attribute
- `states` attribute → `invisible`
- `@api.model` deprecated
- `request.cr` replaced with `env.cr`

### Odoo 19 Breaking Changes
- All Odoo 17 changes
- `category_id` removed from `res.groups`
- `users` field removed from `res.groups`
- `type='json'` → `type='jsonrpc'`
- `expand` attribute removed from search groups

## Emergency Contacts

For urgent issues:
1. Check `odoo-debug.md` for error patterns
2. Use `odoo-investigate-before-fix` for root cause
3. Apply fix from appropriate skill
