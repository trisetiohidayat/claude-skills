# Claude Code Skills Library

A collection of 180 Claude Code skills for Odoo 19 development, migration, operations, and general productivity.

## Quick Start

**Always activate these FIRST before Odoo work:**

```
/odoo-vault-base-analysis   # Provides Odoo running context (REQUIRED)
/odoo-running-context      # Step-by-step operation context
/odoo-environment-detector # Detect Odoo paths & config
```

## Skills by Category

---

### Odoo 19 Code Generation (`odoo19-*`)

80+ skills for generating Odoo 19 components. Trigger when user wants to create, extend, or migrate any Odoo component.

#### Models
| Skill | Purpose |
|-------|---------|
| [[odoo19-model-new]] | Generate new model class with `_name`, `_description` |
| [[odoo19-model-inherit]] | Extend existing model with new fields/methods |
| [[odoo19-model-transient]] | Create transient model for wizards |
| [[odoo19-model-abstract]] | Create reusable abstract mixin model |

#### Fields
| Skill | Purpose |
|-------|---------|
| [[odoo19-field-add]] | Add Char, Text, Html, Selection, Many2one, One2many, Many2many, Date, Datetime, Boolean, Integer, Float, Monetary, Binary, Image, Reference fields |
| [[odoo19-field-compute]] | Create computed field with `@api.depends` |
| [[odoo19-field-relational]] | Create Many2one, One2many, Many2many relational fields |
| [[odoo19-field-selection]] | Create Selection field with dropdown options |

#### Views (XML)
| Skill | Purpose |
|-------|---------|
| [[odoo19-view-form]] | Generate form view with sheet layout, groups, notebooks |
| [[odoo19-view-tree]] | Generate tree/list view with columns and decorations |
| [[odoo19-view-kanban]] | Generate kanban view with cards, progress bars, drag-drop |
| [[odoo19-view-search]] | Generate search view with filters, groupers, domains |
| [[odoo19-view-pivot]] | Generate pivot view for data analysis |
| [[odoo19-view-graph]] | Generate graph view (bar, line, pie) |
| [[odoo19-view-calendar]] | Generate calendar view with date fields and colors |
| [[odoo19-view-activity]] | Generate activity view for scheduling activities |
| [[odoo19-view-map]] | Generate map view with routing and locations |
| [[odoo19-view-coach]] | Generate dashboard/coach view with columns |

#### Business Logic
| Skill | Purpose |
|-------|---------|
| [[odoo19-method-action]] | Create action method triggered by button clicks |
| [[odoo19-method-onchange]] | Create `@api.onchange` method for field change handlers |
| [[odoo19-method-constraint]] | Create `@api.constrains` validation method |
| [[odoo19-flow-state]] | Create state machine workflow with transitions |
| [[odoo19-flow-approval]] | Create approval workflow with approval chain & notifications |
| [[odoo19-orm]] | Master ORM usage — deep API reference |

#### Controllers (HTTP)
| Skill | Purpose |
|-------|---------|
| [[odoo19-controller-new]] | Generate `http.Controller` class with route decorators |
| [[odoo19-controller-http]] | Generate HTTP endpoint with GET/POST, HTML rendering |
| [[odoo19-controller-json]] | Generate JSON API with CORS and authentication |

#### Reports
| Skill | Purpose |
|-------|---------|
| [[odoo19-report-qweb]] | Create QWeb report template with PDF generation |
| [[odoo19-report-xlsx]] | Create XLSX report using `report_xlsx` library |
| [[odoo19-web-template]] | Create QWeb template with template ID and XPath |

#### Security
| Skill | Purpose |
|-------|---------|
| [[odoo19-security-group]] | Create `res.groups` XML for access groups |
| [[odoo19-security-rule]] | Create `ir.rule` XML with domain restrictions |
| [[odoo19-security-field]] | Create field-level permissions using `groups` parameter |
| [[odoo19-security-xml]] | Create `ir.model.access.csv` ACL file |

#### Automation
| Skill | Purpose |
|-------|---------|
| [[odoo19-automation-cron]] | Create `ir.cron` scheduled task |
| [[odoo19-automation-server-action]] | Create `ir.actions.server` for workflows |
| [[odoo19-menu-item]] | Create `ir.ui.menu` with parent and action |
| [[odoo19-action-window]] | Create `ir.actions.act_window` for opening models |

#### Migration (Older versions → Odoo 19)
| Skill | Purpose |
|-------|---------|
| [[odoo19-migrate-model]] | Migrate model code to Odoo 19 syntax |
| [[odoo19-migrate-view]] | Migrate view XML to Odoo 19 format |
| [[odoo19-migrate-manifest]] | Migrate `__manifest__.py` to Odoo 19 |

#### Modules
| Skill | Purpose |
|-------|---------|
| [[odoo19-module-new]] | Create new module with full structure |
| [[odoo19-module-addon]] | Create addon with controllers, static, wizard dirs |

#### Data
| Skill | Purpose |
|-------|---------|
| [[odoo19-data-xml]] | Create data XML with record elements and `ref()` |
| [[odoo19-data-demo]] | Create demo XML with `noupdate` flags |

#### Web Assets
| Skill | Purpose |
|-------|---------|
| [[odoo19-web-assets]] | Create `web.assets.xml` with JS/CSS bundles |
| [[odoo19-web-widget]] | Create custom web widget extending field widgets |

#### Wizards
| Skill | Purpose |
|-------|---------|
| [[odoo19-wizard-new]] | Create complete wizard with transient model and form |
| [[odoo19-wizard-confirm]] | Create simple Yes/No confirmation wizard |

#### Tests
| Skill | Purpose |
|-------|---------|
| [[odoo19-test-unit]] | Create `TransactionCase` unit test classes |
| [[odoo19-test-portal]] | Create portal tour tests with browser automation |

#### Utilities
| Skill | Purpose |
|-------|---------|
| [[odoo19-utils-logging]] | Add `_logger` logging to models |
| [[odoo19-utils-translate]] | Add i18n translations with `_()` |
| [[odoo19-utils-validation]] | Create email, phone, URL validation helpers |

#### Domain-Specific Models
| Skill | Purpose |
|-------|---------|
| [[odoo19-hr-employee]] | Create HR Employee management model |
| [[odoo19-hr-timesheet]] | Create HR Timesheet tracking model |
| [[odoo19-project-task]] | Create Project Task management model |
| [[odoo19-stock-picking]] | Create Stock Picking/Delivery order model |
| [[odoo19-account-invoice]] | Create Invoice management model |
| [[odoo19-mrp-bom]] | Create MRP Bill of Materials model |
| [[odoo19-pos-config]] | Create POS configuration model |
| [[odoo19-website-sale]] | Create e-commerce/Website Sale model |
| [[odoo19-event-manage]] | Create Event Management model |
| [[odoo19-survey-create]] | Create Survey/Quiz model |
| [[odoo19-export-import]] | Export/import data to Excel |

#### API & Integration
| Skill | Purpose |
|-------|---------|
| [[odoo19-api-rest]] | Create REST API with authentication and JSON |
| [[odoo19-api-external]] | Create external API integration (OAuth/API key) |

---

### Odoo Analysis & Operations (`odoo-*`)

#### Context & Environment
| Skill | Purpose |
|-------|---------|
| [[odoo-vault-base-analysis]] | **ALWAYS activate first** — provides Odoo running context |
| [[odoo-running-context]] | Step-by-step operation context |
| [[odoo-environment-detector]] | Detect Odoo paths and configuration |
| [[odoo-environment]] | Check/verify Odoo environment and setup |
| [[odoo-path-resolver]] | Resolve Odoo paths and `odoo.conf` files |
| [[odoo-init]] | Initialize new Odoo project with version selection |

#### Odoo Service & Process
| Skill | Purpose |
|-------|---------|
| [[odoo-odoo-service]] | Start/stop/restart Odoo service/daemon |
| [[odoo-restart-upgrade]] | Advisor: when to restart server or upgrade module |

#### Database Management
| Skill | Purpose |
|-------|---------|
| [[odoo-db-management]] | Database backup/restore/duplicate/clone |
| [[odoo-db-create]] | Create new database via Odoo method |
| [[odoo-db-restore]] | Restore database from SQL dump |
| [[odoo-db-migration]] | Database upgrade via upgrade.odoo.com |

#### Module Management
| Skill | Purpose |
|-------|---------|
| [[odoo-module-install]] | Install/upgrade/uninstall modules via CLI |
| [[odoo-module-test]] | Test modules comprehensively |
| [[odoo-module-fixing]] | Manual bug fix — **does not stop until resolved** |
| [[odoo-module-migration]] | Code syntax migration between versions |
| [[odoo-module-structure]] | Understand and design module architecture |

#### Rust MCP
| Skill | Purpose |
|-------|---------|
| [[odoo-rust-mcp-setup]] | Auto-setup Odoo MCP by detecting config |
| [[odoo-rust-mcp-list]] | List all registered Odoo MCP instances |
| [[odoo-rust-mcp-restart]] | Restart rust-mcp Odoo MCP server |

#### Password & User
| Skill | Purpose |
|-------|---------|
| [[odoo-password-update]] | Update user password via Odoo Shell |
| [[odoo-password-update-by-id]] | Update password by user ID |
| [[odoo-password-update-by-id-2]] | Update password for user ID=2 |
| [[odoo-reset-main-user]] | Reset `main_user` (ID=2) password to "admin" |

#### Analysis Skills (trigger anytime)
| Skill | Purpose |
|-------|---------|
| [[odoo-architect]] | Architecture analysis and planning |
| [[odoo-architecture-analysis]] | Modular architecture analysis |
| [[odoo-base-understanding]] | Deep understanding of Odoo internals |
| [[odoo-business-process]] | Understand Odoo business processes |
| [[odoo-workflow-analysis]] | State machine and approval flow analysis |
| [[odoo-data-model-analysis]] | Model relationships and field analysis |
| [[odoo-migration-analysis]] | Migration analysis between versions |
| [[odoo-cross-module-analysis]] | Module dependencies and integration analysis |
| [[odoo-security-analysis]] | Security mechanism analysis |
| [[odoo-security-review]] | Security review and vulnerability checklist |
| [[odoo-error-analysis]] | Systematic error analysis and root cause |
| [[odoo-investigate-before-fix]] | Debug before applying fixes |
| [[odoo-debug-tdd]] | TDD debugging workflow |
| [[odoo-reporting-analysis]] | QWeb/XLSX/pivot report analysis |
| [[odoo-performance-guide]] | Performance optimization guide |
| [[odoo-performance-analysis]] | Query optimization and N+1 analysis |
| [[odoo-integration-analysis]] | External system integration analysis |
| [[odoo-testing-strategy]] | Unit/integration/E2E testing strategy |
| [[odoo-code-quality]] | Code quality review and best practices |
| [[odoo-reporting-analysis]] | Reporting systems analysis |

#### Automation & UI
| Skill | Purpose |
|-------|---------|
| [[odoo-click-anywhere-test]] | Run `click_all` test in Odoo |
| [[odoo-ui-automation]] | Automate Odoo UI interactions |
| [[odoo-uat-script-generator]] | Generate UAT test scripts |
| [[odoo-manual-writer]] | Create user manual with auto screenshots |

#### Vault Documentation
| Skill | Purpose |
|-------|---------|
| [[odoo-vault-analysis]] | Build and fix vault documentation |
| [[odoo-vault-researcher]] | Autonomous documentation researcher |
| [[odoo-custom-module-docs]] | Create comprehensive module documentation |

#### Data & Sync
| Skill | Purpose |
|-------|---------|
| [[odoo-data-sync-xlsx]] | Export/import data to Excel |
| [[odoo-orm-sync]] | Sync Odoo data between databases |
| [[odoo-migration-data-audit]] | Data audit between Odoo v15 and v19 |
| [[odoo-migration-data-sync]] | Compare and sync data between databases |
| [[odoo-migration-findings]] | Document migration findings |

#### Agent Teams
| Skill | Purpose |
|-------|---------|
| [[odoo-agent-teams-v2]] | 5-agent workflow orchestration (session-scoped) |
| [[odoo-agent-teams-v3]] | 5-agent testing & development (v3 — current) |
| [[odoo-agent-teams-fixing]] | 5-agent fix workflow |

---

### AutoResearch (`autorel*`)

Autonomous vault documentation compounding loop.

| Skill | Purpose |
|-------|---------|
| [[autoresearch]] | Autonomous knowledge compounding loop |
| [[autorelog]] | Show AutoResearch activity log |
| [[autorestart]] | Restart running session |
| [[autorestatus]] | Show current status and progress |
| [[autorestop]] | Stop running session gracefully |
| [[autoverify]] | Verify module docs against code |

---

### Version Control (`gitnexus-*`)

Git operations powered by GitNexus knowledge graph.

| Skill | Purpose |
|-------|---------|
| [[gitnexus-exploring]] | Explore code, understand architecture |
| [[gitnexus-debugging]] | Debug bugs, trace errors |
| [[gitnexus-refactoring]] | Safe rename, extract, move, restructure |
| [[gitnexus-impact-analysis]] | Safety analysis — what will break |
| [[gitnexus-cli]] | Run GitNexus CLI commands |
| [[gitnexus-guide]] | GitNexus tools and workflow reference |

| Skill | Purpose |
|-------|---------|
| [[git-commit-multi]] | Commit across multiple repos with smart grouping |
| [[git-commit-odoo]] | Commit Odoo addon repos, one commit per module |
| [[commit-staged-push]] | Git workflow: commit staged changes and push |

---

### Development Workflows (`superpowers:*`)

Core cognitive workflows — **invoke before significant tasks.**

| Skill | Purpose | When |
|-------|---------|------|
| [[superpowers:brainstorming]] | Turn ideas into designs | Before creative/implementation work |
| [[superpowers:systematic-debugging]] | Root cause analysis | Any bug, error, or failure |
| [[superpowers:test-driven-development]] | TDD workflow | Before writing any code |
| [[superpowers:writing-plans]] | Write implementation plan | Before multi-step work |
| [[superpowers:executing-plans]] | Execute written plans | After writing-plans |
| [[superpowers:subagent-driven-development]] | Parallel agent orchestration | 2+ independent tasks |
| [[superpowers:odoo-sdd]] | Odoo Spec-Driven Development | Odoo development projects |
| [[superpowers:odoo-custom-docs]] | Create comprehensive Odoo docs | Module documentation |
| [[superpowers:receiving-code-review]] | Process code review feedback | After code review |
| [[superpowers:requesting-code-review]] | Request peer review | Before merging |
| [[superpowers:finishing-a-development-branch]] | Wrap up feature branch | Before PR |
| [[superpowers:verification-before-completion]] | Verify task completion | Before claiming done |
| [[superpowers:using-git-worktrees]] | Worktree isolation | Isolated feature work |
| [[superpowers:writing-skills]] | Create/modify skills | Skill development |

---

### Office Documents

| Skill | Purpose |
|-------|---------|
| [[docx]] | Create, read, edit Word `.docx` documents |
| [[xlsx]] | Excel XLSX operations |
| [[pptx]] | Create, edit PowerPoint `.pptx` |
| [[officecli]] | Office docs via officecli CLI |
| [[pdf]] | PDF: read, merge, split, watermark, OCR |
| [[md-to-pdf]] | Convert Markdown to PDF |
| [[md-to-pdf-pro]] | Advanced Markdown to PDF |
| [[marp-slides]] | Create Marp slide presentations |

---

### Web & Browser

| Skill | Purpose |
|-------|---------|
| [[playwright-cli]] | Automate browser interactions, test web pages |
| [[playwright-cli-odoo]] | Automate Odoo UI with CSS selectors |
| [[browser-use]] | Browser automation for testing and scraping |
| [[webapp-testing]] | Test local web apps with Playwright |
| [[web-artifacts-builder]] | Complex React/Tailwind/shadcn artifacts |
| [[webfetch-guide]] | Web content fetching guide |

---

### Design & Visual

| Skill | Purpose |
|-------|---------|
| [[frontend-design]] | Production-grade frontend interfaces |
| [[canvas-design]] | Canvas compositions and layouts |
| [[theme-factory]] | Apply themes to slides, docs, artifacts |
| [[brand-guidelines]] | Anthropic brand colors and typography |
| [[mermaid-diagram]] | Generate Mermaid diagrams |

---

### AI & Art

| Skill | Purpose |
|-------|---------|
| [[claude-api]] | Build apps with Claude API/SDK |
| [[algorithmic-art]] | Generative art with p5.js |
| [[slack-gif-creator]] | Create animated GIFs for Slack |
| [[artifacts-builder]] | Complex multi-component HTML artifacts |

---

### Productivity & Utilities

| Skill | Purpose |
|-------|---------|
| [[skill-creator]] | Create, modify, evaluate skills |
| [[find-skills]] | Discover and install skills |
| [[mcp-builder]] | Build MCP servers (Python/Node) |
| [[tree-view]] | Display directory tree structure |
| [[deepdive]] | One-shot deep research session |
| [[crawl4ai]] | Crawl and scrape web pages |
| [[caveman]] | Ultra-compressed communication mode |
| [[caveman-compress]] | Compress memory files |
| [[llm-wiki]] | Personal LLM Wiki — compounding knowledge |
| [[llm-wiki-base-analysis]] | LLM Wiki analysis skill |
| [[postgres-kill-idle]] | Kill PostgreSQL idle connections |
| [[cmux-control]] | Control tmux multiplexer |
| [[doc-coauthoring]] | Internal communications writing |
| [[internal-comms]] | Company communication templates |
| [[commit-staged-push]] | Git commit staged and push |
| [[claude-md-hallucination]] | Add hallucination awareness to CLAUDE.md |

---

## Architecture

```
skill-name/
├── SKILL.md              # Main skill file (required)
└── [bundled files]       # Reference docs, scripts (optional)
```

Skills are invoked via slash commands (e.g., `/odoo19-model-new`).

## Migration Workflow

Odoo migration requires **two separate skills**:

1. [[odoo-module-migration]] — code syntax migration (not semantics)
2. [[odoo-db-migration]] — database upgrade via upgrade.odoo.com
