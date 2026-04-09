---
description: Migrate Odoo view XML files from older versions to Odoo 19 format. Use when user wants to migrate views to Odoo 19.
---


# Odoo 19 View Migration

Migrate Odoo view XML files from older versions to Odoo 19 format, focusing on deprecated attributes, widget names, and structural changes.

## Instructions

1. **Read the target XML view file:**
   - Identify all view definitions (tree, form, kanban, search, etc.)
   - Check for deprecated attributes and widgets
   - Look for old-style field definitions

2. **Update deprecated attributes:**
   - Remove `attrs` in favor of `attrs` with proper syntax (still valid but check for old patterns)
   - Update `readonly`, `required`, `invisible` to use `attrs` or states
   - Replace `keyboard_mode` with modern alternatives

3. **Update deprecated widgets:**
   - `statusbar` → keep (still valid)
   - `progressbar` → keep (still valid)
   - `many2many_tags` → keep (still valid)
   - `selection` → keep (still valid)
   - `radio` → keep (still valid)
   - `priority` → keep (still valid)
   - `monetary` → keep (still valid)
   - `date` → keep (still valid)
   - `datetime` → keep (still valid)
   - `float` → keep (still valid)
   - `integer` → keep (still valid)
   - `text` → keep (still valid)
   - `html` → keep (still valid)
   - `image` → keep (still valid)
   - `handle` → keep (still valid)
   - `many2one` → keep (still valid)
   - `one2many` → keep (still valid)
   - `many2many` → keep (still valid)

4. **Update field attributes:**
   - Replace `nolabel` with proper field definition
   - Update `options` attribute format
   - Check `widget` attribute validity

5. **Update tree view specifics:**
   - Replace `colors` with `decoration-*` attributes
   - Update `editable` attribute (still valid)
   - Check `multi_edit` attribute

6. **Update form view specifics:**
   - Ensure proper `sheet` structure
   - Update `notebook` and `page` elements
   - Check `group` and `field` nesting

7. **Update search view specifics:**
   - Check `filter` element structure
   - Update `group` elements
   - Verify `searchpanel` definitions (if present)

## Common Migration Patterns

### Pattern 1: Tree View - Replace colors with decoration

**Before (Odoo 12-15):**
```xml
<tree string="Orders" colors="red:state=='cancel';blue:state=='draft'">
    <field name="name"/>
    <field name="state"/>
</tree>
```

**After (Odoo 19):**
```xml
<tree string="Orders" decoration-danger="state=='cancel'" decoration-info="state=='draft'">
    <field name="name"/>
    <field name="state"/>
</tree>
```

### Pattern 2: Form View - Update attrs format

**Before (Odoo 12-16):**
```xml
<field name="partner_id" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
```

**After (Odoo 19):**
```xml
<field name="partner_id" readonly="state != 'draft'"/>
```

### Pattern 3: Remove deprecated widgets

**Before (Odoo 12-14):**
```xml
<field name="description" widget="text"/>
```

**After (Odoo 19):**
```xml
<field name="description" widget="text"/>
```

### Pattern 4: Update button attributes

**Before (Odoo 12-15):**
```xml
<button name="action_confirm" string="Confirm" type="object" class="oe_highlight"/>
```

**After (Odoo 19):**
```xml
<button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
```

### Pattern 5: Update notebook/page structure

**Before (Odoo 12-16):**
```xml
<notebook>
    <page string="General">
        <group>
            <field name="name"/>
        </group>
    </page>
</notebook>
```

**After (Odoo 19):**
```xml
<notebook>
    <page name="general" string="General">
        <group>
            <field name="name"/>
        </group>
    </page>
</notebook>
```

## Usage Examples

### Example 1: Tree View Migration

```bash
/migrate-view views/sale_order_views.xml
```

**Input File (views/sale_order_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_sale_order_tree" model="ir.ui.view">
        <field name="name">sale.order.tree</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <tree string="Sale Orders" colors="red:state=='cancel';blue:state=='draft';green:state=='done'">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="date_order"/>
                <field name="amount_total"/>
                <field name="state"/>
            </tree>
        </field>
    </record>
</odoo>
```

**Output File (views/sale_order_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_sale_order_tree" model="ir.ui.view">
        <field name="name">sale.order.tree</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <tree string="Sale Orders"
                  decoration-danger="state=='cancel'"
                  decoration-info="state=='draft'"
                  decoration-success="state=='done'">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="date_order"/>
                <field name="amount_total"/>
                <field name="state"/>
            </tree>
        </field>
    </record>
</odoo>
```

### Example 2: Form View Migration

```bash
/migrate-view views/product_product_views.xml
```

**Input File (views/product_product_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_product_form" model="ir.ui.view">
        <field name="name">product.product.form</field>
        <field name="model">product.product</field>
        <field name="arch" type="xml">
            <form string="Product">
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="default_code"/>
                        </group>
                        <group>
                            <field name="list_price"/>
                            <field name="standard_price"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Description">
                            <field name="description" widget="text"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

**Output File (views/product_product_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_product_form" model="ir.ui.view">
        <field name="name">product.product.form</field>
        <field name="model">product.product</field>
        <field name="arch" type="xml">
            <form string="Product">
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="default_code"/>
                        </group>
                        <group>
                            <field name="list_price"/>
                            <field name="standard_price"/>
                        </group>
                    </group>
                    <notebook>
                        <page name="description" string="Description">
                            <field name="description" widget="text"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

### Example 3: Search View Migration

```bash
/migrate-view views/library_book_views.xml
```

**Input File (views/library_book_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_library_book_search" model="ir.ui.view">
        <field name="name">library.book.search</field>
        <field name="model">library.book</field>
        <field name="arch" type="xml">
            <search string="Library Books">
                <field name="name"/>
                <field name="author"/>
                <filter string="Available" name="available" domain="[('state', '=', 'available')]"/>
                <filter string="Borrowed" name="borrowed" domain="[('state', '=', 'borrowed')]"/>
                <separator/>
                <group expand="0" string="Group By">
                    <filter string="Author" name="author" context="{'group_by': 'author'}"/>
                    <filter string="State" name="state" context="{'group_by': 'state'}"/>
                </group>
            </search>
        </field>
    </record>
</odoo>
```

**Output File (views/library_book_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_library_book_search" model="ir.ui.view">
        <field name="name">library.book.search</field>
        <field name="model">library.book</field>
        <field name="arch" type="xml">
            <search string="Library Books">
                <field name="name"/>
                <field name="author"/>
                <filter string="Available" name="available" domain="[('state', '=', 'available')]"/>
                <filter string="Borrowed" name="borrowed" domain="[('state', '=', 'borrowed')]"/>
                <separator/>
                <group expand="0" string="Group By">
                    <filter string="Author" name="author_groupby" context="{'group_by': 'author'}"/>
                    <filter string="State" name="state_groupby" context="{'group_by': 'state'}"/>
                </group>
            </search>
        </field>
    </record>
</odoo>
```

### Example 4: Complex Form View with Buttons

```bash
/migrate-view views/hr_employee_views.xml
```

**Input File (views/hr_employee_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_employee_form" model="ir.ui.view">
        <field name="name">hr.employee.form</field>
        <field name="model">hr.employee</field>
        <field name="arch" type="xml">
            <form string="Employee">
                <header>
                    <button name="action_confirm" string="Confirm" type="object" class="oe_highlight" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                    <button name="action_approve" string="Approve" type="object" attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <field name="name" placeholder="Employee Name"/>
                    </div>
                    <group>
                        <group>
                            <field name="department_id"/>
                            <field name="job_id"/>
                        </group>
                        <group>
                            <field name="work_email"/>
                            <field name="work_phone"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

**Output File (views/hr_employee_views.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_employee_form" model="ir.ui.view">
        <field name="name">hr.employee.form</field>
        <field name="model">hr.employee</field>
        <field name="arch" type="xml">
            <form string="Employee">
                <header>
                    <button name="action_confirm" string="Confirm" type="object" class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_approve" string="Approve" type="object" invisible="state != 'confirmed'"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <field name="name" placeholder="Employee Name"/>
                    </div>
                    <group>
                        <group>
                            <field name="department_id"/>
                            <field name="job_id"/>
                        </group>
                        <group>
                            <field name="work_email"/>
                            <field name="work_phone"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

## Decoration Color Mapping

Old `colors` format to new `decoration-*` format:

| Old Color | New Decoration |
|-----------|----------------|
| `red` | `decoration-danger` |
| `blue` | `decoration-info` |
| `green` | `decoration-success` |
| `orange` | `decoration-warning` |
| `gray` | `decoration-muted` |
| `black` | `decoration-bf` (bold) |
| `purple` | `decoration-it` (italic) |
| `brown` | `decoration-primary` |
| `pink` | `decoration-secondary` |

## Common Widget Names in Odoo 19

### Text Widgets
- `text` - Multi-line text input
- `html` - HTML editor (requires web_editor)
- `url` - URL field with validation
- `email` - Email field with validation

### Relational Widgets
- `many2one` - Dropdown selection
- `many2many_tags` - Tag-style many2many
- `many2many_checkboxes` - Checkboxes for many2many
- `many2many_kanban` - Kanban view for many2many
- `one2many` - List view for one2many
- `one2many_list` - List view for one2many

### Selection Widgets
- `selection` - Dropdown selection
- `radio` - Radio button selection
- `priority` - Priority star selection

### Date/Time Widgets
- `date` - Date picker
- `datetime` - Date and time picker
- `datetime_range` - Date range picker

### Numeric Widgets
- `float` - Float number input
- `float_time` - Time duration (HH:MM)
- `monetary` - Monetary value with currency
- `percentage` - Percentage input
- `integer` - Integer input

### Media Widgets
- `image` - Image upload/preview
- `file` - File upload/download
- `binary` - Binary file upload

### Special Widgets
- `statusbar` - Status bar for workflow
- `progressbar` - Progress bar
- `handle` - Drag handle for reordering
- `reference` - Reference field (model + id)
- `chart_of_accounts` - Account chart selection
- `toggle_button` - Toggle button for boolean

## Migration Checklist

- [ ] Replace `colors` with `decoration-*` attributes
- [ ] Update `attrs` to modern format or use specific attributes
- [ ] Replace `class="oe_highlight"` with `class="btn-primary"`
- [ ] Add `name` attribute to `page` elements
- [ ] Update button class names
- [ ] Check for deprecated widgets
- [ ] Verify field widget compatibility
- [ ] Update `options` attribute format
- [ ] Check `searchpanel` structure
- [ ] Test views in different screen sizes
- [ ] Verify all conditional attributes work correctly

## Important Notes

1. **Backward Compatibility:** Some old attributes still work but should be updated for consistency.

2. **Attribute Format:** Use modern `invisible="condition"` format instead of `attrs="{'invisible': [('condition')]}"` when possible.

3. **Testing:** After migration, test:
   - All views render correctly
   - Buttons work as expected
   - Conditional fields show/hide properly
   - Search filters function correctly
   - Decoration colors appear correctly

4. **Performance:** Ensure view changes don't negatively impact performance, especially for large recordsets.

5. **Accessibility:** Check that migrated views maintain accessibility standards.

## Related Skills

- `/view-tree` - Create tree views
- `/view-form` - Create form views
- `/view-kanban` - Create kanban views
- `/view-search` - Create search views
- `/view-calendar` - Create calendar views
- `/view-pivot` - Create pivot views
- `/view-graph` - Create graph views
