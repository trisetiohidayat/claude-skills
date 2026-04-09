---
description: Create demo XML data file with noupdate flags for Odoo 19 modules. Use when user wants to create demo data for a module.
---


# Odoo 19 Demo Data File Creation

This skill creates a demo XML data file following Odoo 19 conventions with proper noupdate flags.

## Overview

Demo data files in Odoo 19 are used to populate demonstration data when a module is installed with demo data enabled. These files use the `noupdate="1"` flag to prevent modifications during module updates.

## Steps to Create Demo Data File

### 1. **Determine File Location**

Demo files should be placed in:
```
{module}/demo/
```

### 2. **File Naming Convention**

Use descriptive names following this pattern:
- `demo_{model_name}.xml` - General demo data for a model
- `demo_{model_name}_{description}.xml` - Specific demo data sets

### 3. **XML Structure**

Create the file with these essential elements:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Demo records go here -->
    </data>
</odoo>
```

### 4. **Create Demo Records**

For each record, use the `<record>` tag with:
- **id**: Unique identifier (external ID)
- **model**: Model name
- **noupdate="1"**: Prevents modification during updates

#### Basic Record Structure

```xml
<record id="demo_record_1" model="res.partner">
    <field name="name">Demo Partner 1</field>
    <field name="email">demo1@example.com</field>
    <field name="customer_rank" eval="1"/>
    <field name="supplier_rank" eval="0"/>
</record>
```

### 5. **Use Common Field Types**

#### Text Fields
```xml
<field name="name">Example Name</field>
<field name="description">This is a demo description</field>
```

#### Numeric Fields
```xml
<field name="price" eval="100.50"/>
<field name="quantity" eval="10"/>
```

#### Date Fields
```xml
<field name="date_order" eval="(DateTime.today() - timedelta(days=7)).strftime('%Y-%m-%d')"/>
<field name="date_from" eval="time.strftime('%Y-%m-01')"/>
```

#### Boolean Fields
```xml
<field name="active" eval="True"/>
<field name="is_company" eval="False"/>
```

#### Selection Fields
```xml
<field name="state">draft</field>
<field name="priority">1</field>
```

#### Many2one Fields
```xml
<field name="user_id" ref="base.user_admin"/>
<field name="company_id" ref="base.main_company"/>
<field name="country_id" ref="base.us"/>
```

#### One2many Fields
```xml
<field name="line_ids" eval="[(6, 0, [
    ref('demo_line_1'),
    ref('demo_line_2')
])]"/>
```

#### Many2many Fields
```xml
<field name="category_id" eval="[(6, 0, [
    ref('base.category_customer'),
    ref('base.category_supplier')
])]"/>
```

### 6. **Link Related Records**

Create parent-child relationships:

```xml
<!-- Parent record -->
<record id="demo_partner_parent" model="res.partner">
    <field name="name">Parent Company</field>
    <field name="is_company" eval="True"/>
</record>

<!-- Child record -->
<record id="demo_partner_child" model="res.partner">
    <field name="name">Child Contact</field>
    <field name="parent_id" ref="demo_partner_parent"/>
    <field name="type">contact</field>
</record>
```

### 7. **Update Module Manifest**

Add the demo file to `__manifest__.py`:

```python
'demo': [
    'demo/demo_res_partner.xml',
    'demo/demo_product_template.xml',
],
```

## Complete Example

### File: `demo/demo_res_partner.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Individual Contact -->
        <record id="demo_partner_1" model="res.partner">
            <field name="name">John Doe</field>
            <field name="email">john.doe@example.com</field>
            <field name="phone">+1-555-0101</field>
            <field name="is_company" eval="False"/>
            <field name="customer_rank" eval="1"/>
            <field name="supplier_rank" eval="0"/>
            <field name="country_id" ref="base.us"/>
            <field name="lang">en_US</field>
            <field name="active" eval="True"/>
        </record>

        <!-- Company -->
        <record id="demo_company_1" model="res.partner">
            <field name="name">Acme Corporation</field>
            <field name="email">info@acme.com</field>
            <field name="phone">+1-555-0200</field>
            <field name="website">www.acme.com</field>
            <field name="is_company" eval="True"/>
            <field name="customer_rank" eval="1"/>
            <field name="supplier_rank" eval="1"/>
            <field name="company_type">company</field>
            <field name="country_id" ref="base.us"/>
        </record>

        <!-- Company with child contacts -->
        <record id="demo_company_2" model="res.partner">
            <field name="name">Tech Solutions Inc</field>
            <field name="email">contact@techsolutions.com</field>
            <field name="is_company" eval="True"/>
            <field name="customer_rank" eval="1"/>
            <field name="country_id" ref="base.us"/>
        </record>

        <record id="demo_contact_1" model="res.partner">
            <field name="name">Jane Smith</field>
            <field name="email">jane@techsolutions.com</field>
            <field name="parent_id" ref="demo_company_2"/>
            <field name="function">Sales Manager</field>
            <field name="is_company" eval="False"/>
        </record>

        <record id="demo_contact_2" model="res.partner">
            <field name="name">Bob Johnson</field>
            <field name="email">bob@techsolutions.com</field>
            <field name="parent_id" ref="demo_company_2"/>
            <field name="function">Technical Lead</field>
            <field name="is_company" eval="False"/>
        </record>
    </data>
</odoo>
```

### File: `demo/demo_product_template.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Product Category -->
        <record id="demo_category_services" model="product.category">
            <field name="name">Services</field>
            <field name="parent_id" ref="product.product_category_all"/>
        </record>

        <!-- Service Product -->
        <record id="demo_service_1" model="product.template">
            <field name="name">Consulting Service</field>
            <field name="type">service</field>
            <field name="categ_id" ref="demo_category_services"/>
            <field name="list_price" eval="150.0"/>
            <field name="standard_price" eval="75.0"/>
            <field name="description">Professional consulting services</field>
            <field name="sale_ok" eval="True"/>
            <field name="purchase_ok" eval="False"/>
            <field name="uom_id" ref="uom.product_uom_hour"/>
            <field name="uom_po_id" ref="uom.product_uom_hour"/>
        </record>

        <!-- Consumable Product -->
        <record id="demo_product_1" model="product.template">
            <field name="name">Office Supplies</field>
            <field name="type">consu</field>
            <field name="categ_id" ref="product.product_category_all"/>
            <field name="list_price" eval="25.0"/>
            <field name="standard_price" eval="10.0"/>
            <field name="description">General office supplies</field>
            <field name="sale_ok" eval="True"/>
            <field name="purchase_ok" eval="True"/>
            <field name="uom_id" ref="uom.product_uom_unit"/>
            <field name="uom_po_id" ref="uom.product_uom_unit"/>
        </record>

        <!-- Stockable Product with Variants -->
        <record id="demo_product_2" model="product.template">
            <field name="name">Office Chair</field>
            <field name="type">product</field>
            <field name="categ_id" ref="product.product_category_all"/>
            <field name="list_price" eval="299.0"/>
            <field name="standard_price" eval="150.0"/>
            <field name="description">Ergonomic office chair</field>
            <field name="sale_ok" eval="True"/>
            <field name="purchase_ok" eval="True"/>
            <field name="tracking">lot</field>
        </record>

        <!-- Product Variant -->
        <record id="demo_product_variant_1" model="product.product">
            <field name="product_tmpl_id" ref="demo_product_2"/>
            <field name="name">Office Chair - Black</field>
            <field name="default_code">CHAIR-BLK</field>
        </record>

        <record id="demo_product_variant_2" model="product.product">
            <field name="product_tmpl_id" ref="demo_product_2"/>
            <field name="name">Office Chair - Gray</field>
            <field name="default_code">CHAIR-GRY</field>
        </record>
    </data>
</odoo>
```

## Best Practices

### 1. **Use Descriptive IDs**
```xml
<!-- Good -->
<record id="demo_partner_admin_user" model="res.partner">

<!-- Avoid -->
<record id="demo_1" model="res.partner">
```

### 2. **Use External ID References**
Always use `ref()` to reference other records:
```xml
<field name="country_id" ref="base.us"/>
<field name="parent_id" ref="demo_company_1"/>
```

### 3. **Set noupdate Flags**
Prevent accidental modifications:
```xml
<record id="demo_record" model="model.name" noupdate="1">
```

### 4. **Use Python Expressions**
For computed values:
```xml
<field name="amount_total" eval="100.0 * 1.20"/>
<field name="date_start" eval="(DateTime.today()).strftime('%Y-%m-%d')"/>
```

### 5. **Add Meaningful Data**
Create realistic demo data that helps users understand the module's functionality.

### 6. **Organize Records**
Group related records and add comments:
```xml
<!-- Customer Group -->
<record id="demo_customer_1" model="res.partner">
    ...
</record>

<!-- Supplier Group -->
<record id="demo_supplier_1" model="res.partner">
    ...
</record>
```

### 7. **Use Proper Data Types**
Match field types with appropriate XML attributes:
- Text: `<field name="name">Value</field>`
- Integer: `<field name="count" eval="10"/>`
- Float: `<field name="price" eval="99.99"/>`
- Boolean: `<field name="active" eval="True"/>`

## Common Patterns

### Date Calculations
```xml
<field name="date_from" eval="time.strftime('%Y-%m-01')"/>
<field name="date_to" eval="(DateTime.today() + relativedelta(months=1, day=1, days=-1)).strftime('%Y-%m-%d')"/>
<field name="create_date" eval="(DateTime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')"/>
```

### Sequence Generation
```xml
<field name="code">DEMO/{year}/{month:02d}</field>
```

### Conditional Values
```xml
<field name="amount" eval="100.0 if record.type == 'service' else 50.0"/>
```

### Search References
```xml
<field name="user_id" search="[('login', '=', 'admin')]" model="res.users"/>
```

## Module Manifest Integration

Update `__manifest__.py`:

```python
{
    'name': 'Your Module Name',
    'version': '19.0.1.0.0',
    'category': 'Category',
    'summary': 'Module description',
    'description': 'Long description',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'product',
    ],
    'data': [
        # ...
    ],
    'demo': [
        'demo/demo_res_partner.xml',
        'demo/demo_product_template.xml',
    ],
    'installable': True,
    'application': True,
}
```

## Usage Examples

### Example 1: Create Demo Partners
```bash
/data-demo module=my_module model=res.partner records=10
```

### Example 2: Create Demo Products
```bash
/data-demo module=my_module model=product.template records=5 file_name=demo_products.xml
```

### Example 3: Create Demo Sale Orders
```bash
/data-demo module=sale_custom model=sale.order records=15
```

## Notes

- Demo data is only loaded when installing with demo data enabled
- Use `noupdate="1"` to preserve demo data during module updates
- Keep demo data realistic and meaningful
- Test demo data loading with `--init your_module` and `--demo` flags
- Use external IDs for all cross-references
- Ensure all referenced records exist (dependencies in manifest)
