# Odoo 19 ORM Cheat Sheet

## Model Definition

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _order = 'sequence, name'
    _inherit = 'base.model'  # or ['base.model', 'other.model']
    # _inherits = {'parent.model': 'field_name'}
```

## Field Types

```python
# Basic
name = fields.Char(string='Name', required=True, index=True)
description = fields.Text()
active = fields.Boolean(default=True)
sequence = fields.Integer(default=0)

# Numeric
amount = fields.Float(digits=(16, 2))
price = fields.Monetary(currency_field='currency_id')

# Temporal
date = fields.Date()
datetime = fields.Datetime()
deadline = fields.Date(string='Deadline')

# Relational
parent_id = fields.Many2one('my.model', string='Parent', ondelete='cascade')
child_ids = fields.One2many('my.model', 'parent_id', string='Children')
tag_ids = fields.Many2many('tag.model', string='Tags')
reference = fields.Reference([('model.name', 'Display Name')], string='Reference')

# Special
user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
currency_id = fields.Many2one('res.currency', compute='_compute_currency')
json_data = fields.Json()
xml_id = fields.Char(string='External ID', compute='_compute_xml_id', search='_search_xml_id')
```

## API Decorators

```python
@api.model                    # Model method (self is empty recordset)
@api.depends('field')         # Compute field dependencies
@api.depends_context('ctx')   # Context dependencies
@api.constrains('field')      # Python constraint
@api.onchange('field')        # On change handler
@api.ondelete(at_uninstall=False)  # Unlink check
@api.model_create_multi        # Batch create
@api.readonly                  # Readonly cursor
@api.private                   # Not callable via RPC
```

## Domain Operators

```python
# Basic
[('field', '=', value)]
[('field', '!=', value)]
[('field', '>', value)]
[('field', '<', value)]
[('field', '>=', value)]
[('field', '<=', value)]

# String
[('name', 'like', 'pattern')]
[('name', 'ilike', 'PATTERN')]
[('name', '=like', 'Pat%')]

# List
[('state', 'in', ['draft', 'done'])]
[('state', 'not in', ['cancel'])]

# Null safety
[('date', '=?', date_value)]

# Hierarchy
[('parent_id', 'child_of', parent_id)]
[('id', 'parent_of', record_id)]

# Boolean
[('field', '=', False)]  # NULL check
Domain.TRUE()   # [] - match all
Domain.FALSE()  # [(1,'=',1)] - match none
```

## Domain Composition

```python
# AND (implicit)
[('a', '=', 1), ('b', '=', 2)]

# OR
['|', ('a', '=', 1), ('b', '=', 2)]

# Complex
['|', ('a', '=', 1), '&', ('b', '=', 2), ('c', '=', 3)]
# = (a=1 OR (b=2 AND c=3))

# Programmatic
Domain.AND([domain1, domain2])
Domain.OR([domain1, domain2])
d1 & d2  # AND
d1 | d2  # OR
~d1      # NOT
```

## CRUD Operations

```python
# Create
record = self.env['model'].create({'name': 'Value'})
records = self.env['model'].create([{'name': 'A'}, {'name': 'B'}])

# Read
data = record.read(['name', 'field'])[0]
names = records.mapped('name')

# Write
record.write({'name': 'New', 'active': False})
records.write({'active': False})

# Delete
record.unlink()

# Search
records = self.env['model'].search([('active', '=', True)])
records = self.env['model'].search(domain, offset=0, limit=10, order='name')
count = self.env['model'].search_count(domain)

# Browse
record = self.env['model'].browse(id)
records = self.env['model'].browse([1, 2, 3])

# Copy
copy = record.copy()
copy = record.copy({'name': 'New Name'})
```

## Recordset Operations

```python
# Access
record.id          # Single ID
record._ids        # Tuple of IDs
record.env         # Environment
len(record)        # Count
bool(record)       # Is not empty

# Set operations
rec1 | rec2        # Union
rec1 & rec2        # Intersection
rec1 - rec2        # Difference
rec in records     # Membership

# Transformations
records.filtered(lambda r: r.active)
records.mapped('name')           # List of values
records.mapped('partner_id')    # Recordset of partners
records.sorted('create_date')
records.sorted(lambda r: r.name, reverse=True)
```

## Command Pattern

```python
from odoo.fields import Command

# One2many / Many2many
line_ids = fields.One2many('model.line', 'order_id')

order.write({
    'line_ids': [
        Command.create({'product': 1, 'qty': 5}),
        Command.update(line_id, {'qty': 10}),
        Command.delete(line_id),      # Delete from DB
        Command.unlink(line_id),     # Just remove relation
        Command.link(existing_id),
        Command.clear(),
        Command.set([id1, id2]),     # Replace all
    ]
})
```

## Computed Fields

```python
total = fields.Float(
    compute='_compute_total',
    store=True,               # Persist to DB
    precompute=True,          # Compute before insert
    compute_sudo=True,        # Bypass access rights
    recursive=True,          # For self-dependency
)

@api.depends('price', 'quantity')
def _compute_total(self):
    for rec in self:
        rec.total = rec.price * rec.quantity

# Inverse (writable computed)
@api.depends('first_name', 'last_name')
def _compute_name(self):
    for rec in self:
        rec.name = f"{rec.first_name} {rec.last_name}"

def _inverse_name(self):
    for rec in self:
        parts = rec.name.split(' ', 1)
        rec.first_name = parts[0]
        rec.last_name = parts[1] if len(parts) > 1 else ''

# Search on computed
def _search_name(self, operator, value):
    return [('first_name', operator, value)]
```

## Related Fields

```python
# Simple related
partner_name = fields.Char(related='partner_id.name', store=True)

# With readonly default (need inverse to write)
full_name = fields.Char(
    related='partner_id.full_name',
    inverse='_inverse_full_name',
)
```

## Constraints

```python
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for rec in self:
        if rec.start_date > rec.end_date:
            raise ValidationError("End date must be after start date")

@api.constrains('code')
def _check_unique_code(self):
    for rec in self:
        if self.search_count([('code', '=', rec.code), ('id', '!=', rec.id)]):
            raise ValidationError(f"Code {rec.code} already exists")
```

## Onchange

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.address = self.partner_id.address
        self.phone = self.partner_id.phone
    return {
        'warning': {
            'title': 'Warning Title',
            'message': 'Warning message',
            'type': 'notification',  # or 'dialog'
        }
    }
```

## Environment

```python
env = self.env
env.uid              # Current user ID
env.user             # res.users record
env.company          # Current company
env.companies        # Available companies
env.cr               # Cursor
env.context          # Context dict
env.su               # Superuser mode

# Switching
env = self.with_user(user_id)
env = self.with_context(ctx)
env = self.sudo()
env = self.sudo(user_id)

# Protect fields
with env.protecting(['field1'], records):
    record.write({'field1': 'value'})  # Protected

# Flush
record.flush()
env.flush_all()
env.invalidate_all()
```

## Default Values

```python
# In field definition
active = fields.Boolean(default=True)
price = fields.Float(default=100.0)
data = fields.Json(default=lambda self: {'key': 'value'})

# default_get override
@api.model
def default_get(self, fields):
    result = super().default_get(fields)
    result['field'] = 'default_value'
    return result
```

## Override Patterns

```python
# create
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        vals['field'] = self._prepare_value(vals)
    return super().create(vals_list)

# write
def write(self, vals):
    vals['updated_by'] = self.env.uid
    return super().write(vals)

# unlink
@api.ondelete(at_uninstall=False)
def _unlink_if_not_done(self):
    if self.state == 'done':
        raise UserError("Cannot delete done records")

# copy
def copy(self, default=None):
    default = dict(default or {}, name=f"{self.name} (Copy)")
    return super().copy(default)

# _compute_display_name
def _compute_display_name(self):
    for rec in self:
        rec.display_name = f"[{rec.code}] {rec.name}"
```

## Inheritance

```python
# _inherit - extend model
class Extension(models.Model):
    _name = 'original.model'
    _inherit = 'original.model'

    new_field = fields.Char()
    # Override existing field
    name = fields.Char(string='Custom Label')

# _inherit with _name - new model
class NewModel(models.Model):
    _name = 'new.model'
    _inherit = ['model1', 'model2']

# _inherits - delegation
class Child(models.Model):
    _name = 'child.model'
    _inherits = {'parent.model': 'parent_id'}

    parent_id = fields.Many2one(
        'parent.model',
        required=True,
        ondelete='cascade',
        delegate=True,
    )
```

## SQL Constraints

```python
_sql_constraints = [
    ('unique_name', 'unique(name)', 'Name must be unique!'),
    ('check_positive', 'check(price >= 0)', 'Price must be positive'),
]
```

## Import Reference

```python
# Common imports
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.fields import Command, Domain
from odoo.tools import SQL
```

## Performance Tips

```python
# Good - batch operations
records.write({'field': 'value'})
for rec in records:
    print(rec.name)  # Prefetched

# Bad - N queries
for rec in records:
    self.env['model'].browse(rec.id).write({'field': 'value'})

# Good - mapped
partner_ids = records.mapped('partner_id')

# Good - search with IN
existing = model.search([('id', 'in', target_ids)])

# Flush when needed
record.flush()  # Before accessing from raw SQL
```
