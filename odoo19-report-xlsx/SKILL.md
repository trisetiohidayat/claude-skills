---
description: Create XLSX report using report_xlsx library for Odoo 19. Use when user wants to create an Excel report.
---


# Odoo 19 XLSX Report Creation

Create an XLSX report using the report_xlsx library following Odoo 19 conventions, including report action XML, Python report class with workbook generation, cell formatting, and multi-sheet support.

## Instructions

1. **Ensure report_xlsx dependency:**
   - Add 'report_xlsx' to dependencies in __manifest__.py
   - Install the report_xlsx module in Odoo

2. **Determine the file locations:**
   - Report action XML: `{module_name}/report/{report_name}_report.xml`
   - Python report class: `{module_name}/report/{report_name}.py`

3. **Create the report action XML:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="{report_name}_action"
            string="{report_title}"
            model="{model_name}"
            report_type="xlsx"
            name="{module_name}.{report_name}"
            attachment="{attachment}"/>
    </data>
</odoo>
```

4. **Create the Python report class:**

```python
from odoo import models

class {ReportClassName}(models.AbstractModel):
    _name = 'report.{module_name}.{report_name}'
    _inherit = 'report.report_xlsx.abstract'
    _description = '{report_title} XLSX Report'

    def generate_xlsx_report(self, workbook, data, records):
        # Create sheet
        sheet = workbook.add_worksheet('{Sheet Name}')

        # Add formats
        bold_format = workbook.add_format({'bold': True})
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFF00',
            'border': 1,
        })

        # Set column widths
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 30)

        # Write headers
        sheet.write(0, 0, 'Header 1', header_format)
        sheet.write(0, 1, 'Header 2', header_format)

        # Write data
        row = 1
        for record in records:
            sheet.write(row, 0, record.field1)
            sheet.write(row, 1, record.field2)
            row += 1
```

5. **Update __manifest__.py:**

```python
'depends': [
    'base',
    'report_xlsx',  # Add this dependency
    # ... other dependencies
],
'data': [
    # ...
    'report/{report_name}_report.xml',
],
```

6. **Update report/__init__.py:**
```python
from . import {report_name}
```

7. **Common workbook operations:**
   - `workbook.add_worksheet(name)` - Create new sheet
   - `workbook.add_format(options)` - Create cell format
   - `workbook.add_chart(options)` - Create chart
   - `sheet.write(row, col, data, format)` - Write cell
   - `sheet.write_row(row, col, data, format)` - Write row
   - `sheet.write_column(row, col, data, format)` - Write column
   - `sheet.merge_range(first_row, first_col, last_row, last_col, data, format)` - Merge cells
   - `sheet.set_column(col_range, width)` - Set column width
   - `sheet.set_row(row, height)` - Set row height

8. **Format options:**
   - `bold: True` - Bold text
   - `italic: True` - Italic text
   - `font_size: 12` - Font size
   - `font_color: 'red'` - Font color
   - `bg_color: '#FFFF00'` - Background color
   - `align: 'left/center/right'` - Horizontal alignment
   - `valign: 'top/vcenter/bottom'` - Vertical alignment
   - `border: 1` - Border width
   - `num_format: '#,##0.00'` - Number format
   - `num_format: 'dd/mm/yyyy'` - Date format

## Usage Examples

### Basic XLSX Report

```bash
/report-xlsx library_book book_xlsx "Library Book XLSX" book.library
```

Output:
```xml
<!-- library_book/report/book_xlsx_report.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="book_xlsx_action"
            string="Library Book XLSX"
            model="book.library"
            report_type="xlsx"
            name="library_book.book_xlsx"/>
    </data>
</odoo>
```

```python
# library_book/report/book_xlsx.py
from odoo import models

class BookXlsx(models.AbstractModel):
    _name = 'report.library_book.book_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Library Book XLSX Report'

    def generate_xlsx_report(self, workbook, data, books):
        # Create sheet
        sheet = workbook.add_worksheet('Books')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
        })

        # Set column widths
        sheet.set_column('A:A', 10)  # ID
        sheet.set_column('B:B', 40)  # Title
        sheet.set_column('C:C', 20)  # ISBN
        sheet.set_column('D:D', 30)  # Author

        # Write title
        sheet.merge_range('A1:D1', 'Library Books Report', title_format)

        # Write headers
        sheet.write(2, 0, 'ID', header_format)
        sheet.write(2, 1, 'Title', header_format)
        sheet.write(2, 2, 'ISBN', header_format)
        sheet.write(2, 3, 'Authors', header_format)

        # Write data
        row = 3
        for book in books:
            sheet.write(row, 0, book.id)
            sheet.write(row, 1, book.name)
            sheet.write(row, 2, book.isbn or '')

            # Get authors
            authors = ', '.join([author.name for author in book.author_ids])
            sheet.write(row, 3, authors)

            row += 1
```

### Sales Order XLSX Report with Formatting

```bash
/report-xlsx sale_order sale_order_xlsx "Sales Order XLSX" sale.order attachment="'SO-' + object.name + '.xlsx'"
```

Output:
```xml
<!-- sale_order/report/sale_order_xlsx_report.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="sale_order_xlsx_action"
            string="Sales Order XLSX"
            model="sale.order"
            report_type="xlsx"
            name="sale_order.sale_order_xlsx"
            attachment="'SO-' + object.name + '.xlsx'"/>
    </data>
</odoo>
```

```python
# sale_order/report/sale_order_xlsx.py
from odoo import models
from datetime import datetime

class SaleOrderXlsx(models.AbstractModel):
    _name = 'report.sale_order.sale_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Sales Order XLSX Report'

    def generate_xlsx_report(self, workbook, data, orders):
        for order in orders:
            # Create sheet for each order
            sheet_name = order.name[:31]  # Excel sheet name max 31 chars
            sheet = workbook.add_worksheet(sheet_name)

            # Define formats
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
            })

            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1,
                'align': 'center',
            })

            cell_format = workbook.add_format({
                'border': 1,
                'valign': 'vcenter',
            })

            currency_format = workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
            })

            date_format = workbook.add_format({
                'num_format': 'dd/mm/yyyy',
                'border': 1,
            })

            # Set column widths
            sheet.set_column('A:A', 5)
            sheet.set_column('B:B', 40)
            sheet.set_column('C:C', 15)
            sheet.set_column('D:D', 15)
            sheet.set_column('E:E', 15)

            # Write title
            sheet.merge_range('A1:E1', 'Sales Order: %s' % order.name, title_format)
            sheet.set_row(0, 30)

            # Write order info
            sheet.write(2, 0, 'Customer:', header_format)
            sheet.write(2, 1, order.partner_id.name, cell_format)

            sheet.write(3, 0, 'Order Date:', header_format)
            sheet.write(3, 1, order.date_order, date_format)

            sheet.write(4, 0, 'State:', header_format)
            sheet.write(4, 1, order.state, cell_format)

            # Write table headers
            row = 6
            sheet.write(row, 0, '#', header_format)
            sheet.write(row, 1, 'Product', header_format)
            sheet.write(row, 2, 'Quantity', header_format)
            sheet.write(row, 3, 'Unit Price', header_format)
            sheet.write(row, 4, 'Subtotal', header_format)

            # Write order lines
            row += 1
            for line in order.order_line:
                sheet.write(row, 0, line.sequence, cell_format)
                sheet.write(row, 1, line.product_id.name, cell_format)
                sheet.write(row, 2, line.product_uom_qty, cell_format)
                sheet.write(row, 3, line.price_unit, currency_format)
                sheet.write(row, 4, line.price_subtotal, currency_format)
                row += 1

            # Write totals
            row += 1
            sheet.write(row, 3, 'Untaxed Amount:', header_format)
            sheet.write(row, 4, order.amount_untaxed, currency_format)

            row += 1
            sheet.write(row, 3, 'Tax:', header_format)
            sheet.write(row, 4, order.amount_tax, currency_format)

            row += 1
            sheet.write(row, 3, 'Total:', header_format)
            sheet.write(row, 4, order.amount_total, currency_format)
```

### Multi-Sheet XLSX Report

```bash
/report-xlsx purchase_order purchase_xlsx "Purchase Analysis XLSX" purchase.order
```

Output:
```python
# purchase_order/report/purchase_xlsx.py
from odoo import models

class PurchaseXlsx(models.AbstractModel):
    _name = 'report.purchase_order.purchase_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Purchase Analysis XLSX Report'

    def generate_xlsx_report(self, workbook, data, orders):
        # Define common formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'align': 'center',
            'border': 1,
        })

        summary_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFC000',
            'border': 1,
        })

        # Sheet 1: Orders Summary
        sheet1 = workbook.add_worksheet('Orders Summary')
        self._write_orders_summary(sheet1, orders, header_format, summary_format)

        # Sheet 2: Products Detail
        sheet2 = workbook.add_worksheet('Products Detail')
        self._write_products_detail(sheet2, orders, header_format)

        # Sheet 3: Suppliers Analysis
        sheet3 = workbook.add_worksheet('Suppliers Analysis')
        self._write_suppliers_analysis(sheet3, orders, header_format, summary_format)

    def _write_orders_summary(self, sheet, orders, header_format, summary_format):
        """Write orders summary sheet"""
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)

        # Headers
        sheet.write(0, 0, 'Order Reference', header_format)
        sheet.write(0, 1, 'Supplier', header_format)
        sheet.write(0, 2, 'Date', header_format)
        sheet.write(0, 3, 'State', header_format)
        sheet.write(0, 4, 'Total', header_format)

        # Data
        row = 1
        total_amount = 0
        for order in orders:
            sheet.write(row, 0, order.name)
            sheet.write(row, 1, order.partner_id.name)
            sheet.write(row, 2, str(order.date_order))
            sheet.write(row, 3, order.state)
            sheet.write(row, 4, order.amount_total)
            total_amount += order.amount_total
            row += 1

        # Summary
        sheet.write(row, 3, 'TOTAL:', summary_format)
        sheet.write(row, 4, total_amount, summary_format)

    def _write_products_detail(self, sheet, orders, header_format):
        """Write products detail sheet"""
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)

        # Headers
        sheet.write(0, 0, 'Product Code', header_format)
        sheet.write(0, 1, 'Product Name', header_format)
        sheet.write(0, 2, 'Quantity', header_format)
        sheet.write(0, 3, 'Unit Price', header_format)
        sheet.write(0, 4, 'Subtotal', header_format)

        # Data
        row = 1
        for order in orders:
            for line in order.order_line:
                sheet.write(row, 0, line.product_id.default_code or '')
                sheet.write(row, 1, line.product_id.name)
                sheet.write(row, 2, line.product_uom_qty)
                sheet.write(row, 3, line.price_unit)
                sheet.write(row, 4, line.price_subtotal)
                row += 1

    def _write_suppliers_analysis(self, sheet, orders, header_format, summary_format):
        """Write suppliers analysis sheet"""
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)

        # Headers
        sheet.write(0, 0, 'Supplier', header_format)
        sheet.write(0, 1, 'Number of Orders', header_format)
        sheet.write(0, 2, 'Total Amount', header_format)

        # Aggregate data by supplier
        supplier_data = {}
        for order in orders:
            supplier = order.partner_id.name
            if supplier not in supplier_data:
                supplier_data[supplier] = {
                    'count': 0,
                    'amount': 0,
                }
            supplier_data[supplier]['count'] += 1
            supplier_data[supplier]['amount'] += order.amount_total

        # Write data
        row = 1
        grand_total = 0
        for supplier, data in sorted(supplier_data.items()):
            sheet.write(row, 0, supplier)
            sheet.write(row, 1, data['count'])
            sheet.write(row, 2, data['amount'])
            grand_total += data['amount']
            row += 1

        # Summary
        sheet.write(row, 1, 'TOTAL:', summary_format)
        sheet.write(row, 2, grand_total, summary_format)
```

### XLSX Report with Charts

```bash
/report-xlsx sales_report sales_analysis_xlsx "Sales Analysis XLSX" sale.report
```

Output:
```python
# sales_report/report/sales_analysis_xlsx.py
from odoo import models

class SalesAnalysisXlsx(models.AbstractModel):
    _name = 'report.sales_report.sales_analysis_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Sales Analysis XLSX Report'

    def generate_xlsx_report(self, workbook, data, records):
        # Create data sheet
        sheet = workbook.add_worksheet('Sales Data')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
        })

        # Write headers
        sheet.write(0, 0, 'Month', header_format)
        sheet.write(0, 1, 'Sales', header_format)
        sheet.write(0, 2, 'Target', header_format)

        # Write data (example data)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        sales = [50000, 75000, 60000, 80000, 95000, 110000]
        targets = [70000, 70000, 70000, 70000, 70000, 70000]

        row = 1
        for month, sale, target in zip(months, sales, targets):
            sheet.write(row, 0, month)
            sheet.write(row, 1, sale)
            sheet.write(row, 2, target)
            row += 1

        # Create chart
        chart = workbook.add_chart({'type': 'column'})

        # Add series to chart
        chart.add_series({
            'name': ['Sales Data', 0, 1],
            'categories': ['Sales Data', 1, 0, 6, 0],
            'values': ['Sales Data', 1, 1, 6, 1],
            'fill': {'color': '#4F81BD'},
        })

        chart.add_series({
            'name': ['Sales Data', 0, 2],
            'categories': ['Sales Data', 1, 0, 6, 0],
            'values': ['Sales Data', 1, 2, 6, 2],
            'fill': {'color': '#C0504D'},
        })

        # Configure chart
        chart.set_title({'name': 'Sales vs Target'})
        chart.set_x_axis({'name': 'Month'})
        chart.set_y_axis({'name': 'Amount'})
        chart.set_legend({'position': 'bottom'})

        # Insert chart into sheet
        sheet.insert_chart('D2', chart)
```

## Best Practices

1. **Report Structure:**
   - Keep logic simple and organized in separate methods
   - Use descriptive variable names
   - Add comments for complex calculations
   - Separate data processing from formatting

2. **Formatting:**
   - Define formats once and reuse them
   - Use consistent color schemes
   - Apply borders to tables for readability
   - Set appropriate column widths

3. **Performance:**
   - Avoid complex database queries in loops
   - Use search() with proper domains before processing
   - Consider batch processing for large datasets
   - Use precomputed fields when possible

4. **Multi-Sheet Reports:**
   - Use descriptive sheet names (max 31 characters)
   - Keep related data on the same sheet
   - Add summary sheets at the end
   - Maintain consistent formatting across sheets

5. **Data Handling:**
   - Handle None/null values properly
   - Format dates and numbers consistently
   - Validate data before writing
   - Use appropriate number formats

6. **User Experience:**
   - Use meaningful attachment names
   - Add headers and footers
   - Include totals and subtotals
   - Use conditional formatting for emphasis

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── report/
│   ├── __init__.py  # Import report classes
│   ├── {report_name}_report.xml      # Report action
│   └── {report_name}.py              # Python report class
└── models/
    └── {model_file}.py
```

## Common Format Patterns

```python
# Date format
date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

# Currency format
currency_format = workbook.add_format({
    'num_format': '#,##0.00',
    'align': 'right',
})

# Percentage format
percent_format = workbook.add_format({
    'num_format': '0.00%',
    'align': 'right',
})

# Header format
header_format = workbook.add_format({
    'bold': True,
    'bg_color': '#4F81BD',
    'font_color': 'white',
    'align': 'center',
    'border': 1,
})

# Total format
total_format = workbook.add_format({
    'bold': True,
    'bg_color': '#FFC000',
    'top': 1,
})

# Text wrap
text_wrap_format = workbook.add_format({
    'text_wrap': True,
    'valign': 'top',
})
```

## Next Steps

After creating the XLSX report, use:
- `/report-qweb` - Create PDF version of the same report
- `/view-form` - Add print button to form views
- `/security-group` - Configure who can access the report

## Additional Resources

- XlsxWriter documentation: https://xlsxwriter.readthedocs.io/
- report_xlsx module: Provides abstract class for XLSX reports
- Chart types: column, bar, line, pie, scatter, stock
- Format options: fonts, colors, borders, alignment, number formats
