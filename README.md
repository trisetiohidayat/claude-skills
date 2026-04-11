# Claude Code Skills Library

A collection of Claude Code skills for Odoo 19 development, migration, and operations.

## Skills Overview

### Odoo 19 Code Generation (`odoo19-*`)

50+ skills for generating Odoo 19 components:

| Category | Skills |
|----------|--------|
| Models | `odoo19-model-new`, `odoo19-model-inherit`, `odoo19-model-abstract`, `odoo19-model-transient` |
| Fields | `odoo19-field-add`, `odoo19-field-compute`, `odoo19-field-relational`, `odoo19-field-selection` |
| Views | `odoo19-view-form`, `odoo19-view-tree`, `odoo19-view-kanban`, `odoo19-view-search`, `odoo19-view-pivot`, `odoo19-view-graph`, `odoo19-view-calendar`, `odoo19-view-activity`, `odoo19-view-map` |
| Business Logic | `odoo19-method-action`, `odoo19-method-onchange`, `odoo19-method-constraint` |
| Controllers | `odoo19-controller-new`, `odoo19-controller-http`, `odoo19-controller-json` |
| Reports | `odoo19-report-qweb`, `odoo19-report-xlsx` |
| Security | `odoo19-security-group`, `odoo19-security-rule`, `odoo19-security-field`, `odoo19-security-xml` |
| Automation | `odoo19-automation-cron`, `odoo19-automation-server-action` |
| Migration | `odoo19-migrate-model`, `odoo19-migrate-view`, `odoo19-migrate-manifest` |
| Domain-Specific | `odoo19-wizard-new`, `odoo19-wizard-confirm`, `odoo19-test-unit`, `odoo19-test-portal`, `odoo19-hr-employee`, `odoo19-project-task`, `odoo19-stock-picking`, `odoo19-account-invoice`, `odoo19-mrp-bom`, `odoo19-pos-config`, `odoo19-website-sale`, `odoo19-event-manage`, `odoo19-survey-create`, `odoo19-hr-timesheet`, `odoo19-web-widget`, `odoo19-web-assets`, `odoo19-web-template`, `odoo19-menu-item`, `odoo19-action-window`, `odoo19-data-xml`, `odoo19-data-demo`, `odoo19-utils-logging`, `odoo19-utils-translate`, `odoo19-utils-validation`, `odoo19-orm`, `odoo19-flow-state`, `odoo19-flow-approval`, `odoo19-api-rest`, `odoo19-api-external` |

### Odoo Analysis & Operations (`odoo-*`)

| Skill | Purpose |
|-------|---------|
| `odoo-vault-base-context` | **Always activate first** — provides Odoo running context |
| `odoo-db-migration` | Database migration via upgrade.odoo.com |
| `odoo-module-migration` | Module code syntax migration between versions |
| `odoo-module-install` | Module install/upgrade/uninstall via command line |
| `odoo-module-test` | Test Odoo modules comprehensively |
| `odoo-module-fixing` | Fix module bugs manually |
| `odoo-db-management` | Database backup/restore/duplicate |
| `odoo-db-restore` | Restore database from SQL dump |
| `odoo-environment` | Check/verify Odoo environment |
| `odoo-path-resolver` | Resolve Odoo paths and configuration |
| `odoo-architect` | Architecture analysis and planning |
| `odoo-architecture-analysis` | Modular architecture analysis |
| `odoo-business-process` | Understand Odoo business processes |
| `odoo-workflow-analysis` | State machine and approval flows |
| `odoo-data-model-analysis` | Model relationships and field types |
| `odoo-migration-analysis` | Migration analysis between versions |
| `odoo-cross-module-analysis` | Module dependencies analysis |
| `odoo-security-review` | Security review and checklist |
| `odoo-error-analysis` | Root cause identification |
| `odoo-investigate-before-fix` | Debug specific errors before fix |
| `odoo-reporting-analysis` | QWeb/XLSX/pivot report analysis |
| `odoo-performance-guide` | Performance optimization |
| `odoo-performance-analysis` | Query optimization analysis |
| `odoo-integration-analysis` | External system integration |
| `odoo-testing-strategy` | Unit/integration/E2E testing strategy |
| `odoo-click-anywhere-test` | Run click_all test in Odoo |
| `odoo-password-update` | Update user password via Odoo Shell |
| `odoo-odoo-service` | Start/stop/restart Odoo server |
| `odoo-init` | Initialize new Odoo project |
| `odoo-base-understanding` | Deep understanding of Odoo code |
| `odoo-code-quality` | Code quality review |
| `odoo-restart-upgrade` | Restart & upgrade advisor |
| `odoo-user-context` | Step-by-step operation context |
| `odoo-uat-script-generator` | Generate UAT scripts |
| `odoo-debug-tdd` | TDD debugging workflow |
| `odoo-agent-teams-v2` | 5-agent workflow orchestration |
| `odoo-agent-teams-v3` | 5-agent testing & development |
| `odoo-agent-teams-fixing` | 5-agent fix workflow |

### AutoResearch (`autorel*`)

Background automation skills for vault documentation:

- `autorelog` — Show activity log
- `autorestart` — Restart running session
- `autorestatus` — Show current status and progress
- `autorestop` — Stop running session
- `autoverify` — Verify module documentation against code

### Version Control (`gitnexus-*`)

Git operations: `gitnexus-exploring`, `gitnexus-debugging`, `gitnexus-refactoring`, `gitnexus-impact-analysis`, `gitnexus-cli`, `gitnexus-guide`

### Development Workflows (`superpowers:*`)

Core workflows — invoke before any significant task:

- `superpowers:brainstorming` — Before creative work
- `superpowers:systematic-debugging` — When encountering bugs
- `superpowers:test-driven-development` — Before writing code
- `superpowers:writing-plans` — Before multi-step implementation
- `superpowers:executing-plans` — Execute written implementation plans
- `superpowers:subagent-driven-development` — Parallel agent execution
- `superpowers:odoo-sdd` — Odoo Spec-Driven Development

### Other Utilities

`mermaid-diagram`, `mcp-builder`, `artifacts-builder`, `theme-factory`, `webapp-testing`, `md-to-pdf`, `pdf`, `docx`, `pptx`, `xlsx`, `officecli`, `canvas-design`, `algorithmic-art`, `slack-gif-creator`, `skill-creator`

## Architecture

```
skill-name/
├── SKILL.md              # Main skill file (required)
└── [bundled files]       # Reference docs, scripts, themes (optional)
```

Each skill is a directory containing a `SKILL.md` file. Skills are invoked via slash commands (e.g., `/odoo19-model-new`).

## Odoo Context

**Always activate `odoo-vault-base-context` first** before working with Odoo:

```
Use /odoo-vault-base-context skill FIRST before any Odoo task.
```

## Migration Workflow

Odoo migration requires two separate skills:

1. `odoo-module-migration` — code syntax migration only (not semantics)
2. `odoo-db-migration` — database upgrade via upgrade.odoo.com
