---
name: odoo-reporting-analysis
description: |
  Analisis pelaporan Odoo - QWeb reports, XLSX reports, pivot tables, dashboards, graph views,
  BI tools integration. Gunakan ketika:
  - User bertanya tentang reporting
  - Ingin build report baru
  - Need to analyze existing reports
  - Ingin understand BI integration
---

# Odoo Reporting Analysis Skill

## Overview

Skill ini membantu menganalisis dan membangun sistem pelaporan Odoo yang komprehensif. Pelaporan merupakan aspek kritis dalam setiap implementasi enterprise Odoo, memungkinkan stakeholder menganalisis data bisnis, memantau KPI, dan membuat keputusan berbasis data. Odoo menyediakan berbagai mekanisme pelaporan yang dapat disesuaikan, mulai dari report PDF berbasis QWeb, laporan Excel, hingga dashboard interaktif dengan pivot tables dan graph views.

Pemahaman mendalam tentang arsitektur pelaporan Odoo memungkinkan developer membangun solusi reporting yang powerful dan mudah digunakan. Skill ini akan memandu Anda melalui analisis berbagai tipe laporan, struktur internal, teknik desain lanjutan, dan integrasi dengan tools BI eksternal.

Dalam konteks Odoo 19, terdapat beberapa perubahan signifikan dalam sistem pelaporan. QWeb terus menjadi engine utama untuk PDF reports, namun dengan peningkatan performa dan fitur baru. Module report_xlsx tetap menjadi standar untuk laporan Excel, sementara pivot dan graph views mengalami peningkatan interaktivitas.

## Step 1: Analyze Report Types

### 1.1 QWeb PDF Reports

QWeb adalah template engine Odoo yang digunakan untuk menghasilkan PDF reports. QWeb menggabungkan kekuatan Python dengan sintaks template yang ekspresif, memungkinkan pembuatan laporan yang kompleks namun tetap maintainable.

Struktur dasar modul laporan QWeb:

```
my_report_module/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py
│   └── report_models.py
├── reports/
│   ├── __init__.py
│   └── report_template.xml
└── views/
    └── report_views.xml
```

Contoh __manifest__.py untuk modul laporan:

```python
# __manifest__.py
{
    'name': 'Vendor Report',
    'version': '19.0.1',
    'category': 'Reporting',
    'summary': 'Vendor analysis reports',
    'description': """
        Vendor Reports Module
        ====================

        Provides comprehensive vendor analysis and reporting capabilities:
        - Vendor balance summary
        - Vendor invoice details
        - Payment history
        - Performance metrics
    """,
    'author': 'Roedl',
    'website': 'https://www.roedl.com',
    'depends': ['base', 'account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_template.xml',
        'views/report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

Model untuk laporan:

```python
# models/report_models.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class VendorReport(models.Model):
    """Model untuk vendor reporting"""
    _name = 'vendor.report'
    _description = 'Vendor Report'
    _auto = False

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    vendor_name = fields.Char()
    vendor_ref = fields.Char(string='Vendor Code')
    invoice_count = fields.Integer(string='Invoice Count')
    total_invoiced = fields.Float(string='Total Invoiced')
    total_paid = fields.Float(string='Total Paid')
    total_due = fields.Float(string='Total Due')
    last_invoice_date = fields.Date(string='Last Invoice Date')
    payment_rate = fields.Float(string='Payment Rate', compute='_compute_payment_rate')

    def _compute_payment_rate(self):
        """Calculate payment rate"""
        for record in self:
            if record.total_invoiced > 0:
                record.payment_rate = (record.total_paid / record.total_invoiced) * 100
            else:
                record.payment_rate = 0

    def init(self):
        """Create materialized view untuk reporting"""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW vendor_report AS (
                SELECT
                    p.id as id,
                    p.id as vendor_id,
                    p.name as vendor_name,
                    p.ref as vendor_ref,
                    COUNT(ai.id) as invoice_count,
                    SUM(ai.amount_total) as total_invoiced,
                    COALESCE(SUM(ail.price_total), 0) as total_paid,
                    SUM(ai.amount_residual) as total_due,
                    MAX(ai.invoice_date) as last_invoice_date
                FROM res_partner p
                LEFT JOIN account_move ai ON
                    ai.partner_id = p.id
                    AND ai.move_type IN ('in_invoice', 'in_refund')
                    AND ai.state = 'posted'
                LEFT JOIN account_move_line ail ON
                    ail.move_id = ai.id
                    AND ail.account_id IN (
                        SELECT id FROM account_account
                        WHERE account_type = 'asset_receivable'
                    )
                WHERE p.supplier_rank > 0
                GROUP BY p.id
            )
        """)


class ReportVendorSummary(models.AbstractModel):
    """Abstract model untuk vendor summary report"""
    _name = 'report.vendor.summary'
    _description = 'Vendor Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Return values untuk report"""
        docs = self.env['res.partner'].browse(docids)

        # Get date range dari data
        date_from = data.get('date_from') or fields.Date.today().replace(day=1)
        date_to = data.get('date_to') or fields.Date.today()

        # Get invoice data
        invoices = self.env['account.move'].search([
            ('partner_id', 'in', docids),
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('state', '=', 'posted'),
        ])

        # Group by vendor
        vendor_data = {}
        for invoice in invoices:
            if invoice.partner_id.id not in vendor_data:
                vendor_data[invoice.partner_id.id] = {
                    'vendor': invoice.partner_id,
                    'invoices': [],
                    'total': 0,
                    'paid': 0,
                    'due': 0,
                }

            vendor_data[invoice.partner_id.id]['invoices'].append(invoice)
            vendor_data[invoice.partner_id.id]['total'] += invoice.amount_total
            vendor_data[invoice.partner_id.id]['paid'] += invoice.amount_total - invoice.amount_residual
            vendor_data[invoice.partner_id.id]['due'] += invoice.amount_residual

        return {
            'docs': docs,
            'vendor_data': vendor_data,
            'date_from': date_from,
            'date_to': date_to,
            'currency': self.env.company.currency_id,
        }
```

Template QWeb untuk laporan:

```xml
<!-- reports/report_template.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Report Action -->
        <record id="action_vendor_summary" model="ir.actions.report">
            <field name="name">Vendor Summary</field>
            <field name="model">res.partner</field>
            <field name="report_type">qweb-pdf</field>
            <field name="report_name">vendor_report.summary</field>
            <field name="report_file">vendor_report.summary</field>
            <field name="binding_model_id" ref="base.model_res_partner"/>
            <field name="binding_type">report</field>
        </record>

        <!-- Report Template -->
        <template id="summary">
            <t t-call="web.html_container">
                <t t-foreach="docs" t-as="o">
                    <t t-call="web.external_layout">
                        <div class="page">
                            <!-- Header -->
                            <div class="row mt-4">
                                <div class="col-12">
                                    <h2 class="text-center">Vendor Summary Report</h2>
                                    <p class="text-center text-muted">
                                        <span t-esc="date_from"/> to <span t-esc="date_to"/>
                                    </p>
                                </div>
                            </div>

                            <!-- Vendor Info -->
                            <div class="row mt-4">
                                <div class="col-6">
                                    <strong>Vendor:</strong> <span t-esc="o.name"/><br/>
                                    <strong>Code:</strong> <span t-esc="o.ref"/><br/>
                                    <strong>Email:</strong> <span t-esc="o.email"/>
                                </div>
                                <div class="col-6 text-right">
                                    <strong>Report Date:</strong> <span t-esc="context_timestamp(datetime.datetime.now()).strftime('%Y-%m-%d')"/><br/>
                                    <strong>Currency:</strong> <span t-esc="currency.name"/>
                                </div>
                            </div>

                            <!-- Summary Cards -->
                            <div class="row mt-4">
                                <div class="col-4">
                                    <div class="card bg-primary text-white">
                                        <div class="card-body">
                                            <h5 class="card-title">Total Invoiced</h5>
                                            <h3 t-esc="vendor_data[o.id]['total']" t-options="{'widget': 'monetary', 'display_currency': currency}"/>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="card bg-success text-white">
                                        <div class="card-body">
                                            <h5 class="card-title">Total Paid</h5>
                                            <h3 t-esc="vendor_data[o.id]['paid']" t-options="{'widget': 'monetary', 'display_currency': currency}"/>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="card bg-warning text-white">
                                        <div class="card-body">
                                            <h5 class="card-title">Total Due</h5>
                                            <h3 t-esc="vendor_data[o.id]['due']" t-options="{'widget': 'monetary', 'display_currency': currency}"/>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Invoice Table -->
                            <div class="row mt-4">
                                <div class="col-12">
                                    <h4>Invoice Details</h4>
                                    <table class="table table-sm table-bordered">
                                        <thead>
                                            <tr>
                                                <th>Invoice #</th>
                                                <th>Date</th>
                                                <th>Due Date</th>
                                                <th class="text-right">Amount</th>
                                                <th class="text-right">Paid</th>
                                                <th class="text-right">Due</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr t-foreach="vendor_data[o.id]['invoices']" t-as="inv">
                                                <td><span t-esc="inv.name"/></td>
                                                <td><span t-esc="inv.invoice_date"/></td>
                                                <td><span t-esc="inv.invoice_date_due"/></td>
                                                <td class="text-right" t-esc="inv.amount_total" t-options="{'widget': 'monetary', 'display_currency': currency}"/>
                                                <td class="text-right" t-esc="inv.amount_total - inv.amount_residual" t-options="{'widget': 'monetary', 'display_currency': currency}"/>
                                                <td class="text-right" t-esc="inv.amount_residual" t-options="{'widget': 'monetary', 'display_currency': currency}"/>
                                                <td>
                                                    <span t-attf-class="badge badge-#{'success' if inv.payment_state == 'paid' else 'warning'}">
                                                        <span t-esc="inv.payment_state"/>
                                                    </span>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- Notes -->
                            <div class="row mt-4" t-if="o.comment">
                                <div class="col-12">
                                    <h4>Notes</h4>
                                    <p t-esc="o.comment"/>
                                </div>
                            </div>
                        </div>
                    </t>
                </t>
            </t>
        </template>
    </data>
</odoo>
```

### 1.2 XLSX Reports

Laporan Excel sangat berguna untuk analisis lebih lanjut yang memerlukan manipulasi data di spreadsheet. Odoo menggunakan module report_xlsx untuk menghasilkan laporan Excel.

Struktur laporan XLSX:

```python
# models/report_xlsx.py
from odoo import models
import datetime

class VendorXlsxReport(models.AbstractModel):
    """Abstract model untuk Excel report"""
    _name = 'report.vendor.report_xlsx'
    _description = 'Vendor XLSX Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        """Generate Excel report"""
        # Get currency
        currency = self.env.company.currency_id

        for partner in partners:
            # Create sheet
            sheet = workbook.add_worksheet(partner.name[:31])

            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
            })

            number_format = workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
            })

            date_format = workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'border': 1,
            })

            # Set column widths
            sheet.set_column('A:A', 15)  # Invoice
            sheet.set_column('B:B', 12)  # Date
            sheet.set_column('C:C', 12)  # Due Date
            sheet.set_column('D:D', 15)  # Amount
            sheet.set_column('E:E', 15)  # Paid
            sheet.set_column('F:F', 15)  # Due

            # Write header
            sheet.write('A1', 'Invoice #', header_format)
            sheet.write('B1', 'Date', header_format)
            sheet.write('C1', 'Due Date', header_format)
            sheet.write('D1', 'Amount', header_format)
            sheet.write('E1', 'Paid', header_format)
            sheet.write('F1', 'Due', header_format)

            # Get invoices
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['in_invoice', 'in_refund']),
                ('state', '=', 'posted'),
            ], order='invoice_date desc')

            # Write data
            row = 1
            for invoice in invoices:
                sheet.write(row, 0, invoice.name)
                sheet.write(row, 1, invoice.invoice_date, date_format)
                sheet.write(row, 2, invoice.invoice_date_due, date_format)
                sheet.write(row, 3, invoice.amount_total, number_format)
                sheet.write(row, 4, invoice.amount_total - invoice.amount_residual, number_format)
                sheet.write(row, 5, invoice.amount_residual, number_format)
                row += 1

            # Write totals
            sheet.write(row, 0, 'TOTAL', header_format)
            sheet.write_formula(row, 3, f'=SUM(D2:D{row})', number_format)
            sheet.write_formula(row, 4, f'=SUM(E2:E{row})', number_format)
            sheet.write_formula(row, 5, f'=SUM(F2:F{row})', number_format)

            # Add summary
            row += 2
            sheet.write(row, 0, 'Summary', header_format)
            row += 1
            sheet.write(row, 0, 'Total Invoiced:')
            sheet.write(row, 1, sum(invoices.mapped('amount_total')), number_format)
            row += 1
            sheet.write(row, 0, 'Total Paid:')
            sheet.write(row, 1, sum(invoices.mapped('amount_total') - invoices.mapped('amount_residual')), number_format)
            row += 1
            sheet.write(row, 0, 'Total Due:')
            sheet.write(row, 1, sum(invoices.mapped('amount_residual')), number_format)
```

### 1.3 Pivot Tables

Pivot tables di Odoo memungkinkan analisis data interaktif tanpa perlu membuat report khusus:

```xml
<!-- views/pivot_view.xml -->
<odoo>
    <data>
        <record id="view_vendor_pivot" model="ir.ui.view">
            <field name="name">vendor.pivot</field>
            <field name="model">account.move</field>
            <field name="arch" type="xml">
                <pivot string="Vendor Analysis" disable_linking="1">
                    <field name="partner_id" type="row"/>
                    <field name="invoice_date" interval="month" type="col"/>
                    <field name="amount_total" type="measure"/>
                </pivot>
            </field>
        </record>

        <record id="view_vendor_pivot_extended" model="ir.ui.view">
            <field name="name">vendor.pivot.extended</field>
            <field name="model">account.move</field>
            <field name="arch" type="xml">
                <pivot string="Vendor Analysis Extended" sample="1">
                    <field name="partner_id" type="row" order="amount_total desc"/>
                    <field name="invoice_date" interval="week" type="col"/>
                    <field name="amount_total" type="measure" string="Invoiced Amount"/>
                    <field name="amount_residual" type="measure" string="Due Amount"/>
                    <field name="invoice_id" type="measure" string="Invoice Count"/>
                </pivot>
            </field>
        </record>
    </data>
</odoo>
```

### 1.4 Graph Views

Graph views menyediakan visualisasi data dalam berbagai format:

```xml
<!-- views/graph_view.xml -->
<odoo>
    <data>
        <record id="view_vendor_graph" model="ir.ui.view">
            <field name="name">vendor.graph</field>
            <field name="model">account.move</field>
            <field name="arch" type="xml">
                <graph string="Vendor Revenue" type="bar" orientation="horizontal">
                    <field name="partner_id" type="row" group="True"/>
                    <field name="amount_total" type="measure"/>
                </graph>
            </field>
        </record>

        <record id="view_vendor_graph_line" model="ir.ui.view">
            <field name="name">vendor.graph.line</field>
            <field name="model">account.move</field>
            <field name="arch" type="xml">
                <graph string="Vendor Trend" type="line">
                    <field name="invoice_date" interval="month" type="col"/>
                    <field name="partner_id" type="row"/>
                    <field name="amount_total" type="measure"/>
                </graph>
            </field>
        </record>
    </data>
</odoo>
```

### 1.5 Dashboards

Dashboards menggabungkan berbagai elemen reporting dalam satu tampilan:

```xml
<!-- views/dashboard.xml -->
<odoo>
    <data>
        <!-- Dashboard Action -->
        <record id="action_vendor_dashboard" model="ir.actions.act_window">
            <field name="name">Vendor Dashboard</field>
            <field name="res_model">account.move</field>
            <field name="view_mode">graph,pivot,tree,form</field>
            <field name="context">{
                'search_default_partner_id': 1,
                'group_by': ['partner_id'],
            }</field>
        </record>

        <!-- Dashboard View -->
        <record id="view_vendor_dashboard" model="ir.ui.view">
            <field name="name">vendor.dashboard</field>
            <field name="model">account.move</field>
            <field name="arch" type="xml">
                <dashboard>
                    <group>
                        <group>
                            <aggregate name="total_invoiced" field="amount_total" string="Total Invoiced"/>
                            <aggregate name="total_due" field="amount_residual" string="Total Due"/>
                            <aggregate name="invoice_count" field="id" string="Invoice Count" count="True"/>
                        </group>
                        <group>
                            <aggregate name="avg_invoice" field="amount_total" string="Average Invoice" avg="True"/>
                            <measure name="partner_id" string="Vendors"/>
                        </group>
                    </group>
                    <view type="graph" ref="view_vendor_graph"/>
                </dashboard>
            </field>
        </record>
    </data>
</odoo>
```

## Step 2: Analyze Report Structure

### 2.1 Report Models

Struktur model laporan sangat penting untuk dipahami. Ada beberapa pendekatan:

**Approach 1: SQL View (Materialized)**
```python
class ReportPartnerInvoice(models.Model):
    _name = 'report.partner.invoice'
    _description = 'Partner Invoice Report'
    _auto = False

    partner_id = fields.Many2one('res.partner', string='Partner')
    move_count = fields.Integer(string='# Invoices')
    total_invoiced = fields.Float(string='Total Invoiced')
    total_paid = fields.Float(string='Total Paid')
    total_due = fields.Float(string='Total Due')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_partner_invoice AS (
                SELECT
                    p.id,
                    p.id as partner_id,
                    COUNT(am.id) as move_count,
                    SUM(am.amount_total) as total_invoiced,
                    SUM(am.amount_total - am.amount_residual) as total_paid,
                    SUM(am.amount_residual) as total_due
                FROM res_partner p
                LEFT JOIN account_move am ON
                    am.partner_id = p.id
                    AND am.move_type IN ('in_invoice', 'in_refund')
                    AND am.state = 'posted'
                WHERE p.supplier_rank > 0
                GROUP BY p.id
            )
        """)
```

**Approach 2: Read Group Aggregation**
```python
class ReportPartnerInvoice(models.Model):
    _name = 'report.partner.invoice'
    _description = 'Partner Invoice Report'

    partner_id = fields.Many2one('res.partner', string='Partner')
    move_count = fields.Integer(string='# Invoices')
    total_invoiced = fields.Float(string='Total Invoiced')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, order=False):
        """Override read_group to aggregate from account.move"""
        result = super().read_group(domain, fields, groupby, offset, limit, order)

        if not result:
            return result

        # Convert to proper format
        for record in result:
            if 'partner_id' in record and isinstance(record['partner_id'], tuple):
                record['partner_id'] = record['partner_id'][0]

        return result
```

### 2.2 Report Templates

Template QWeb menggunakan sintaks khusus:

**Basic Syntax:**
```xml
<!-- Variable output -->
<span t-esc="expression"/>

<!-- Conditional -->
<t t-if="condition">
    Content here
</t>

<!-- Loop -->
<t t-foreach="records" t-as="record">
    <span t-esc="record.name"/>
</t>

<!-- Call other template -->
<t t-call="module.template_name"/>

<!-- Set variable -->
<t t-set="var_name" t-value="expression"/>
```

**Advanced Patterns:**
```xml
<!-- Formatting currency -->
<span t-esc="amount" t-options="{'widget': 'monetary', 'display_currency': currency_id}"/>

<!-- Date formatting -->
<span t-esc="date_field" t-options="{'widget': 'date'}"/>
<span t-esc="datetime_field" t-options="{'widget': 'datetime'}"/>

<!-- Conditional classes -->
<span t-attf-class="badge #{'success' if status == 'paid' else 'warning'}">

<!-- HTML content -->
<div t-raw="html_content"/>

<!-- Iteration with index -->
<t t-foreach="records" t-as="record">
    <span t-esc="record_index"/> - <span t-esc="record.name"/>
</t>
```

### 2.3 Print Actions

Print actions mengontrol bagaimana laporan dipanggil dan diproses:

```xml
<!-- views/report_actions.xml -->
<odoo>
    <data>
        <!-- Report dengan wizard -->
        <record id="action_vendor_report_wizard" model="ir.actions.report">
            <field name="name">Vendor Report</field>
            <field name="model">res.partner</field>
            <field name="report_type">qweb-pdf</field>
            <field name="report_name">module.report_vendor</field>
            <field name="report_file">module.report_vendor</field>
            <field name="binding_model_id" ref="base.model_res_partner"/>
            <field name="binding_type">report</field>
            <field name="parser_state">default</field>
        </record>

        <!-- Report Print Menu -->
        <record id="menu_vendor_report" model="ir.actions.act_window">
            <field name="name">Vendor Report</field>
            <field name="res_model">wizard.vendor.report</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
        </record>

        <record id="menu_vendor_report_print" model="ir.values">
            <field name="name">Print Vendor Report</field>
            <field name="key2">client_action_multi</field>
            <field name="model">res.partner</field>
            <field name="value" ref="menu_vendor_report"/>
        </record>
    </data>
</odoo>
```

## Step 3: Analyze Report Design

### 3.1 QWeb Advanced Features

**Multi-company Reports:**
```python
class ReportMultiCompany(models.AbstractModel):
    _name = 'report.multi.company'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Get companies user has access to
        companies = self.env.companies

        return {
            'docs': self.env[self.model].browse(docids),
            'companies': companies,
        }
```

**Custom Fonts:**
```xml
<template id="external_layout_custom" name="Custom Layout">
    <t t-call="web.basic_layout">
        <div class="header">
            <div class="row">
                <div class="col-3">
                    <img t-att-src="image_data_uri(company.logo)" style="max-height: 50px;"/>
                </div>
                <div class="col-9 text-right">
                    <strong t-esc="company.name"/><br/>
                    <span t-esc="company.street"/><br/>
                    <span t-esc="company.city"/> <span t-esc="company.zip"/>
                </div>
            </div>
        </div>
        <div class="article">
            <t t-raw="0"/>
        </div>
        <div class="footer">
            <div class="text-center">
                Page <span class="page"/> of <span class="topage"/>
            </div>
        </div>
    </t>
</template>
```

### 3.2 Bootstrap Integration

QWeb reports dapat menggunakan Bootstrap classes:

```xml
<template id="report_with_bootstrap">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <div class="container">
                        <div class="row">
                            <div class="col-md-12">
                                <h3>Report Title</h3>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">
                                        Metric 1
                                    </div>
                                    <div class="card-body">
                                        <h5 t-esc="o.metric_1"/>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">
                                        Metric 2
                                    </div>
                                    <div class="card-body">
                                        <h5 t-esc="o.metric_2"/>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">
                                        Metric 3
                                    </div>
                                    <div class="card-body">
                                        <h5 t-esc="o.metric_3"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 3.3 Report Design Best Practices

**1. Keep reports modular:**
```xml
<!-- Main template calls sub-templates -->
<template id="report_main">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="module.report_header"/>
            <t t-call="module.report_body"/>
            <t t-call="module.report_footer"/>
        </t>
    </t>
</template>
```

**2. Use consistent styling:**
```css
/* Add to report stylesheet */
.report-table {
    width: 100%;
    border-collapse: collapse;
}
.report-table th,
.report-table td {
    padding: 8px;
    border: 1px solid #ddd;
}
.report-table th {
    background-color: #f5f5f5;
    font-weight: bold;
}
```

**3. Handle large datasets:**
```python
@api.model
def _get_report_values(self, docids, data=None):
    # For large datasets, use pagination
    batch_size = 1000
    docs = self.env[self.model].browse(docids[:batch_size])

    return {
        'docs': docs,
        'total_count': len(docids),
        'showing_count': len(docs),
    }
```

## Step 4: Analyze Advanced Reporting

### 4.1 Read Group Aggregations

read_group adalah powerful untuk aggregasi data:

```python
def get_vendor_summary(self, date_from=None, date_to=None):
    """Get vendor summary menggunakan read_group"""
    domain = [
        ('move_type', 'in', ['in_invoice', 'in_refund']),
        ('state', '=', 'posted'),
    ]

    if date_from:
        domain.append(('invoice_date', '>=', date_from))
    if date_to:
        domain.append(('invoice_date', '<=', date_to))

    result = self.env['account.move'].read_group(
        domain,
        fields=['partner_id', 'amount_total', 'amount_residual', 'id'],
        groupby=['partner_id'],
        orderby='amount_total desc',
    )

    # Process result
    summary = []
    for group in result:
        summary.append({
            'partner': group['partner_id'][1] if group['partner_id'] else 'Unknown',
            'partner_id': group['partner_id'][0] if group['partner_id'] else False,
            'invoice_count': group['id_count'],
            'total_invoiced': group['amount_total'],
            'total_due': group['amount_residual'],
        })

    return summary

def get_monthly_trend(self, partner_id, months=12):
    """Get monthly trend menggunakan read_group dengan interval"""
    domain = [
        ('partner_id', '=', partner_id),
        ('move_type', 'in', ['in_invoice', 'in_refund']),
        ('state', '=', 'posted'),
    ]

    result = self.env['account.move'].read_group(
        domain,
        fields=['invoice_date', 'amount_total'],
        groupby=['invoice_date:month'],
        orderby='invoice_date desc',
        limit=months,
    )

    return result
```

### 4.2 Custom SQL Queries

Untuk query kompleks, raw SQL dapat digunakan:

```python
def get_complex_report(self, date_from, date_to):
    """Execute complex SQL query"""
    query = """
        SELECT
            p.id as partner_id,
            p.name as partner_name,
            p.ref as partner_ref,
            COUNT(am.id) as invoice_count,
            SUM(am.amount_total) as total_invoiced,
            SUM(CASE WHEN am.payment_state = 'paid' THEN am.amount_total ELSE 0 END) as total_paid,
            SUM(am.amount_residual) as total_due,
            MAX(am.invoice_date) as last_invoice,
            AVG(am.amount_total) as avg_invoice
        FROM res_partner p
        INNER JOIN account_move am ON
            am.partner_id = p.id
            AND am.move_type = 'in_invoice'
            AND am.state = 'posted'
            AND am.invoice_date >= %s
            AND am.invoice_date <= %s
        WHERE p.supplier_rank > 0
        GROUP BY p.id, p.name, p.ref
        HAVING SUM(am.amount_total) > 0
        ORDER BY total_invoiced DESC
        LIMIT 50
    """

    self.env.cr.execute(query, (date_from, date_to))
    results = self.env.cr.dictfetchall()

    return results

def get_pivot_data(self, dimension1, dimension2, measure):
    """Get data untuk pivot table"""
    query = """
        SELECT
            {dim1} as row_dim,
            {dim2} as col_dim,
            SUM({measure}) as value
        FROM account_move
        WHERE move_type = 'in_invoice'
            AND state = 'posted'
        GROUP BY {dim1}, {dim2}
        ORDER BY {dim1}
    """.format(
        dim1=dimension1,
        dim2=dimension2,
        measure=measure
    )

    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

### 4.3 Dashboard Widgets

Custom dashboard widgets:

```python
class VendorDashboard(models.Model):
    _name = 'vendor.dashboard'
    _description = 'Vendor Dashboard'

    name = fields.Char()

    @api.model
    def get_kpi_data(self):
        """Get KPI data untuk dashboard"""
        # Total outstanding
        outstanding = self.env['account.move'].search_read(
            [('move_type', '=', 'in_invoice'),
             ('state', '=', 'posted'),
             ('amount_residual', '>', 0)],
            ['amount_residual'],
        )
        total_outstanding = sum(r['amount_residual'] for r in outstanding)

        # Overdue invoices
        overdue = self.env['account.move'].search_read(
            [('move_type', '=', 'in_invoice'),
             ('state', '=', 'posted'),
             ('invoice_date_due', '<', fields.Date.today()),
             ('amount_residual', '>', 0)],
            ['amount_residual'],
        )
        total_overdue = sum(r['amount_residual'] for r in overdue)

        # This month
        today = fields.Date.today()
        month_start = today.replace(day=1)
        month_invoices = self.env['account.move'].search_read(
            [('move_type', '=', 'in_invoice'),
             ('state', '=', 'posted'),
             ('invoice_date', '>=', month_start)],
            ['amount_total'],
        )
        month_total = sum(r['amount_total'] for r in month_invoices)

        return {
            'total_outstanding': total_outstanding,
            'total_overdue': total_overdue,
            'month_total': month_total,
            'overdue_count': len(overdue),
        }
```

## Step 5: Document Report Architecture

### 5.1 Report List Template

Dokumentasi harus mencakup daftar lengkap laporan:

```markdown
# Report Architecture

## Module: vendor_report

### Reports

| Report Name | Type | Model | Description |
|-------------|------|-------|-------------|
| Vendor Summary | PDF | res.partner | Summary of vendor invoices |
| Vendor Detail | PDF | res.partner | Detailed vendor report |
| Vendor XLSX | Excel | res.partner | Export to Excel |
| Vendor Pivot | Pivot | account.move | Pivot analysis |

### Views

| View Name | Type | Model |
|-----------|------|-------|
| Vendor Pivot | Pivot | account.move |
| Vendor Graph | Graph | account.move |
| Vendor Dashboard | Dashboard | account.move |

### Data Sources

- account.move: Invoice data
- res.partner: Vendor information
- account.payment: Payment information
```

## Output Format

## Reporting Analysis

### Report Types

[Summary of recommended report types based on requirements]

### Data Sources

[Description of data sources and models used]

### Custom Modifications

[List of custom reports and modifications]

### Recommendations

[Specific recommendations for reporting solution]
