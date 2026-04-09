---
name: odoo19-mrp-bom
description: Create MRP Bill of Materials (BOM) model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat manufacturing BOM, product recipe, atau extend mrp.bom.
---

# Odoo 19 MRP BOM Generator

Skill ini digunakan untuk membuat Bill of Materials models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Membuat manufacturing BOM
- Product recipe/formulation
- Product kit definitions
- Extending mrp.bom

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **BOM type**: Kit, Manufacturing, atau Subassembly
3. **Fields yang dibutuhkan**: Custom fields

## Extending mrp.bom

```python
from odoo import models, fields

class MrpBom(models.Model):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'

    # Custom fields
    bom_code = fields.Char(string='BOM Code')
```

## Complete BOM Extension

```python
from odoo import models, fields, api, _

class MrpBomExtended(models.Model):
    _name = 'mrp.bom'
    _inherit = ['mrp.bom', 'mail.thread']
    _description = 'Bill of Materials (Extended)'

    # BOM Identification
    bom_code = fields.Char(
        string='BOM Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Product
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
    )

    # Quantity
    product_qty = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )

    # BOM Type
    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit'),
        ('subassembly', 'Subassembly'),
    ], string='BoM Type', default='normal', required=True)

    # Routing
    routing_id = fields.Many2one(
        'mrp.routing',
        string='Routing',
    )

    # Cost
    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # BOM Lines
    bom_line_ids = fields.One2many(
        'mrp.bom.line',
        'bom_id',
        string='BoM Lines',
    )

    # Active
    active = fields.Boolean(default=True)

    @api.depends('bom_line_ids.material_cost')
    def _compute_total_cost(self):
        for bom in self:
            bom.total_cost = sum(bom.bom_line_ids.mapped('material_cost'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('bom_code', _('New')) == _('New'):
                vals['bom_code'] = self.env['ir.sequence'].next_by_code(
                    'mrp.bom.code'
                ) or _('New')
        return super().create(vals_list)
```

## BOM Line Model

```python
class MrpBomLine(models.Model):
    _name = 'mrp.bom.line'
    _inherit = 'mrp.bom.line'
    _description = 'Bill of Material Line'

    # Custom fields
    material_cost = fields.Monetary(
        string='Material Cost',
        compute='_compute_material_cost',
        store=True,
    )
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.depends('product_id', 'product_qty')
    def _compute_material_cost(self):
        for line in self:
            line.material_cost = line.product_id.standard_price * line.product_qty
```

## View Integration

```xml
<record id="view_bom_form_extended" model="ir.ui.view">
    <field name="name">mrp.bom.form.extended</field>
    <field name="model">mrp.bom</field>
    <field name="inherit_id" ref="mrp.mrp_bom_form_view"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='product_id']" position="after">
            <field name="bom_code"/>
        </xpath>
        <xpath expr="//field[@name='product_qty']" position="after">
            <field name="total_cost"/>
        </xpath>
    </field>
</record>
```

## Best Practices

1. **Inherit dari mrp.bom** untuk compatibility
2. **Use proper UoM** untuk quantity
3. **Consider phantom BOMs** untuk kits
4. **Link ke routing** untuk manufacturing operations

## Dependencies

- `mrp` (built-in)
- `mrp_subcontracting` (for subcontracting)
