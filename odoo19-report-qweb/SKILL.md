---
description: Create QWeb report template with PDF generation for Odoo 19. Use when user wants to create a QWeb report.
---


# Odoo 19 QWeb Report Creation

Create a QWeb report with PDF generation following Odoo 19 conventions, including report action XML, QWeb template structure, and optional Python report class for custom data processing.

## Instructions

1. **Determine the file locations:**
   - Report action XML: `{module_name}/report/{report_name}_report.xml`
   - QWeb template XML: `{module_name}/report/{report_name}_templates.xml`
   - Optional Python class: `{module_name}/report/{report_name}.py`

2. **Create the report action XML:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="{report_name}_action"
            string="{report_title}"
            model="{model_name}"
            report_type="{report_type}"
            name="{module_name}.{report_name}_template"
            file="{module_name}.{report_name}_template"
            print_report_name="{print_report_name}"
            attachment="{attachment}"
            paperformat="{module_name}_paperformat_{paper_format}"/>
    </data>
</odoo>
```

3. **Create the QWeb template XML:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="{report_name}_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>{report_title}</h2>
                        <!-- Your report content here -->
                        <div class="row">
                            <div class="col-6">
                                <strong>Field 1:</strong> <span t-field="o.field1"/>
                            </div>
                            <div class="col-6">
                                <strong>Field 2:</strong> <span t-field="o.field2"/>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

4. **Optional: Create a paper format:**

```xml
<record id="{module_name}_paperformat_{paper_format}" model="report.paperformat">
    <field name="name">{paper_format} Paper Format</field>
    <field name="default" eval="True"/>
    <field name="format">{paper_format}</field>
    <field name="page_height">0</field>
    <field name="page_width">0</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">40</field>
    <field name="margin_bottom">20</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">35</field>
    <field name="dpi">90</field>
</record>
```

5. **Optional: Create a Python report class for custom logic:**

```python
from odoo import models

class {ReportClassName}(models.AbstractModel):
    _name = 'report.{module_name}.{report_name}_template'
    _description = '{report_title} Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env[{model_name}].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': '{model_name}',
            'docs': docs,
            'data': data,
            # Add custom values here
            'custom_value': self._compute_custom_value(docs),
        }

    def _compute_custom_value(self, docs):
        # Your custom logic here
        return {}
```

6. **Update __manifest__.py:**

```python
'data': [
    # ...
    'report/{report_name}_report.xml',
    'report/{report_name}_templates.xml',
],
```

7. **Common QWeb template directives:**
   - `t-field="o.field_name"` - Direct field access
   - `t-esc="value"` - Escaped output
   - `t-raw="value"` - Raw HTML output
   - `t-if="condition"` - Conditional display
   - `t-foreach="records" t-as="r"` - Loop through records
   - `t-call="template_id"` - Call another template
   - `t-set="variable" t-value="expression"` - Set variable

## Usage Examples

### Basic PDF Report

```bash
/report-qweb library_book book_report "Library Book Report" book.library
```

Output:
```xml
<!-- library_book/report/book_report_report.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="book_report_action"
            string="Library Book Report"
            model="book.library"
            report_type="qweb-pdf"
            name="library_book.book_report_template"
            file="library_book.book_report_template"
            print_report_name="'Book Report - %s' % (object.name,)"/>
    </data>
</odoo>

<!-- library_book/report/book_report_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="book_report_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Library Book Report</h2>
                        <div class="row mt32">
                            <div class="col-6">
                                <strong>Title:</strong> <span t-field="o.name"/>
                            </div>
                            <div class="col-6">
                                <strong>ISBN:</strong> <span t-field="o.isbn"/>
                            </div>
                        </div>
                        <div class="row mt16">
                            <div class="col-12">
                                <strong>Description:</strong>
                                <p t-field="o.description"/>
                            </div>
                        </div>
                        <div class="row mt16">
                            <div class="col-12">
                                <strong>Authors:</strong>
                                <ul>
                                    <li t-foreach="o.author_ids" t-as="author">
                                        <span t-field="author.name"/>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Report with Custom Paper Format

```bash
/report-qweb sale_order sale_order_report "Sale Order Report" sale.order paperformat="custom" paper_format="A4"
```

Output:
```xml
<!-- sale_order/report/sale_order_report_report.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Custom Paper Format -->
        <record id="sale_order_paperformat_custom" model="report.paperformat">
            <field name="name">Sale Order Custom Format</field>
            <field name="default" eval="True"/>
            <field name="format">A4</field>
            <field name="page_height">0</field>
            <field name="page_width">0</field>
            <field name="orientation">Portrait</field>
            <field name="margin_top">40</field>
            <field name="margin_bottom">20</field>
            <field name="margin_left">7</field>
            <field name="margin_right">7</field>
            <field name="header_line" eval="False"/>
            <field name="header_spacing">35</field>
            <field name="dpi">90</field>
        </record>

        <report
            id="sale_order_report_action"
            string="Sale Order Report"
            model="sale.order"
            report_type="qweb-pdf"
            name="sale_order.sale_order_report_template"
            file="sale_order.sale_order_report_template"
            print_report_name="'Order-%s' % (object.name,)"
            paperformat="sale_order_paperformat_custom"/>
    </data>
</odoo>

<!-- sale_order/report/sale_order_report_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="sale_order_report_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Sale Order: <span t-field="o.name"/></h2>
                        <div class="row mt32">
                            <div class="col-6">
                                <strong>Customer:</strong> <span t-field="o.partner_id.name"/>
                            </div>
                            <div class="col-6">
                                <strong>Date:</strong> <span t-field="o.date_order"/>
                            </div>
                        </div>

                        <table class="table table-sm mt32">
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Unit Price</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr t-foreach="o.order_line" t-as="line">
                                    <td><span t-field="line.product_id.name"/></td>
                                    <td><span t-field="line.product_uom_qty"/></td>
                                    <td><span t-field="line.price_unit"/></td>
                                    <td><span t-field="line.price_subtotal"/></td>
                                </tr>
                            </tbody>
                        </table>

                        <div class="row mt16">
                            <div class="col-8">
                                <strong>Total Amount:</strong>
                            </div>
                            <div class="col-4">
                                <span t-field="o.amount_total" t-options="{'widget': 'monetary', 'display_currency': o.currency_id}"/>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Report with Python Class for Custom Logic

```bash
/report-qweb hr_employee payslip_report "Payslip Report" hr.payslip print_report_name="object.name"
```

Output:
```xml
<!-- hr_employee/report/payslip_report_report.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="payslip_report_action"
            string="Payslip Report"
            model="hr.payslip"
            report_type="qweb-pdf"
            name="hr_employee.payslip_report_template"
            file="hr_employee.payslip_report_template"
            print_report_name="'Payslip-%s' % (object.name,)"/>
    </data>
</odoo>

<!-- hr_employee/report/payslip_report_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="payslip_report_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Payslip: <span t-field="o.name"/></h2>

                        <div class="row mt32">
                            <div class="col-6">
                                <strong>Employee:</strong> <span t-field="o.employee_id.name"/>
                            </div>
                            <div class="col-6">
                                <strong>Period:</strong>
                                <span t-field="o.date_from"/> to <span t-field="o.date_to"/>
                            </div>
                        </div>

                        <!-- Use custom computed values from Python class -->
                        <h3 class="mt32">Earnings</h3>
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Rule</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr t-foreach="earnings" t-as="line">
                                    <td><span t-esc="line['name']"/></td>
                                    <td><span t-esc="line['amount']"/></td>
                                </tr>
                            </tbody>
                        </table>

                        <h3 class="mt32">Deductions</h3>
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Rule</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr t-foreach="deductions" t-as="line">
                                    <td><span t-esc="line['name']"/></td>
                                    <td><span t-esc="line['amount']"/></td>
                                </tr>
                            </tbody>
                        </table>

                        <div class="row mt32">
                            <div class="col-8">
                                <strong>Net Salary:</strong>
                            </div>
                            <div class="col-4">
                                <span t-esc="net_salary"/>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

```python
# hr_employee/report/payslip_report.py
from odoo import models

class PayslipReport(models.AbstractModel):
    _name = 'report.hr_employee.payslip_report_template'
    _description = 'Payslip Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.payslip'].browse(docids)

        earnings_list = []
        deductions_list = []
        net_salary = 0

        for payslip in docs:
            # Compute earnings
            for line in payslip.line_ids.filtered(lambda l: l.category_id.code == 'NET'):
                if line.amount > 0:
                    earnings_list.append({
                        'name': line.name,
                        'amount': line.amount,
                    })
                    net_salary += line.amount

            # Compute deductions
            for line in payslip.line_ids.filtered(lambda l: l.category_id.code == 'DED'):
                deductions_list.append({
                    'name': line.name,
                    'amount': abs(line.amount),
                })
                net_salary -= abs(line.amount)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': docs,
            'data': data,
            'earnings': earnings_list,
            'deductions': deductions_list,
            'net_salary': net_salary,
        }
```

### Report with Attachment

```bash
/report-qweb account_invoice invoice_report "Invoice Report" account.move attachment="'INV-' + object.name + '.pdf'"
```

Output:
```xml
<!-- account_invoice/report/invoice_report_report.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="invoice_report_action"
            string="Invoice Report"
            model="account.move"
            report_type="qweb-pdf"
            name="account_invoice.invoice_report_template"
            file="account_invoice.invoice_report_template"
            print_report_name="'Invoice-%s' % (object.name,)"
            attachment="'INV-' + object.name + '.pdf'"/>
    </data>
</odoo>
```

## Best Practices

1. **Report Naming:**
   - Use descriptive, user-friendly report titles
   - Use consistent naming convention for technical names
   - Include module name as prefix for templates

2. **Template Organization:**
   - Use Bootstrap classes for layout (row, col-6, col-12, etc.)
   - Leverage web.external_layout for consistent headers/footers
   - Use semantic HTML tags (table, h2, h3, p, ul, li)

3. **Performance:**
   - Keep templates simple and efficient
   - Avoid complex Python logic in templates
   - Use Python class for data processing and computations

4. **Styling:**
   - Use Odoo's built-in CSS classes
   - Add custom CSS in <style> tags when needed
   - Maintain consistent spacing with mt16, mt32 classes

5. **Printing:**
   - Set appropriate paper formats for your reports
   - Configure margins properly to avoid content cutoff
   - Use print_report_name for meaningful filenames
   - Consider attachment for storing generated reports

6. **Localization:**
   - Use t-options widget for monetary fields
   - Apply date formatting with t-field-options
   - Respect user language preferences

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── report/
│   ├── __init__.py  # Import report classes
│   ├── {report_name}_report.xml      # Report action
│   ├── {report_name}_templates.xml   # QWeb templates
│   └── {report_name}.py              # Optional Python class
├── models/
│   └── {model_file}.py
└── views/
    └── {model_file}_views.xml
```

## Next Steps

After creating the report, use:
- `/report-xlsx` - Create XLSX version of the report
- `/view-form` - Add print button to form views
- `/security-group` - Configure who can access the report

## Additional Resources

- QWeb documentation: Use `t-field`, `t-foreach`, `t-if` directives
- Report layouts: `web.external_layout`, `web.external_layout_clean`, `web.external_layout_boxed`
- Paper formats: A4, Letter, Legal, or custom dimensions
- Widgets: monetary, date, datetime, image, html, selection
