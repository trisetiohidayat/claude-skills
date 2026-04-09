---
description: Create QWeb template files with proper template ID and XPath expressions. Use when user wants to create a QWeb template.
---


# Odoo 19 QWeb Template Creation

Create QWeb template files with proper template ID, inherit_id for template extension, and XPath expressions for selective modification following Odoo 19 conventions.

## Instructions

1. **Determine the file location:**
   - Templates should be in: `{module_name}/views/{template_filename}.xml`
   - Use descriptive filenames (e.g., `templates.xml`, `assets.xml`, `report_templates.xml`)

2. **Generate the template XML structure:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Template definitions -->
    </data>
</odoo>
```

3. **Template types:**
   - `qweb` - General QWeb templates
   - `xml` - XML data templates
   - `report` - Report templates (QWeb reports)
   - `dashboard` - Dashboard templates
   - `portal` - Portal templates
   - `email` - Email templates

4. **Create standalone templates:**

```xml
<template id="template_id" name="Template Name" xml:space="preserve">
    <!-- Template content -->
    <div class="o_template">
        <h1>Content</h1>
    </div>
</template>
```

5. **Inherit and extend templates:**

```xml
<template id="module_name.inherit_template"
          name="Inherit Template Name"
          inherit_id="parent_module.template_id"
          active="True">

    <xpath expr="//div[@class='target-class']" position="inside">
        <!-- New content -->
    </xpath>

</template>
```

6. **XPath position modifiers:**
   - `inside` - Add content inside the element
   - `after` - Add content after the element
   - `before` - Add content before the element
   - `replace` - Replace the element
   - `attributes` - Modify element attributes
   - `move` - Move element to new location

7. **Add to __manifest__.py:**
   - Include template XML in data list
   - Format: `'views/templates.xml'`

## Usage Examples

### Basic QWeb Template

```bash
/web-template library_book custom_header
```

Output:
```xml
<!-- library_book/views/templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="custom_header" name="Custom Header" xml:space="preserve">
            <header class="o_custom_header">
                <div class="container">
                    <div class="row">
                        <div class="col-md-6">
                            <h1>Library Management</h1>
                        </div>
                        <div class="col-md-6 text-right">
                            <button class="btn btn-primary">Add Book</button>
                        </div>
                    </div>
                </div>
            </header>
        </template>
    </data>
</odoo>
```

### Template Inheritance with XPath

```bash
/web-template sale_custom order_form_summary inherit_id="sale.order_form" xpath_expr="//div[@class='oe_button_box']" position="after"
```

Output:
```xml
<!-- sale_custom/views/templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="order_form_summary"
                  name="Order Form Summary"
                  inherit_id="sale.sale_order_form"
                  active="True">

            <!-- Add summary section after button box -->
            <xpath expr="//div[@class='oe_button_box']" position="after">
                <div class="o_order_summary">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="summary_box">
                                <strong>Subtotal:</strong>
                                <span t-field="record.amount_untaxed"/>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary_box">
                                <strong>Tax:</strong>
                                <span t-field="record.amount_tax"/>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary_box">
                                <strong>Total:</strong>
                                <span t-field="record.amount_total"/>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary_box">
                                <strong>Status:</strong>
                                <span t-field="record.state"/>
                            </div>
                        </div>
                    </div>
                </div>
            </xpath>

        </template>
    </data>
</odoo>
```

### Multiple XPath Modifications

```bash
/web-template product_custom product_form_enhanced inherit_id="product.product_normal_form_view" xpath_expr="//field[@name='lst_price']|//notebook/page[@name='sales']" position="before|inside"
```

Output:
```xml
<!-- product_custom/views/templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="product_form_enhanced"
                  name="Product Form Enhanced"
                  inherit_id="product.product_normal_form_view"
                  active="True">

            <!-- Add profit margin before price -->
            <xpath expr="//field[@name='lst_price']" position="before">
                <field name="profit_margin" widget="percentage"/>
            </xpath>

            <!-- Add sales history to sales tab -->
            <xpath expr="//notebook/page[@name='sales']" position="inside">
                <group string="Sales History">
                    <field name="sales_count"/>
                    <field name="last_sale_date"/>
                    <field name="total_sales"/>
                </group>
            </xpath>

            <!-- Add custom class to price field -->
            <xpath expr="//field[@name='lst_price']" position="attributes">
                <attribute name="widget">monetary</attribute>
                <attribute name="class">o_price_highlight</attribute>
            </xpath>

        </template>
    </data>
</odoo>
```

### Portal Template

```bash
/web-template portal_custom portal_order_details template_type="portal"
```

Output:
```xml
<!-- portal_custom/views/templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="portal_order_details"
                  name="Portal Order Details"
                  xml:space="preserve">

            <t t-call="portal.portal_layout">
                <t t-set="breadcrumbs_searchbar" t-value="True"/>

                <div class="o_portal_sale_details">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">
                                Order <t t-esc="order.name"/>
                                <span class="badge"
                                      t-att-class="'badge-%s' % ('success' if order.state in ('done', 'sale') else 'warning')">
                                    <t t-esc="order.state"/>
                                </span>
                            </h3>
                        </div>

                        <div class="panel-body">
                            <!-- Order information -->
                            <div class="row mb8">
                                <div class="col-md-6">
                                    <strong>Date:</strong>
                                    <span t-field="order.date_order"/>
                                </div>
                                <div class="col-md-6 text-right">
                                    <strong>Customer:</strong>
                                    <span t-field="order.partner_id.name"/>
                                </div>
                            </div>

                            <!-- Order lines -->
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th class="text-right">Quantity</th>
                                        <th class="text-right">Unit Price</th>
                                        <th class="text-right">Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr t-foreach="order.order_line" t-as="line">
                                        <td>
                                            <span t-field="line.name"/>
                                        </td>
                                        <td class="text-right">
                                            <span t-field="line.product_uom_qty"/>
                                        </td>
                                        <td class="text-right">
                                            <span t-field="line.price_unit" t-options='{"widget": "monetary"}'/>
                                        </td>
                                        <td class="text-right">
                                            <span t-field="line.price_total" t-options='{"widget": "monetary"}'/>
                                        </td>
                                    </tr>
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="3" class="text-right">
                                            <strong>Total:</strong>
                                        </td>
                                        <td class="text-right">
                                            <strong t-field="order.amount_total" t-options='{"widget": "monetary"}'/>
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                </div>

            </t>

        </template>
    </data>
</odoo>
```

### Report Template

```bash
/web-template invoice_custom report_invoice_custom template_type="report" inherit_id="account.report_invoice_document"
```

Output:
```xml
<!-- invoice_custom/views/report_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="report_invoice_custom"
                  name="Custom Invoice Report"
                  inherit_id="account.report_invoice_document">

            <!-- Add custom header -->
            <xpath expr="//div[hasclass('o_report_layout_standard')]/div[@id='informations']" position="inside">
                <div class="custom_invoice_info">
                    <span t-if="o.invoice_origin">
                        <strong>Source:</strong> <span t-field="o.invoice_origin"/>
                    </span>
                </div>
            </xpath>

            <!-- Add customer notes section -->
            <xpath expr="//div[@id='footer']" position="before">
                <div class="page_break"/>
                <div class="custom_notes_section">
                    <h3>Customer Notes</h3>
                    <p t-field="o.comment"/>
                </div>
            </xpath>

            <!-- Modify invoice lines table -->
            <xpath expr="//table[hasclass('table', 'table-condensed')]/thead/tr" position="inside">
                <th class="text-right">Discount</th>
            </xpath>

            <xpath expr="//table[hasclass('table', 'table-condensed')]/tbody/t" position="inside">
                <td class="text-right">
                    <span t-field="line.discount"/>%
                </td>
            </xpath>

            <!-- Add payment terms -->
            <xpath expr="//div[@id='qrcode']" position="after">
                <div class="payment_terms">
                    <strong>Payment Terms:</strong>
                    <span t-field="o.invoice_payment_term_id.name"/>
                </div>
            </xpath>

        </template>

        <template id="report_invoice_custom_values"
                  name="Custom Invoice Report Values"
                  inherit_id="account.report_invoice_document">

            <!-- Add custom CSS -->
            <xpath expr="//t[@t-call='web.html_container']" position="before">
                <style>
                    .custom_invoice_info {
                        font-size: 10px;
                        margin-bottom: 10px;
                    }
                    .payment_terms {
                        margin-top: 20px;
                        font-size: 9px;
                    }
                    .custom_notes_section {
                        margin-top: 30px;
                        page-break-inside: avoid;
                    }
                </style>
            </xpath>

        </template>

    </data>
</odoo>
```

### Dashboard Template

```bash
/web-template dashboard_custom dashboard_sales_summary template_type="dashboard"
```

Output:
```xml
<!-- dashboard_custom/views/dashboard_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="dashboard_sales_summary"
                  name="Sales Summary Dashboard"
                  xml:space="preserve">

            <div class="o_dashboard_sales">
                <div class="container-fluid">
                    <div class="row">
                        <!-- KPI Cards -->
                        <div class="col-md-3">
                            <div class="card card-primary">
                                <div class="card-body">
                                    <h3 class="card-title">Total Sales</h3>
                                    <h2 t-esc="data.total_sales"/>
                                    <p class="text-muted">
                                        <span class="fa fa-arrow-up text-success"/>
                                        <span t-esc="data.growth"/>% vs last month
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-3">
                            <div class="card card-success">
                                <div class="card-body">
                                    <h3 class="card-title">New Orders</h3>
                                    <h2 t-esc="data.new_orders"/>
                                    <p class="text-muted">
                                        <span class="fa fa-clock-o"/>
                                        Today
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-3">
                            <div class="card card-info">
                                <div class="card-body">
                                    <h3 class="card-title">Revenue</h3>
                                    <h2 t-esc="data.revenue" t-options='{"widget": "monetary"}'/>
                                    <p class="text-muted">
                                        <span class="fa fa-calendar"/>
                                        This month
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-3">
                            <div class="card card-warning">
                                <div class="card-body">
                                    <h3 class="card-title">Pending</h3>
                                    <h2 t-esc="data.pending_orders"/>
                                    <p class="text-muted">
                                        <span class="fa fa-exclamation-triangle"/>
                                        Require action
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Charts Section -->
                    <div class="row mt16">
                        <div class="col-md-8">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Sales Trend</h3>
                                </div>
                                <div class="panel-body">
                                    <div class="o_chart_sales">
                                        <!-- Chart placeholder -->
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Top Products</h3>
                                </div>
                                <div class="panel-body">
                                    <ul class="list-group">
                                        <t t-foreach="data.top_products" t-as="product">
                                            <li class="list-group-item">
                                                <span t-esc="product.name"/>
                                                <span class="badge pull-right" t-esc="product.quantity"/>
                                            </li>
                                        </t>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </template>
    </data>
</odoo>
```

### Email Template

```bash
/web-template mail_custom email_order_confirmation template_type="email"
```

Output:
```xml
<!-- mail_custom/views/email_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="email_order_confirmation"
                  name="Order Confirmation Email">

            <!-- Subject -->
            <t t-set="subject" t-value="'Order Confirmation - %s' % (object.name,)"/>

            <!-- Email body -->
            <div>
                <p>Dear <t t-esc="object.partner_id.name"/>,</p>

                <p>Thank you for your order <strong t-esc="object.name"/>. We're pleased to confirm that we've received your order.</p>

                <div style="margin: 20px 0;">
                    <h3>Order Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f8f9fa;">
                                <th style="padding: 10px; border: 1px solid #dee2e6; text-align: left;">Product</th>
                                <th style="padding: 10px; border: 1px solid #dee2e6; text-align: right;">Quantity</th>
                                <th style="padding: 10px; border: 1px solid #dee2e6; text-align: right;">Unit Price</th>
                                <th style="padding: 10px; border: 1px solid #dee2e6; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="object.order_line" t-as="line">
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">
                                        <span t-field="line.name"/>
                                    </td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: right;">
                                        <span t-field="line.product_uom_qty"/>
                                    </td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: right;">
                                        <span t-field="line.price_unit" t-options='{"widget": "monetary"}'/>
                                    </td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: right;">
                                        <span t-field="line.price_total" t-options='{"widget": "monetary"}'/>
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                </div>

                <div style="margin: 20px 0; text-align: right;">
                    <strong>Total: <span t-field="object.amount_total" t-options='{"widget": "monetary"}'/></strong>
                </div>

                <p>You can track your order status <a t-attf-href="/my/orders/{{ object.id }}">here</a>.</p>

                <p>Best regards,<br/>
                The Sales Team</p>

                <hr style="margin: 20px 0; border: none; border-top: 1px solid #dee2e6;"/>

                <p style="font-size: 12px; color: #6c757d;">
                    This is an automated message. Please do not reply directly to this email.
                </p>
            </div>

        </template>
    </data>
</odoo>
```

## Template Directives

### t-name - Template Name
```xml
<t t-name="template.id">
    <!-- Content -->
</t>
```

### t-set - Set Variable
```xml
<t t-set="variable_name" t-value="record.field"/>
<t t-set="user_name" t-value="user.name"/>
```

### t-esc - Escape Output
```xml
<span t-esc="record.name"/>
<t t-esc="variable_name"/>
```

### t-raw - Raw Output (no escaping)
```xml
<div t-raw="record.html_content"/>
```

### t-if - Conditional Rendering
```xml>
<div t-if="record.state == 'confirmed'">
    <!-- Content if true -->
</div>
```

### t-elif - Else If
```xml
<div t-if="record.state == 'draft'">Draft</div>
<div t-elif="record.state == 'confirmed'">Confirmed</div>
<div t-else="">Other</div>
```

### t-else - Else
```xml
<div t-if="condition">True</div>
<div t-else="">False</div>
```

### t-foreach - Loop
```xml
<t t-foreach="records" t-as="record">
    <span t-esc="record.name"/>
</t>
```

### t-as - Loop Variable
```xml
<t t-foreach="records" t-as="record">
    <span t-esc="record_index"/> <!-- Current index -->
</t>
```

### t-att - Attributes
```xml
<div t-attf-class="row {{ record.state }}">
<div t-att-class="record.class_name">
<div t-att-style="'background-color: ' + record.color">
```

### t-call - Call Template
```xml
<t t-call="web.html_container">
    <!-- Content -->
</t>
```

### t-field - Field Widget
```xml
<span t-field="record.name"/>
<span t-field="record.date" t-options='{"widget": "date"}'/>
<span t-field="record.amount" t-options='{"widget": "monetary"}'/>
```

### t-options - Widget Options
```xml
<span t-field="record.amount" t-options='{"widget": "monetary", "display_currency": "record.currency_id"}'/>
```

## XPath Expressions

### By Attribute
```xml
<xpath expr="//div[@class='target-class']" position="inside">
<xpath expr="//field[@name='field_name']" position="after">
<xpath expr="//button[@name='action_method']" position="before">
```

### By ID
```xml
<xpath expr="//div[@id='element_id']" position="inside">
```

### By Position
```xml
<xpath expr="//div[1]" position="inside">  <!-- First div -->
<xpath expr="//div[last()]" position="after">  <!-- Last div -->
```

### By Class
```xml
<xpath expr="//*[hasclass('o_form_statusbar')]" position="inside">
```

### Complex Expressions
```xml
<xpath expr="//notebook/page[@name='sales']//group[@string='Information']" position="inside">
<xpath expr="//form/sheet/div[@class='oe_title']" position="after">
```

## Best Practices

1. **Template Naming:**
   - Use descriptive IDs: `{module}.{purpose}`
   - Use consistent prefixes: `module_name.template_name`
   - Avoid generic names: `custom_template` (bad)

2. **XPath Usage:**
   - Use specific expressions to avoid conflicts
   - Test XPath with Odoo Studio or browser dev tools
   - Use `position="attributes"` for simple modifications

3. **Template Inheritance:**
   - Always specify `inherit_id` when extending
   - Use `active="True"` to enable/disable
   - Keep extensions focused on one purpose

4. **Performance:**
   - Avoid complex logic in templates
   - Use computed fields instead of template logic
   - Lazy load heavy components

5. **Accessibility:**
   - Use semantic HTML
   - Add proper ARIA labels
   - Ensure keyboard navigation

6. **Security:**
   - Always escape user input with `t-esc`
   - Use `t-raw` only for trusted content
   - Validate data in Python, not templates

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── views/
│   ├── templates.xml        # General templates
│   ├── report_templates.xml  # Report templates
│   ├── email_templates.xml   # Email templates
│   └── assets.xml           # Asset bundles
└── static/
    └── src/
        └── xml/
            └── component_templates.xml  # JS component templates
```

## Next Steps

After creating templates, use:
- `/web-assets` - Add template XML to asset bundles
- `/web-widget` - Create widgets that use templates
- `/controller-new` - Create controllers that render templates
- `/report-qweb` - Create QWeb reports
