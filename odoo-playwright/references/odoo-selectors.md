# Odoo Web UI Selector Reference

Complete reference of CSS classes, data attributes, and role patterns for reliable Odoo element targeting. Use these selectors instead of generic snapshot refs to minimize token usage and improve stability.

---

## Form View Selectors

### Buttons (form header)

| Action | CSS Selector | Notes |
|--------|-------------|-------|
| Save | `[data-hotkey="s"]` | Preferred — works even if CSS changes |
| Save (alt) | `.o_form_button_save` | Fallback |
| Discard | `[data-hotkey="j"]` | Default hotkey for discard |
| Create | `[data-hotkey="c"]` | New record from form |
| Delete | `.o_form_button_remove` | May trigger confirmation dialog |

```bash
playwright-cli click '[data-hotkey="s"]'   # Save
playwright-cli click '[data-hotkey="j"]'   # Discard
playwright-cli click '[data-hotkey="c"]'   # Create new
```

### Form Fields

Field containers have `name` attribute matching the model field name. Always prefer `[name="field_name"]` over generic CSS classes.

```bash
# Char field
playwright-cli fill '[name="name"] input' 'John Doe'
playwright-cli fill '[name="email"]' 'john@example.com'

# Text field (many lines)
playwright-cli fill '[name="description"] textarea' 'Long description here'

# Integer / Float
playwright-cli fill '[name="quantity"] input' '10'
playwright-cli fill '[name="list_price"] input' '150000'

# Date field — click picker input, then pick from calendar
playwright-cli click '[name="date_order"] .o_datepicker_input'
playwright-cli click '.o_datepicker_picker td[data-date="2026-04-17"]:not(.o_datepicker_weekend)'

# Datetime field
playwright-cli click '[name="date_deadline"] .o_datepicker_input'
# Select date tab first
playwright-cli click '.o_datepicker .nav-item:has-text("Date")'
playwright-cli click '.o_datepicker_picker td[data-date="2026-04-17"]'
# Then time
playwright-cli click '.o_datepicker .nav-item:has-text("Time")'
playwright-cli click '.o_datepicker .time-picker input[name="hours"]'
playwright-cli type '14'
playwright-cli click '.o_datepicker .time-picker input[name="minutes"]'
playwright-cli type '30'

# Boolean / Checkbox
playwright-cli check '[name="active"]'
playwright-cli uncheck '[name="active"]'

# Binary (file upload)
playwright-cli upload '[name="binary_field"] input[type="file"]' ./document.pdf

# HTML field (inline editor)
playwright-cli click '[name="description"] .odoo-editor-editable'
playwright-cli type 'Description text'
```

### Selection / Dropdown Fields

```bash
# Standard select (selection field, many2one rendered as select)
playwright-cli click '[name="state"] select'
playwright-cli select '[name="state"] select' 'draft'
# OR click option
playwright-cli click '[name="state"] option[value="draft"]'

# Many2one with autocomplete dropdown
playwright-cli click '[name="partner_id"] input'
playwright-cli fill '[name="partner_id"] input' 'Admin'
playwright-cli click '.o-autocomplete--dropdown-item:has-text("Administrator")'

# Many2one with selection modal (for complex relations)
# May open a modal dialog — handle with modal selectors
playwright-cli click '[name="user_id"] .o_external_button'
```

### Relational Fields (One2many, Many2many)

```bash
# One2many: embedded list inside form — add new line
playwright-cli click '.o_field_one2many .o_list_button_add'
playwright-cli fill '.o_field_one2many tr.o_data_row:first-child [name="product_id"] input' 'Product A'

# Many2many tags — click tag to remove, click + to add
playwright-cli click '[name="tag_ids"] .o_tag:has-text("VIP")'      # remove tag
playwright-cli click '[name="tag_ids"] .o_tag_add'                     # add tag
playwright-cli fill '[name="tag_ids"] .o_tag_input' 'New Tag'
playwright-cli press Enter
```

### Form Status / Stage Indicator

```bash
# Stage badge in header (e.g., Sale Order state)
playwright-cli click '.o_form_statusbar .dropdown-toggle'
playwright-cli click '.o_statusbar_buttons .o_dropdown_menu .o_menu_item:has-text("Confirm")'
```

---

## List View Selectors

### Record Rows

| Action | Selector |
|--------|---------|
| Row by ID | `tr.o_data_row[data-id="42"]` |
| Cell by field | `tr.o_data_row[data-id="42"] td[name="display_name"]` |
| View button in row | `tr.o_data_row[data-id="42"] .o_list_button_open` |
| Edit button in row | `tr.o_data_row[data-id="42"] .o_list_button_edit` |
| Delete button in row | `tr.o_data_row[data-id="42"] .o_list_record_remove` |
| Row checkbox | `tr.o_data_row[data-id="42"] .o_list_record_selector input` |

```bash
# Open record in form view
playwright-cli click 'tr.o_data_row[data-id="42"]'
playwright-cli click 'tr.o_data_row[data-id="42"] td[name="name"]'

# Open via view button
playwright-cli click 'tr.o_data_row[data-id="42"] .o_list_button_open'

# Select row for bulk action
playwright-cli check 'tr.o_data_row[data-id="42"] .o_list_record_selector input'

# Delete row (from list)
playwright-cli click 'tr.o_data_row[data-id="42"] .o_list_record_remove'

# Edit row inline (list editable)
playwright-cli dblclick 'tr.o_data_row[data-id="42"] td[name="name"]'
playwright-cli fill 'tr.o_data_row[data-id="42"] td[name="name"] input' 'New Name'
playwright-cli click '.o_list_button_save'
```

### List Header / Controls

```bash
# Create new record
playwright-cli click '.o_list_button_add'

# Save / discard inline edits
playwright-cli click '.o_list_button_save'
playwright-cli click '.o_list_button_discard'

# Resize column (drag)
playwright-cli mousemove 500 200
playwright-cli mousedown
playwright-cli mousemove 600 200
playwright-cli mouseup

# Sort column (click header)
playwright-cli click 'th[name="name"]:has-text("Name")'
playwright-cli click 'th[name="name"].o-column-sortable'  # if already sorted

# Toggle column visibility
playwright-cli click '.o_list_settings'
playwright-cli click '.o_switch_monetary .btn'  # example toggle
```

### Pagination

```bash
# Next page
playwright-cli click '.o_pager_next'
# Previous
playwright-cli click '.o_pager_previous'
# Go to specific page — click the page number
playwright-cli click '.o_pager_value'

# Change page size (rows per page)
playwright-cli click '.o_pager_limit select'  # if dropdown
# OR click edit icon on pager
playwright-cli click '.o_pager_value .fa-pencil'
playwright-cli fill '.o_pager_value input' '100'
playwright-cli press Enter
```

---

## Kanban View Selectors

### Cards & Columns

| Element | Selector |
|---------|---------|
| Card by text | `.o_kanban_record:has-text("Record Name")` |
| Card by ID | `.o_kanban_record[data-id="42"]` |
| Card in column | `.o_kanban_group[data-id="1"] .o_kanban_record:has-text("Task")` |
| Column | `.o_kanban_group[data-id="1"]` |
| Quick add button | `.o-kanban-button-new` |
| Quick create input | `.o_kanban_quick_create input` |
| Quick create submit | `.o_kanban_quick_create .o_kanban_add` |
| Load more | `.o_kanban_load_more` |
| Edit card button | `.o_kanban_record:has-text("Name") .o_kanban_edit` |
| Delete card button | `.o_kanban_record:has-text("Name") .o_kanban_delete` |

```bash
# Open a card
playwright-cli click '.o_kanban_record:has-text("SO001")'

# Quick create in column
playwright-cli click '.o-kanban-button-new'
playwright-cli fill '.o_kanban_quick_create input' 'New Task'
playwright-cli click '.o_kanban_quick_create .o_kanban_add'

# Open card in edit mode
playwright-cli click '.o_kanban_record:has-text("Task A") .o_kanban_edit'
playwright-cli fill '.o_kanban_record:has-text("Task A") input[name="name"]' 'Updated'
playwright-cli click '.o_kanban_record:has-text("Task A") .o_kanban_save'
```

### Kanban Color / Progress Indicators

```bash
# Colored status bar on card (stage-based)
playwright-cli eval "el => el.closest('.o_kanban_record').querySelector('.o_kanban_color_5')" e5

# Progress bar inside card
playwright-cli click '.o_kanban_record:has-text("Task A") .o_progressbar .progress-bar'
```

---

## Calendar View

### Elements

| Element | Selector |
|---------|---------|
| Day cell | `.o_calendar_view .o_calendar_day` |
| Week cell | `.o_calendar_view .o_calendar_week` |
| Month cell | `.o_calendar_view .fc-daygrid-day` |
| Event block | `.o_calendar_event` |
| Event by title | `.o_calendar_event:has-text("Meeting with Client")` |
| Today highlight | `.o_calendar_view .o_calendar_today` |
| Navigation arrows | `.o_calendar_view .fc-button-primary` |
| View mode buttons | `.o_calendar_view .fc-button:has-text("Week")` |

### Navigation

```bash
# Switch to Day / Week / Month / Agenda view
playwright-cli click '.o_calendar_view .fc-button:has-text("Day")'
playwright-cli click '.o_calendar_view .fc-button:has-text("Week")'
playwright-cli click '.o_calendar_view .fc-button:has-text("Month")'
playwright-cli click '.o_calendar_view .fc-button:has-text("Agenda")'

# Navigate to next / previous period
playwright-cli click '.o_calendar_view .fc-button:has-text("Next")'
playwright-cli click '.o_calendar_view .fc-button:has-text("Prev")'
playwright-cli click '.o_calendar_view .fc-button:has-text("Today")'

# Jump to specific date (via datepicker)
playwright-cli click '.o_calendar_view .o_datepicker_input'
playwright-cli click '.o_datepicker_picker td[data-date="2026-04-20"]'
```

### Events

```bash
# Click an event to open its form
playwright-cli click '.o_calendar_event:has-text("Weekly Review")'

# Create event via quick create (click on empty day slot)
playwright-cli click '.o_calendar_view .fc-daygrid-day[data-date="2026-04-20"]'
playwright-cli fill '.o_calendar_view .o_calendar_quick_create input' 'New Event'
playwright-cli press Enter

# Open full create form (right-click or long press on empty slot)
playwright-cli click '.o_calendar_view .fc-daygrid-day[data-date="2026-04-20"]'
playwright-cli click '.o_calendar_view .o_calendar_more'

# Delete an event (open first, then delete)
playwright-cli click '.o_calendar_event:has-text("Event A")'
playwright-cli click '.o_form_button_remove'
playwright-cli click '.modal .btn-danger'
```

---

## Pivot View

### Elements

| Element | Selector |
|---------|---------|
| Pivot table | `.o_pivot` |
| Cell value | `.o_pivot .o_pivot_cell[data-type="number"]` |
| Total row/col | `.o_pivot .o_pivot_cell[data-type="total"]` |
| Expand button | `.o_pivot .o_pivot_cell .fa-plus` |
| Collapse button | `.o_pivot .o_pivot_cell .fa-minus` |
| Measure dropdown | `.o_pivot .o_measure .dropdown-toggle` |
| Attribute dropdown | `.o_pivot .o_filter .dropdown-toggle` |
| Export button | `.o_pivot .o_pivot_export .btn` |

### Operations

```bash
# Expand a cell (drill down)
playwright-cli click '.o_pivot .o_pivot_cell:nth-child(3) .fa-plus'

# Collapse a cell
playwright-cli click '.o_pivot .o_pivot_cell:nth-child(3) .fa-minus'

# Switch measure (e.g., from "Quantity" to "Revenue")
playwright-cli click '.o_pivot .o_measure .dropdown-toggle'
playwright-cli click '.o_pivot .o_measure .o_menu_item:has-text("Revenue")'

# Add attribute/grouping
playwright-cli click '.o_pivot .o_filter .dropdown-toggle'
playwright-cli click '.o_pivot .o_filter .o_menu_item:has-text("Sales Person")'

# Export pivot to xlsx
playwright-cli click '.o_pivot .o_pivot_export .btn'
playwright-cli click '.o_menu_item:has-text("Export to XLSX")'
```

---

## Graph View

### Elements

| Element | Selector |
|---------|---------|
| Graph container | `.o_graph_view` |
| Bar/Line/Pie toggle | `.o_graph_view .o_graph_buttons .btn` |
| Legend item | `.o_graph_view .o_graph_legend .o_legend_item` |
| Axis label | `.o_graph_view .o_graph_axis_label` |

### Operations

```bash
# Switch view type
playwright-cli click '.o_graph_view .o_graph_buttons .btn:has-text("Bar")'
playwright-cli click '.o_graph_view .o_graph_buttons .btn:has-text("Line")'
playwright-cli click '.o_graph_view .o_graph_buttons .btn:has-text("Pie")'

# Click legend item to toggle visibility
playwright-cli click '.o_graph_view .o_graph_legend .o_legend_item:has-text("Revenue")'

# Click on a bar/slice to drill down
playwright-cli click '.o_graph_view .o_graph_renderer rect[data-index="2"]'
# OR via JS if chart is canvas-based
playwright-cli run-code "async page => { const canvas = page.locator('.o_graph_view canvas'); await canvas.click({ position: { x: 100, y: 50 } }); }"
```

---

## Inline Editable List (Tab/Enter Flow)

Odoo list views with `edit="inline"` let you tab through cells and type directly.

```bash
# Start editing — double-click the cell
playwright-cli dblclick 'tr.o_data_row[data-id="42"] td[name="name"]'
# Cell becomes editable (input appears inside td)

# Type new value
playwright-cli type 'Updated Name'

# Move to next cell with Tab, save with Enter
playwright-cli press Tab          # move to next column
playwright-cli type 'New Value'
playwright-cli press Enter        # save all changes
playwright-cli press Escape       # or discard with Escape

# Discard all inline changes
playwright-cli click '.o_list_button_discard'
```

**Field targeting in editable list:**

```bash
# Each cell gets an input when editable
playwright-cli dblclick 'tr.o_data_row[data-id="42"] td[name="street"]'
playwright-cli fill 'tr.o_data_row[data-id="42"] td[name="street"] input' '123 Main St'
playwright-cli press Tab

# Boolean cell in list (click to toggle)
playwright-cli click 'tr.o_data_row[data-id="42"] td[name="active"] input'
```

---

## Email Composer

### Elements (mail.ComposeMessage)

| Element | Selector |
|---------|---------|
| Recipient input | `[name="partner_ids"] input` |
| CC field | `.o_mailComposer .o_composer_secondary_recipients` |
| Subject | `[name="subject"] input` |
| Body (rich text) | `.o_mailComposer .o_mail_editor .odoo-editor-editable` |
| Attachment button | `.o_mailComposer .o_attachment_button` |
| Send button | `.o_mailComposer .o_mail_send` |
| Save draft | `.o_mailComposer .o_mail_discard` |

### Operations

```bash
# Open composer (from mail.message or res.partner)
playwright-cli click 'button:has-text("Send Email")'
# OR from action
playwright-cli click '.o_mailComposer .btn-primary'

# Add recipient (many2one email field)
playwright-cli fill '[name="partner_ids"] input' 'admin@example.com'
playwright-cli click '.o-autocomplete--dropdown-item:has-text("admin@example.com")'
# Add more recipients
playwright-cli press Enter
playwright-cli fill '[name="partner_ids"] input' 'user@example.com'
playwright-cli click '.o-autocomplete--dropdown-item:has-text("user@example.com")'
playwright-cli press Enter

# Fill subject
playwright-cli fill '[name="subject"] input' 'Regarding Invoice #INV-001'

# Type in rich text body
playwright-cli click '.o_mailComposer .o_mail_editor .odoo-editor-editable'
playwright-cli type 'Dear Sir/Madam,\n\nPlease find attached...'

# Attach a file
playwright-cli click '.o_mailComposer .o_attachment_button'
playwright-cli upload '.o_mailComposer input[type="file"]' ./invoice.pdf
# Wait for attachment chip to appear
playwright-cli click '.o_attachment[data-filename="invoice.pdf"]'

# Send
playwright-cli click '.o_mailComposer .o_mail_send'

# Or save as draft
playwright-cli click '.o_mailComposer .o_mail_discard'
```

---

## Kanban Drag and Drop

Odoo's kanban drag-drop requires specific positioning since kanban columns often render as scrollable containers.

```bash
# Get card position
playwright-cli eval "el => { const card = document.querySelector('.o_kanban_record:has-text(\"Task 1\")'); const rect = card.getBoundingClientRect(); return { x: rect.x, y: rect.y, width: rect.width, height: rect.height }; }" eN

# Get target column position
playwright-cli eval "el => { const col = document.querySelectorAll('.o_kanban_group')[1]; const rect = col.getBoundingClientRect(); return { x: rect.x, y: rect.y }; }" eN

# Drag using mousemove sequence (Odoo-friendly)
playwright-cli mousemove 300 200   # over the card
playwright-cli mousedown
playwright-cli mousemove 400 200   # start drag
playwright-cli mousemove 600 200   # over target column
playwright-cli mouseup

# Verify card moved to new column
playwright-cli eval "() => document.querySelector('.o_kanban_group:nth-child(2) .o_kanban_record:has-text(\"Task 1\")') ? 'moved' : 'not found'"

# Alternative: drag between kanban groups (drag to middle of column)
playwright-cli mousemove 300 200
playwright-cli mousedown
playwright-cli mousemove 600 300
playwright-cli mouseup
```

---

## Settings / Res.config.form

Settings pages use wizard-style multi-step layout with `res.config.settings`.

```bash
# Open settings (from app menu)
playwright-cli click '.o_menu_toggle'
playwright-cli click '.o_menu_item:has-text("Settings")'

# Settings form container
# Fields are rendered inside setting groups
playwright-cli fill '[name="company_name"] input' 'My Company'
playwright-cli check '[name="allow_external_users"]'

# Trigger immediate-save fields (no save button needed)
playwright-cli fill '[name="google_account_id"] input' 'account-id'
# Wait for save indicator
playwright-cli eval "() => document.querySelector('.o_form_statusbar .o_form_status1') ? 'saving...' : 'saved'"

# Deferred-save fields (need Apply button)
playwright-cli click '[name="default_export_format"] select'
playwright-cli select '[name="default_export_format"] select' 'xlsx'
playwright-cli click 'button[data-hotkey="s"]'    # Save & Close

# Discard settings
playwright-cli click '.o_form_button_cancel'
```

---

## Chatter / Message Thread

### Elements

| Element | Selector |
|---------|---------|
| Chatter panel | `.o_chatter` |
| Message input | `.o_chatter .o_composer_input` |
| Send button | `.o_chatter .o_composer_button_send` |
| Message list | `.o_chatter .o_message_list` |
| Message bubble | `.o_chatter .o_message` |
| Follow/Unfollow | `.o_chatter .o_followers .btn` |
| Log note toggle | `.o_chatter .o_log_note` |
| Attachment area | `.o_chatter .o_attachments` |

### Operations

```bash
# Post a message
playwright-cli fill '.o_chatter .o_composer_input' 'This is a follow-up note.'
playwright-cli click '.o_chatter .o_composer_button_send'

# Post internal note (log)
playwright-cli click '.o_chatter .o_log_note'
playwright-cli fill '.o_chatter .o_composer_input' 'Internal note visible only to internal users.'
playwright-cli click '.o_chatter .o_composer_button_send'

# Toggle follower
playwright-cli click '.o_chatter .o_followers .btn'
playwright-cli click '.o_followers .o_follower_item:has-text("Main User")'
playwright-cli click '.o_followers .btn[data-action="follow"]'

# Attach file to message
playwright-cli click '.o_chatter .o_attachment_button'
playwright-cli upload '.o_chatter input[type="file"]' ./document.pdf'
playwright-cli fill '.o_chatter .o_composer_input' 'Attached document for reference.'
playwright-cli click '.o_chatter .o_composer_button_send'
```

---

## Priority / Stars

Many models (crm.lead, project.task, etc.) have star priority.

```bash
# Toggle star/priority
playwright-cli click '.o_priority .fa-star'
playwright-cli click '.o_priority:has-text("High Priority") .fa-star'
```

---

## X2M Widget (Popup Selector)

When clicking `.o_external_button` on a many2one, Odoo opens a popup with a list.

```bash
# Click external button to open selector popup
playwright-cli click '[name="partner_id"] .o_external_button'

# Wait for popup
playwright-cli snapshot

# Search in popup
playwright-cli fill '.o_modal .o_searchview_input' 'Admin'
playwright-cli press Enter

# Select from popup list
playwright-cli click '.o_modal .o_list_table tr.o_data_row[data-id="42"]'
# OR click the row directly
playwright-cli click '.o_modal tr.o_data_row:nth-child(1)'

# Create new from popup
playwright-cli click '.o_modal .o_list_button_add'
playwright-cli fill '[name="name"] input' 'New Partner'
playwright-cli click '[data-hotkey="s"]'
# Popup closes, field is filled
```

---

## Dynamic / Custom Field Patterns

Custom modules may render fields with non-standard CSS classes. Fallback strategy:

```bash
# Step 1: snapshot once to see actual structure
playwright-cli snapshot --depth=5

# Step 2: find the actual [name] attribute from snapshot
# The field name attribute is ALWAYS on the container
# Step 3: target by name attribute
playwright-cli fill '[name="x_custom_field"] input' 'value'

# If field has no name, use text + closest parent
playwright-cli click '.o_form_view .o_field_widget label:has-text("Custom Label") ~ * input'
playwright-cli fill 'label:has-text("Custom Label")' 'value'

# Or inspect attributes first
playwright-cli eval "el => JSON.stringify([...el.closest('.o_field_widget').classList])" eN
playwright-cli eval "el => el.closest('.o_field_widget').getAttribute('name')" eN
```

---

## Control Panel & Search Bar

```bash
# Focus search input
playwright-cli click '.o_searchview_input'
playwright-cli fill '.o_searchview_input' 'admin'
playwright-cli press Enter

# Search facets (active filters shown as chips)
playwright-cli click '.o_searchview_facet .o_facet_remove'  # remove one filter
playwright-cli click '.o_searchview .o_searchview_clear'     # clear all

# Filter menu
playwright-cli click '.o_filter_menu .dropdown-toggle'
playwright-cli click '.o_dropdown_menu .o_menu_item:has-text("My Records")'

# Group by menu
playwright-cli click '.o_group_by_menu .dropdown-toggle'
playwright-cli click '.o_menu_item:has-text("Responsible")'

# Favorite / saved search
playwright-cli click '.o_favorite_menu .dropdown-toggle'
playwright-cli click '.o_menu_item:has-text("Save current search")'
# Fill save dialog
playwright-cli fill '[name="name"]' 'My Saved Filter'
playwright-cli click '.modal-dialog .btn-primary'

# View switcher
playwright-cli click '.o_switch_view.o_kanban'   # switch to kanban
playwright-cli click '.o_switch_view.o_list'    # switch to list
playwright-cli click '.o_switch_view.o_graph'   # switch to graph

# Action menu (Export, Print, etc.)
playwright-cli click '.o_cp_action_menus .dropdown-toggle'
playwright-cli click '.o_menu_item:has-text("Export")'
```

---

## Navigation / App Menu

```bash
# Open hamburger menu
playwright-cli click '.o_menu_toggle'

# App by xmlid (from Odoo menu definition)
# Replace underscores with underscores (keep xmlid format)
playwright-cli click '[data-menu-xmlid="sale.menu_sales"]'
playwright-cli click '[data-menu-xmlid="stock.menu_stock_transfers"]'
playwright-cli click '[data-menu-xmlid="account.menu_finance"]'
playwright-cli click '[data-menu-xmlid="mrp.menu_mrp_production"]'
playwright-cli click '[data-menu-xmlid="crm.menu_crm_opportunity"]'

# Breadcrumb (from form back to list/kanban)
playwright-cli click '.breadcrumb a:has-text("Orders")'

# Direct URL navigation (for speed)
# action=model.xml_id or action=xml_id of the ir.actions.act_window
playwright-cli goto 'http://localhost:8069/web#action=module.action_model'
```

---

## Dialogs & Modals

```bash
# Primary action (Save, Confirm, Apply)
playwright-cli click '.modal .btn-primary'
playwright-cli click '.modal-dialog .modal-footer .btn.btn-primary'

# Secondary / Cancel
playwright-cli click '.modal .btn-secondary'
playwright-cli click '.modal .btn-link'

# Close via X or aria
playwright-cli click '.modal [aria-label="Close"]'
playwright-cli click '.modal-header .close'

# Delete / Danger confirm
playwright-cli click '.modal .btn-danger'

# Select in modal dropdown
playwright-cli click '.modal select[name="journal_id"]'
playwright-cli select '.modal select[name="journal_id"]' 'Bank'

# Input in modal
playwright-cli fill '.modal input[name="amount"]' '500000'

# Multi-step modal (wizard steps)
playwright-cli click '.modal .o_wizard_step:has-text("Step 2")'
playwright-cli click '.modal .btn-next'
playwright-cli click '.modal .btn-back'
```

---

## Notifications / Toasts

```bash
# Success / error toast — dismiss
playwright-cli click '.o_notification_close'
playwright-cli click '.o_notification .toast-close'
playwright-cli click '.alert.alert-success .close'

# Warning banner
playwright-cli click '.alert.alert-warning .close'

# Dialog (not toast)
playwright-cli click '.modal .modal-footer .btn-primary'
```

---

## Priority: data-* Attributes Over CSS Classes

Odoo's CSS classes can change between versions or with custom themes. `data-*` attributes are more stable. When available, always prefer:

```
[data-hotkey]  >  .o_form_button_save  (button targeting)
[data-id]      >  tr:nth-child(2)     (row targeting)
[data-menu-xmlid] > .o_menu_item text  (menu navigation)
[name="field"] >  .o_field_widget     (field targeting)
```

---

## Version Differences

### Odoo 19 vs Odoo 17/18

- Odoo 17+ uses `o_select_menu_menu` for dropdown menus (Odoo 19 pattern)
- Odoo 15 uses older `.o_form_input` classes

### Odoo 15 Legacy Patterns (if targeting older)

```bash
# Odoo 15 form fields
playwright-cli fill '.o_form_view input.o_form_input[name="name"]' 'Value'
playwright-cli fill '.o_form_view textarea.o_form_textarea[name="description"]' 'Desc'

# Odoo 15 list
playwright-cli click '.o_list_view .o_data_row[data-id="42"]'
```

### When in doubt — snapshot once, target from there

```bash
playwright-cli snapshot
# Read the structure, then use selectors from the snapshot
playwright-cli click '.o_kanban_record:has-text("SO001")'
```

---

## Apps Page / Module Management

Module kanban cards on the Apps page (`/web#action=module.module_management`).

### Module Kanban Card Structure

Each module card (`.o_kanban_record`) contains:
- Module icon, name, description
- Action buttons: "Activate" (if uninstalled), "Upgrade" (if installed+extra), "Learn More"
- **Dropdown menu button** (⋮) in the top-right corner — this gives access to Uninstall, Module Info, etc.

### Key Selectors

| Element | Selector | Notes |
|---------|---------|-------|
| Dropdown button | `button[title="Dropdown menu"]` | Inside `.o_dropdown_kanban` on each card |
| Dropdown container | `.o_dropdown_kanban` | Positioned `absolute`, `end-0`, `top-0` |
| Dropdown menu (teleported) | `.o-dropdown--menu.o-dropdown--kanban-record-menu` | Teleported to `body`, not nested in card |
| Dropdown items | `.dropdown-item.oe_kanban_action` | Appears after clicking dropdown |
| Activate button | `.o_kanban_record:has-text("ModuleName") button:has-text("Activate")` | Uninstalled modules |
| Upgrade button | `.o_kanban_record:has-text("ModuleName") button:has-text("Upgrade")` | Installed modules with extra addons |
| Learn More link | `.o_kanban_record:has-text("ModuleName") a:has-text("Learn More")` | Opens module page |

### Uninstall Workflow (Frontend-Only)

```
1. Navigate to Apps page
   playwright-cli click '[data-menu-xmlid="base.menu_management"]'

2. Search for the module name
   playwright-cli fill 'input.o_searchview_input' 'ModuleName'
   playwright-cli press Enter

3. Click the dropdown menu button on the module card
   playwright-cli eval "() => {
     const card = [...document.querySelectorAll('.o_kanban_record')]
       .find(c => c.innerText.includes('ModuleName'));
     const btn = card?.querySelector('button[title=\"Dropdown menu\"]');
     if (btn) { btn.click(); return 'OK'; }
     return 'NOT_FOUND';
   }"

4. Click "Uninstall…" in the dropdown (menu is teleported to body)
   playwright-cli eval "() => {
     const items = [...document.querySelectorAll('.dropdown-item.oe_kanban_action')];
     const uninstall = items.find(i => i.innerText.includes('Uninstall'));
     if (uninstall) { uninstall.click(); return 'OK'; }
     return 'NOT_FOUND';
   }"

5. Confirm in the dialog
   playwright-cli click '[role="dialog"] button:has-text("Uninstall")'

6. Wait for uninstall to complete
   sleep 10
```

### Dialog After Uninstall Click

Clicking "Uninstall…" opens a confirmation dialog:
- Title: "Uninstall module"
- Warning text about risk
- List of modules to uninstall (may include dependent modules)
- List of documents that will be deleted
- Buttons: **"Uninstall"** (destructive) and **"Discard"** (cancel)

```bash
# Discard/cancel the uninstall
playwright-cli eval "() => {
  const btns = [...document.querySelectorAll('button')];
  btns.find(b => b.innerText.includes('Discard'))?.click();
}"

# Confirm the uninstall
playwright-cli click '[role="dialog"] button:has-text("Uninstall")'
```