---
name: odoo19-stock-picking
description: Create Stock Picking/Delivery order model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat delivery order, stock transfer, atau extend stock.picking.
---

# Odoo 19 Stock Picking Generator

Skill ini digunakan untuk membuat Stock Picking/Delivery Order models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Membuat delivery order management
- Stock transfer operations
- Extending stock.picking model
- Warehouse operations

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Picking type**: in, out, internal
3. **Fields yang dibutuhkan**: Custom fields

## Extending stock.picking

### Basic Extension
```python
from odoo import models, fields

class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    # Custom fields
    delivery_code = fields.Char(string='Delivery Code')
```

## Complete Picking Extension

```python
from odoo import models, fields, api, _

class StockPickingExtended(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'mail.thread']
    _description = 'Stock Picking (Extended)'

    # Delivery Identification
    delivery_code = fields.Char(
        string='Delivery Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Picking Details
    name = fields.Char(required=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        required=True,
    )

    # Partner Relations
    partner_id = fields.Many2one('res.partner', string='Partner')
    origin = fields.Char(string='Source Document')

    # Location
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
    )

    # Dates
    scheduled_date = fields.Datetime(
        string='Scheduled Date',
        default=fields.Datetime.now,
    )
    date_done = fields.Datetime(string='Date Done')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    # Move Lines
    move_ids = fields.One2many(
        'stock.move',
        'picking_id',
        string='Stock Moves',
    )
    move_line_ids = fields.One2many(
        'stock.move.line',
        'picking_id',
        string='Operations',
    )

    # Custom Fields
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    tracking_number = fields.Char(string='Tracking Number')
    shipping_date = fields.Date(string='Shipping Date')

    # Notes
    note = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('delivery_code', _('New')) == _('New'):
                vals['delivery_code'] = self.env['ir.sequence'].next_by_code(
                    'stock.picking.delivery'
                ) or _('New')
        return super().create(vals_list)

    def button_validate(self):
        """Validate picking"""
        for picking in self:
            picking.write({
                'state': 'done',
                'date_done': fields.Datetime.now(),
            })

    def button_cancel(self):
        """Cancel picking"""
        for picking in self:
            picking.write({'state': 'cancel'})
```

## Stock Move Model

```python
class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    # Custom fields
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
    )
```

## Stock Move Line

```python
class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _inherit = 'stock.move.line'

    # Custom fields
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial Number',
    )
    result_package_id = fields.Many2one(
        'stock.quant.package',
        string='Result Package',
    )
```

## Picking Type

```python
class StockPickingType(models.Model):
    _name = 'stock.picking.type'
    _inherit = 'stock.picking.type'
    _description = 'Picking Type'

    # Can add custom picking types
    code = fields.Selection([
        ('incoming', 'Receipt'),
        ('outgoing', 'Delivery'),
        ('internal', 'Internal Transfer'),
    ], string='Type of Operation', required=True)
```

## View Integration

### Form View
```xml
<record id="view_picking_form_extended" model="ir.ui.view">
    <field name="name">stock.picking.form.extended</field>
    <field name="model">stock.picking</field>
    <field name="inherit_id" ref="stock.view_picking_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="delivery_code"/>
            <field name="carrier_id"/>
        </xpath>
        <xpath expr="//field[@name='scheduled_date']" position="after">
            <field name="shipping_date"/>
            <field name="tracking_number"/>
        </xpath>
    </field>
</record>
```

## Common Operations

### Create Delivery Order
```python
def create_delivery_order(self, partner_id, lines):
    picking = self.env['stock.picking'].create({
        'partner_id': partner_id,
        'picking_type_id': self.env.ref('stock.picking_type_out').id,
        'location_id': self.env.ref('stock.stock_location_stock').id,
        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        'move_ids': [
            (0, 0, {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            }) for line in lines
        ]
    })
    return picking
```

### Transfer Stock
```python
def transfer_stock(self, product_id, qty, from_loc, to_loc):
    move = self.env['stock.move'].create({
        'name': f'Transfer {product_id.name}',
        'product_id': product_id.id,
        'product_uom_qty': qty,
        'product_uom': product_id.uom_id.id,
        'location_id': from_loc.id,
        'location_dest_id': to_loc.id,
    })
    move._action_confirm()
    move._action_assign()
    move.button_validate()
```

## Best Practices

1. **Inherit dari stock.picking** untuk compatibility dengan Warehouse app
2. **Use picking types** untuk different operations
3. **Leverage stock.move** untuk move lines
4. **Integrate dengan delivery** jika perlu shipping
5. **Consider lot/serial** tracking jika diperlukan

## Dependencies

- `stock` (built-in)
- `delivery` (for carrier integration)
- `stock_account` (for valuation)
