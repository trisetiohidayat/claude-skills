# Odoo-Aware Assertions

Playwright-style assertions specifically for Odoo web client state. These wrap `eval` and `expect` in Odoo-semantic commands, making test assertions more readable and reliable.

---

## Why Odoo-Specific Assertions?

Standard Playwright assertions are generic. These know about Odoo's:
- State/status fields
- Notification system (toasts, warnings)
- Form dirty state
- Readonly field behavior
- Onchange/triggered compute behavior
- Chatter/mail thread

---

## Assertion Commands

### 1. Assert State Field Value

Verify a record's state/status field matches expected value without reading the DOM directly:

```bash
# Via page eval — check state indicator text
playwright-cli eval "() => {
  const badge = document.querySelector('.o_form_statusbar .o_statusbar_status .active');
  return badge ? badge.textContent.trim() : null;
}"

# Or via CSS — check status bar active state
playwright-cli eval "el => el.closest('.o_statusbar_status').querySelector('.active')?.textContent?.trim()" '.o_form_statusbar'

# Example assertion check
playwright-cli run-code "async page => {
  const badge = await page.evaluate(() => {
    const el = document.querySelector('.o_form_statusbar .o_statusbar_status .active');
    return el ? el.textContent.trim() : null;
  });
  console.assert(badge === 'Sale Order', \`Expected state: Sale Order, got: \${badge}\`);
}"
```

**Simpler pattern via `expect`:**
```bash
# Get state text
playwright-cli eval "el => el.querySelector('.active')?.textContent?.trim()" '.o_form_statusbar'
# Manual check: if output !== expected → fail the test
```

---

### 2. Assert Notification Appears

Check for success/error/toast notification after an action:

```bash
# Wait for notification (up to 5s), then check type
playwright-cli run-code "async page => {
  await page.waitForSelector('.o_notification', { timeout: 5000 }).catch(() => null);
  const notif = await page.evaluate(() => {
    const el = document.querySelector('.o_notification');
    if (!el) return null;
    const isError = el.classList.contains('o_error') || el.classList.contains('alert-danger');
    const isSuccess = el.classList.contains('o_success') || el.classList.contains('alert-success');
    return { text: el.textContent.trim(), isError, isSuccess };
  });
  if (!notif) throw new Error('No notification appeared');
  console.log('Notification:', notif);
}"
```

**Types to check:**
| Type | CSS Classes | Meaning |
|------|------------|---------|
| Success | `.alert-success`, `o_success` | Action completed OK |
| Error | `.alert-danger`, `o_error`, `.o_error` | Validation/system error |
| Warning | `.alert-warning` | Warning (e.g., record not found) |
| Info | `.alert-info` | Informational message |

---

### 3. Assert Field Readonly

Verify a field is truly non-editable:

```bash
playwright-cli eval "el => {
  const input = el.querySelector('input, textarea, select');
  return input ? input.readOnly || input.disabled : false;
}" '[name="amount_total"]'
```

---

### 4. Assert Form Dirty / Saved State

Detect whether a form has unsaved changes:

```bash
# Form is dirty (unsaved)
playwright-cli eval "() => !!document.querySelector('.o_form_dirty')"

# Form is clean (saved — no asterisks)
playwright-cli eval "() => !document.querySelector('.o_form_dirty')"

# Alternative: check title indicator
playwright-cli eval "() => document.title.includes('*')"
```

---

### 5. Assert Record Count in List

Check how many records are visible in list/kanban:

```bash
# List view row count
playwright-cli eval "() => document.querySelectorAll('tr.o_data_row').length"

# Kanban card count (all columns)
playwright-cli eval "() => document.querySelectorAll('.o_kanban_record').length"

# Kanban card count in specific column
playwright-cli eval "() => document.querySelectorAll('.o_kanban_group[data-id=\"1\"] .o_kanban_record').length"
```

---

### 6. Assert Required Field Validation Error

Trigger validation by attempting save, then check for red field highlights:

```bash
# Click save (should trigger validation)
playwright-cli click '[data-hotkey="s"]'

# Check for invalid fields
playwright-cli eval "() => {
  const invalid = document.querySelectorAll('.o_field_invalid');
  return invalid.length > 0
    ? invalid.map(el => el.closest('.o_field_widget')?.getAttribute(\"name\") || el.className)
    : [];
}"

# Get error messages
playwright-cli eval "() => {
  return [...document.querySelectorAll('.o_field_invalid')]
    .map(el => ({
      field: el.closest('.o_field_widget')?.getAttribute('name'),
      message: el.querySelector('.o_tooltip')?.textContent ||
               el.querySelector('.o_form_error')?.textContent ||
               el.title
    }));
}"
```

---

### 7. Assert Search Returns Results

Check search/filter returned records or "no results":

```bash
# Search
playwright-cli fill '.o_searchview_input' 'admin'
playwright-cli press Enter

# Check result count
playwright-cli eval "() => {
  const rows = document.querySelectorAll('tr.o_data_row');
  const cards = document.querySelectorAll('.o_kanban_record');
  const noResults = document.querySelector('.o_view_nocontent');
  return {
    listCount: rows.length,
    kanbanCount: cards.length,
    noContent: !!noResults
  };
}"
```

---

### 8. Assert Onchange/Compute Fired

Check that a field's value changed after a triggering field was filled:

```bash
# Fill triggering field
playwright-cli fill '[name="product_id"] input' 'CPU'

# Wait for autocomplete
playwright-cli wait-for-selector '.o-autocomplete--dropdown-item'
playwright-cli click '.o-autocomplete--dropdown-item:has-text("CPU")'

# Check computed field updated
playwright-cli eval "() => {
  const price = document.querySelector('[name=\"price_unit\"] input, [name=\"price_unit\"] .o_form_input');
  return price ? price.value : null;
}"
```

---

### 9. Assert Chatter Has Message

Verify a message was posted to the chatter:

```bash
# Post message
playwright-cli fill '.o_chatter .o_composer_input' 'Test follow-up note'
playwright-cli click '.o_chatter .o_composer_button_send'

# Wait and verify message appears
playwright-cli run-code "async page => {
  await page.waitForSelector('.o_chatter .o_message', { timeout: 3000 });
  const msgCount = await page.evaluate(() =>
    document.querySelectorAll('.o_chatter .o_message').length
  );
  console.assert(msgCount > 0, 'No message appeared in chatter');
}"
```

---

### 10. Assert Button State (Enabled/Disabled)

Check if an action button is clickable:

```bash
# Check confirm button is enabled
playwright-cli eval "el => {
  const btn = el.querySelector('[data-hotkey], .btn-primary');
  return btn && !btn.disabled && !btn.classList.contains('disabled');
}" '.o_form_statusbar'

# Check create button visibility
playwright-cli eval "() => {
  const create = document.querySelector('.o_list_button_add, .o-kanban-button-new');
  return create ? { visible: create.offsetParent !== null, disabled: create.disabled } : null;
}"
```

---

## Assertion Helper Script

For cleaner test files, save this as `odoo-assertions.js` in your project:

```javascript
// odoo-assertions.js — reusable Odoo assertion helpers

async function assertOdooState(page, expected) {
  const badge = await page.evaluate(() => {
    const el = document.querySelector('.o_form_statusbar .o_statusbar_status .active');
    return el ? el.textContent.trim() : null;
  });
  if (badge !== expected) {
    throw new Error(`State mismatch: expected "${expected}", got "${badge}"`);
  }
}

async function assertNotification(page, type = 'success', timeout = 5000) {
  await page.waitForSelector('.o_notification', { timeout });
  const notif = await page.evaluate((type) => {
    const el = document.querySelector('.o_notification');
    const classMap = {
      error: ['o_error', 'alert-danger'],
      success: ['o_success', 'alert-success'],
      warning: ['alert-warning']
    };
    const classes = classMap[type] || [];
    const match = classes.some(c => el.classList.contains(c));
    return { text: el.textContent.trim(), matched: match };
  }, type);
  if (!notif.matched) {
    throw new Error(`Expected ${type} notification, got: ${notif.text}`);
  }
}

async function assertFormClean(page) {
  const dirty = await page.evaluate(() => !!document.querySelector('.o_form_dirty'));
  if (dirty) throw new Error('Form has unsaved changes');
}

async function assertFieldReadonly(page, fieldName) {
  const readonly = await page.evaluate((name) => {
    const input = document.querySelector(`[name="${name}"] input, [name="${name}"] textarea, [name="${name}"] select`);
    return input ? input.readOnly || input.disabled : true;
  }, fieldName);
  if (!readonly) throw new Error(`Field "${fieldName}" should be readonly but is editable`);
}

module.exports = { assertOdooState, assertNotification, assertFormClean, assertFieldReadonly };
```

Usage in test:
```javascript
const { assertOdooState, assertNotification, assertFormClean } = require('./odoo-assertions');

test('confirm quotation', async ({ page }) => {
  await page.goto('http://localhost:8069/web#action=sale.action_quotations');
  await page.click('tr.o_data_row');
  await page.click('.o_form_statusbar .dropdown-toggle');
  await page.click('.o_menu_item:has-text("Confirm")');
  await assertNotification(page, 'success');
  await assertOdooState(page, 'Sale Order');
  await assertFormClean(page);
});
```

---

## Quick Reference Card

| What to Check | Command |
|---------------|---------|
| State field value | `eval ".o_form_statusbar .active" → text` |
| Success notification | `waitForSelector .o_notification + check .alert-success` |
| Error notification | `waitForSelector .o_notification + check .alert-danger` |
| Form dirty (unsaved) | `eval "() => !!document.querySelector('.o_form_dirty')"` |
| Record count (list) | `eval "() => document.querySelectorAll('tr.o_data_row').length"` |
| Record count (kanban) | `eval "() => document.querySelectorAll('.o_kanban_record').length"` |
| Field readonly | `eval "[name='f'] input" → readOnly` |
| Field has error | `eval "() => !!document.querySelector('.o_field_invalid')"` |
| No results empty state | `eval "() => !!document.querySelector('.o_view_nocontent')"` |
| Onchange computed | `eval "[name='price_unit'] input" → value` |
| Chatter has messages | `eval "() => document.querySelectorAll('.o_chatter .o_message').length > 0"` |
