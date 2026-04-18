---
name: odoo-playwright
description: Automate browser interactions in Odoo web client. Use this skill whenever user needs to interact with Odoo UI — fill forms, navigate menus, click list rows, use kanban boards, install modules, or any browser automation task in Odoo web interface. Trigger especially when user mentions Odoo, form views, list views, kanban, apps, modules, control panel, or search bar.
allowed-tools: Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*)
---

# Browser Automation for Odoo Web Client

## PREREQUISITE: Load Odoo Knowledge First

**BEFORE any action, ALWAYS activate `odoo-vault-base-analysis` skill first.**

This gives you the Odoo context + UI discovery patterns:

1. Activate `odoo-vault-base-analysis`
2. Load vault file: `Patterns/UI-Discovery-Patterns.md` — **THIS IS MANDATORY** for UI automation
3. Use `qmd__query` to search vault for the specific task
4. Extract the relevant knowledge (module structure, view patterns, state transitions)
5. Apply UI discovery patterns from the vault file
6. THEN execute browser automation using this skill

```
User: "uninstall module employee"
↓
Activate odoo-vault-base-analysis
↓ Load: Patterns/UI-Discovery-Patterns.md (dropdown pattern, dialog pattern)
↓ Load: Modules/ir.module.module.md (state transitions)
↓ qmd search: "button_immediate_uninstall"
↓ Discovery: dropdown → teleport → menu item → dialog
↓ Use this skill to execute
```

**CRITICAL: The vault `Patterns/UI-Discovery-Patterns.md` is the single source of truth for frontend UI patterns.** Read it FIRST before writing any automation code.

---

## Context Setup

**Before executing, ask user for Odoo context (if not provided):**

```
Odoo URL (contoh: http://localhost:8069):
Nama Database:
Username:
Password:
```

**Login flow:**

```bash
# Save context
cat > ~/.odoo-playwright-context.json << 'EOF'
{"url":"__URL__","db":"__DB__","login":"__USER__","password":"__PASS__"}
EOF

# Login
playwright-cli open __URL__/web/login
playwright-cli fill '[name="login"]' '__USER__'
playwright-cli fill '[name="password"]' '__PASS__'
playwright-cli click 'button[type="submit"]'

# Verify
playwright-cli eval "() => document.querySelector('.o_app_menu') ? 'OK' : 'FAIL'"
```

---

## Core Tool: playwright-cli

```bash
# Navigation
playwright-cli open <url>
playwright-cli goto <url>

# Interaction
playwright-cli click <selector>      # single match
playwright-cli fill <selector> <text> # input text
playwright-cli press Enter             # submit/search
playwright-cli type <text>            # type character by character
playwright-cli check <selector>       # checkbox
playwright-cli uncheck <selector>

# Inspection
playwright-cli snapshot               # full page tree
playwright-cli snapshot <selector>    # specific element
playwright-cli eval "<js>"            # run JS, return result

# Utility
playwright-cli screenshot              # capture page
playwright-cli close                   # close browser
```

---

## Decision Rules

### When CSS selectors fail

```bash
# Use eval to find and click by text content
playwright-cli eval "() => {
  const el = [...document.querySelectorAll('*')].find(
    e => e.textContent.includes('__TEXT__') && e.offsetParent !== null
  );
  if (el) { el.click(); return 'OK'; }
  return 'NOT_FOUND';
}"

# Find specific module card
playwright-cli eval "() => {
  const cards = document.querySelectorAll('.o_kanban_record');
  const target = [...cards].find(c => c.textContent.includes('__MODULE_DESC__'));
  if (target) {
    const btn = target.querySelector('button');
    if (btn) { btn.click(); return 'CLICKED'; }
  }
  return 'NOT_FOUND';
}"
```

### When multiple matches appear (strict mode error)

Odoo apps page often shows multiple cards with similar buttons. Use eval to target the **first match**:

```bash
# Never use: playwright-cli click 'button:has-text("Activate")'
# Instead:
playwright-cli eval "() => {
  const btns = [...document.querySelectorAll('button')].filter(b => b.textContent.includes('Activate'));
  if (btns[0]) { btns[0].click(); return 'CLICKED_FIRST'; }
  return 'NO_BUTTON';
}"
```

### After action, check state

```bash
# Check if page changed (install triggers redirect — this is NORMAL)
playwright-cli eval "() => ({
  url: window.location.href,
  title: document.title,
  bodyText: document.body.innerText.substring(0, 200)
})"
```

### Wait pattern for async operations

```bash
# Install takes time — wait then check
sleep 5
playwright-cli snapshot
```

---

## Verify Results

After install/navigate, always verify the **actual state** from page content, not from assumed behavior:

```bash
# Check module state via page content
playwright-cli eval "() => {
  const openBtn = document.querySelector('button[name=\"button_open_app\"]');
  const installBtn = document.querySelector('button[name=\"button_immediate_install\"]');
  const body = document.body.innerText;
  return {
    hasOpenApp: !!openBtn,
    hasInstall: !!installBtn,
    hasModuleMenu: body.includes('Employees') && body.includes('Departments')
  };
}"
```

---

## Vault Integration

**This skill provides TOOLS, not hardcoded workflows.**

For specific tasks, let vault guide you:

| Task | Vault Search | Discovery Pattern |
|------|-------------|-------------------|
| Install/Uninstall module | `"ir.module.module button_immediate_*"` | See `Patterns/UI-Discovery-Patterns.md` → Pattern 1 & 4 |
| Form view actions | `"odoo form view buttons save edit workflow"` | See `Patterns/UI-Discovery-Patterns.md` → Pattern 2 |
| List view operations | `"odoo list view actions create delete workflow"` | See `Patterns/UI-Discovery-Patterns.md` → Pattern 3 |
| Kanban operations | `"odoo kanban view drag drop card workflow"` | See `Patterns/UI-Discovery-Patterns.md` → Pattern 3 |
| Search/filter | `"odoo search view filter group by workflow"` | See `Patterns/UI-Discovery-Patterns.md` → Pattern 5 |
| Wizard/multi-step | `"odoo wizard multi step workflow"` | See `Patterns/UI-Discovery-Patterns.md` → Pattern 6 |

**Always read `Patterns/UI-Discovery-Patterns.md` FIRST** — it contains the algorithm for finding elements, not just the results.

**Workflow:**
1. Load `Patterns/UI-Discovery-Patterns.md` from vault
2. Apply the appropriate discovery pattern for the view type
3. Use `playwright-cli eval` to implement the pattern
4. Handle teleported dropdowns, dialogs, and async operations

---

## Reference Files

For detailed selector patterns and view-specific knowledge:

| File | Use When |
|------|----------|
| `references/odoo-selectors.md` | Need specific CSS selectors for a view |
| `references/odoo-assertions.md` | Need to verify Odoo-specific states |
| `references/running-code.md` | Need custom JS for complex interactions |
| `references/session-management.md` | Need to persist/load session |

---

## Snapshot Strategy

```bash
# Quick check — just the structure
playwright-cli snapshot

# Specific element — when you know what you need
playwright-cli snapshot '.o_form_view'

# After action — verify state changed
playwright-cli eval "() => window.location.href"
```