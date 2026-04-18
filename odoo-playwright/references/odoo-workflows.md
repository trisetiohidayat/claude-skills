# Odoo-Specific Workflows

Step-by-step automation patterns for common Odoo tasks. Each workflow assumes you're already logged in and on the relevant page. If not, start with Login workflow first.

---

## 1. Login to Odoo

```bash
# Basic login — use name attributes (most stable)
playwright-cli open http://localhost:8069/web/login
playwright-cli fill '[name="login"]' 'admin'
playwright-cli fill '[name="password"]' 'admin'
playwright-cli click 'button[type="submit"]'

# Wait for redirect to web client
playwright-cli eval "() => window.location.pathname !== '/web/login'"
# Or just snapshot to confirm we're in
playwright-cli snapshot
```

**With session persistence** (faster for repeated runs):
```bash
# Save auth state after first login
playwright-cli open http://localhost:8069/web
# ... login manually or via script ...
playwright-cli state-save odoo-auth.json

# On next run, restore session
playwright-cli state-load odoo-auth.json
playwright-cli goto http://localhost:8069/web
```

---

## 2. Navigate via Menu

### By menu text (for unknown xmlid)

```bash
playwright-cli click '.o_menu_toggle'
playwright-cli click '.o_menu_item:has-text("Sales")'
# Wait for submenu to appear
playwright-cli click '.o_menu_item:has-text("Products")'
playwright-cli click '.o_menu_item:has-text("Product Variants")'
```

### By xmlid (when you know it)

```bash
playwright-cli click '[data-menu-xmlid="sale.menu_sales"]'
playwright-cli click '[data-menu-xmlid="sale.product_product_action"]'
```

### Direct URL (fastest, recommended for known actions)

```bash
# List view of a model
playwright-cli goto 'http://localhost:8069/web#action=stock.action_picking_type_list'

# Kanban view
playwright-cli goto 'http://localhost:8069/web#action=project.action_view_kanban'

# Form view — open specific record
playwright-cli goto 'http://localhost:8069/web#model=res.partner&id=42&view_type=form'
```

---

## 3. Create a New Record

### From list → form

```bash
# Click Create
playwright-cli click '.o_list_button_add'

# Fill required fields (tab between them)
playwright-cli fill '[name="name"] input' 'PT. example corp'
playwright-cli press Tab

# Many2one field
playwright-cli click '[name="country_id"] input'
playwright-cli fill '[name="country_id"] input' 'Indonesia'
playwright-cli click '.o-autocomplete--dropdown-item:has-text("Indonesia")'

# Selection field
playwright-cli click '[name="type"] select'
playwright-cli select '[name="type"] select' 'company'

# Checkbox
playwright-cli check '[name="active"]'

# Save
playwright-cli click '[data-hotkey="s"]'
```

### Quick create from kanban

```bash
playwright-cli click '.o-kanban-button-new'
playwright-cli fill '.o_kanban_quick_create input' 'Task Name'
playwright-cli click '.o_kanban_quick_create .o_kanban_add'
# Card appears in column
```

---

## 4. Edit an Existing Record

### From list, open in form

```bash
# Click row (opens form)
playwright-cli click 'tr.o_data_row[data-id="42"]'

# Or use action button in row
playwright-cli click 'tr.o_data_row[data-id="42"] .o_list_button_open'

# Make edits
playwright-cli.fill '[name="phone"] input' '+6281234567890'

# Save
playwright-cli click '[data-hotkey="s"]'
```

### Edit inline in list

```bash
playwright-cli dblclick 'tr.o_data_row[data-id="42"] td[name="name"]'
playwright-cli fill 'tr.o_data_row[data-id="42"] td[name="name"] input' 'New Name'
playwright-cli click '.o_list_button_save'
```

---

## 5. Search & Filter

### Basic search

```bash
playwright-cli click '.o_searchview_input'
playwright-cli fill '.o_searchview_input' 'search term'
playwright-cli press Enter
```

### Filter by value

```bash
# Open filter dropdown
playwright-cli click '.o_filter_menu .dropdown-toggle'

# Click specific filter
playwright-cli click '.o_dropdown_menu .o_menu_item:has-text("My Records")'
# OR click by text in dropdown
playwright-cli click '.o_menu_item:has-text("Draft")'
```

### Advanced filter (custom domain)

```bash
playwright-cli click '.o_filter_menu .dropdown-toggle'
playwright-cli click '.o_menu_item:has-text("Add Custom Filter")'

# Fill domain builder (simplified — may need snapshot to see fields)
playwright-cli snapshot
# Based on snapshot, fill the filter form
playwright-cli click '[name="field"] select'
playwright-cli select '[name="field"] select' 'state'
playwright-cli click '[name="operator"] select'
playwright-cli select '[name="operator"] select' '='
playwright-cli fill '[name="value"] input' 'sale'
playwright-cli click '[name="add"]'  # apply filter
```

### Clear filters

```bash
playwright-cli click '.o_searchview_facet .o_facet_remove'  # remove one
playwright-cli click '.o_searchview_clear'                   # clear all
```

---

## 6. Bulk Operations

### Select multiple rows → action

```bash
# Select rows via checkboxes
playwright-cli check 'tr.o_data_row[data-id="10"] .o_list_record_selector input'
playwright-cli check 'tr.o_data_row[data-id="11"] .o_list_record_selector input'
playwright-cli check 'tr.o_data_row[data-id="12"] .o_list_record_selector input'

# Open action menu
playwright-cli click '.o_list_button_action'
# OR
playwright-cli click '.o_cp_action_menus .dropdown-toggle'

# Select action
playwright-cli click '.o_menu_item:has-text("Delete")'
playwright-cli click '.modal .btn-danger'
```

### Select all (page-level)

```bash
playwright-cli click '.o_list_record_selector .o-checkbox'
# Wait for "Select all on page" to appear
playwright-cli click '.o_list_selection_box .o_list_select_all'
```

---

## 7. Change Stage / State

### Form view statusbar

```bash
playwright-cli click '.o_form_statusbar .dropdown-toggle'
playwright-cli click '.o_statusbar_buttons .o_menu_item:has-text("Confirm")'
# Wait for state update — toast notification appears
playwright-cli snapshot
```

### Kanban drag

```bash
# Drag card from column A to column B
playwright-cli drag '.o_kanban_record:has-text("Task 1")' '.o_kanban_group[data-id="2"]'
# Verify card moved
playwright-cli eval "el => document.querySelector('.o_kanban_group[data-id=\"2\"] .o_kanban_record:has-text(\"Task 1\")') ? 'moved' : 'not found'" eN
```

---

## 8. Wizard / Multi-step Dialog

```bash
# Open wizard (e.g., from action)
playwright-cli click '.o_menu_item:has-text("Register Payment")'
# Wait for modal
playwright-cli snapshot

# Step 1: Fill details
playwright-cli fill '.modal [name="amount"] input' '500000'
playwright-cli click '.modal [name="journal_id"] select'
playwright-cli select '.modal [name="journal_id"] select' 'Bank'

# Next step
playwright-cli click '.modal .btn-next'
playwright-cli snapshot  # see step 2

# Step 2: Confirm
playwright-cli click '.modal .btn-primary'
# Modal closes
```

---

## 9. Export from List

```bash
playwright-cli click '.o_cp_action_menus .dropdown-toggle'
playwright-cli click '.o_menu_item:has-text("Export")'
# Wait for export dialog
playwright-cli snapshot

# Select fields to export
playwright-cli click '.o_export_field[data-name="name"]'
playwright-cli click '.o_export_field[data-name="email"]'
playwright-cli click '.o_export_field[data-name="phone"]'

# Download
playwright-cli click '.modal .btn-primary'
# Browser downloads file — no further action needed
```

---

## 10. Run Odoo Click-anywhere Test

```bash
# Start Odoo in test mode with --test-click-anywhere
# Then use playwright-cli to interact

# Find the click_all test result
playwright-cli goto 'http://localhost:8069/web#action=web_ui.click_all_test_result'

# Inspect results
playwright-cli snapshot

# For detailed JS error log
playwright-cli click '.o_click_all_result:has-text("error")'
playwright-cli console error
playwright-cli network
```

---

## 11. Debugging Odoo UI

```bash
# Get JS console errors
playwright-cli console error

# Check network requests (XHR/fetch)
playwright-cli network

# Inspect element attributes
playwright-cli eval "el => JSON.stringify(el.dataset)" e5

# Get Odoo session info from page
playwright-cli eval "() => ({ uid: odoo.session_info.uid, db: odoo.session_info.db })"

# Check if web client is fully loaded
playwright-cli eval "() => document.querySelector('.o_backend_dashboard') ? 'ready' : 'loading'"


# Get CSRF token (needed for RPC)
playwright-cli eval "() => document.querySelector('html').dataset.csrf"
```

---

## 12. Handle Odoo-Specific Behaviors

### Wait for Odoo to finish RPC

```bash
# Odoo uses a loading indicator during RPC
# Wait for it to disappear
playwright-cli eval "() => document.querySelector('.o.loading') ? 'loading' : 'ready'"
# Or use run-code to wait
playwright-cli run-code "async page => { await page.waitForFunction(() => !document.querySelector('.o_loading'), { timeout: 10000 }); }"

# Alternative: wait for specific element to appear
playwright-cli eval "() => document.querySelector('.o_form_view') ? 'form ready' : 'not ready'"
```

### Handle confirmation dialogs (delete, unlink)

```bash
# Odoo often shows dialog before destructive actions
playwright-cli snapshot
# See dialog → confirm
playwright-cli click '.modal .btn-danger'
# Or dismiss
playwright-cli click '.modal .btn-secondary'
```

### Handle inline validation errors

```bash
# Field turned red (validation error) after save attempt
playwright-cli eval "el => el.closest('.o_form_view').querySelector('.o_field_invalid') ? 'has errors' : 'clean'" eN

# Get error message
playwright-cli eval "el => el.closest('.o_form_view').querySelector('.o_field_invalid')?.title || el.querySelector('.o_form_view .o_notification')?.textContent"
```

### Handle readonly fields

```bash
# Check if field is readonly
playwright-cli eval "el => el.querySelector('[name=\"id\"]')?.readOnly" eN
```

---

## Version-Specific Notes

| Scenario | Odoo 19 | Odoo 17/18 | Odoo 15 |
|----------|---------|------------|---------|
| Select menu class | `.o_select_menu_menu` | `.o_dropdown_menu` | `.dropdown-menu` |
| Many2one autocomplete | `.o-autocomplete--dropdown-item` | Similar | Different structure |
| Datepicker class | `.o_datepicker_picker` | Same | `.datepicker` |
| Form button save | `[data-hotkey="s"]` | Same | `.o_form_button_save` |

When version is unclear, snapshot once at the start and target from there.