---
name: odoo19-orm
description: >
  Menguasai ORM Odoo 19 secara mendalam berdasarkan source code ORM Odoo 19.
  Gunakan skill ini ketika:
  - Membuat atau memodifikasi model Odoo 19 (Model, TransientModel, AbstractModel)
  - Menggunakan decorator API (@api.model, @api.depends, @api.constrains, @api.onchange, dll)
  - Memahami recordset operations (browse, search, create, write, unlink)
  - Implementasi computed fields, related fields, dan stored fields
  - Memahami field types (Char, Integer, Many2one, One2many, Many2many, Selection, dll)
  - Memahami domain operators dan syntax
  - Implementasi inheritance model (_inherit, _inherits)
  - Implementasi SQL constraints dan Python constraints
  - Mengerti Environment, Registry, dan Record Cache mechanism
  - Optimasi prefetching dan batch operations
  - Override ORM methods dengan benar
  - Command pattern untuk relational fields (Command.CREATE, Command.LINK, dll)
---

# Odoo 19 ORM Mastery

Skill ini berdasarkan source code ORM Odoo 19 yang terletak di:
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/models.py` (7,127 lines - BaseModel)
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/fields.py` (1,939 lines - Field class)
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/environments.py` (964 lines - Environment)
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/domains.py` (1,988 lines - Domain)
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/decorators.py` - API decorators
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/commands.py` - Command enum
- `/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo/orm/model_classes.py` - Model class setup

---

## Table of Contents

1. [Model Types & Class Hierarchy](#1-model-types--class-hierarchy)
2. [Environment & Registry](#2-environment--registry)
3. [Recordset Operations](#3-recordset-operations)
4. [Field Types & Definitions](#4-field-types--definitions)
5. [Computed & Related Fields](#5-computed--related-fields)
6. [API Decorators](#6-api-decorators)
7. [Domain Syntax & Operators](#7-domain-syntax--operators)
8. [CRUD Operations Deep Dive](#8-crud-operations-deep-dive)
9. [Inheritance Mechanisms](#9-inheritance-mechanisms)
10. [Constraints (Python & SQL)](#10-constraints-python--sql)
11. [Prefetching & Cache](#11-prefetching--cache)
12. [Command Pattern (Relational Fields)](#12-command-pattern-relational-fields)
13. [Override Patterns](#13-override-patterns)

---

## 1. Model Types & Class Hierarchy

### Source: `odoo/orm/models.py` (line 334+) dan `odoo/orm/model_classes.py`

Odoo 19 menyediakan 3 base class untuk model:

```python
from odoo import models, fields
from odoo.api import model

# 1. Model - Regular database-persisted models
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

# 2. TransientModel - Temporary data (auto-cleanup)
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    _description = 'My Wizard'

# 3. AbstractModel - Abstract super classes (no table)
class MyMixin(models.AbstractModel):
    _name = 'my.mixin'
    _description = 'My Mixin'
```

### Class Hierarchy

```
object
└── BaseModel (metaclass=MetaModel)      # orm/models.py:334
    ├── Model                           # orm/models.py (defined via _abstract/_transient)
    ├── TransientModel
    └── AbstractModel
```

### MetaModel Metaclass (`orm/models.py` line 206)

`MetaModel.__new__` melakukan:
1. collect semua `_field_definitions` dari parent classes
2. collect semua `_inherits`, `_depends`
3. merge attributes dengan proper precedence
4. setup fields sebelum class creation

### Model Attributes (`orm/models.py` line 370-470)

| Attribute | Default | Description |
|-----------|---------|-------------|
| `_name` | required | Model name (e.g., 'sale.order') |
| `_description` | None | Human-readable name |
| `_table` | auto | SQL table name (default: `_name.replace('.', '_')`) |
| `_inherit` | `()` | Parent models to inherit from |
| `_inherits` | `frozendict()` | Delegation inheritance |
| `_order` | `'id'` | Default sort field |
| `_rec_name` | None | Field for labeling (default: 'name') |
| `_parent_name` | `'parent_id'` | Parent field for tree structure |
| `_parent_store` | False | Enable hierarchical parent_path |
| `_auto` | True | Create DB table automatically |
| `_log_access` | auto | Track create_uid, create_date, etc. |
| `_transient` | False | Is TransientModel |
| `_abstract` | True | Is AbstractModel |
| `_check_company_auto` | False | Auto company consistency check |
| `_allow_sudo_commands` | True | Allow sudo in commands |
| `_depends` | `frozendict()` | External model dependencies |

---

## 2. Environment & Registry

### Source: `orm/environments.py` (line 40+)

`Environment` adalah context untuk operasi ORM:

```python
# Akses environment dari recordset
env = self.env  # Current user's environment
env = record.env

# Components:
env.cr          # cursor (database connection)
env.uid          # current user ID
env.context      # context dict
env.su           # superuser mode flag
```

### Environment Methods (`orm/environments.py` line 126+)

```python
# Access model
Partner = env['res.partner']  # Returns a model registry object

# Check permissions
env.is_superuser()  # bool
env.is_admin()      # bool
env.is_system()     # bool

# Context helpers
env.user            # res.users record
env.company         # current company (main)
env.companies       # available companies
env.lang            # current language

# Registry
env.registry        # Registry object
env.cache           # shared record cache

# Protection (context manager)
with env.protecting(fields_to_protect, records):
    ...
```

### Protection Mechanism (`orm/environments.py` line 392+)

```python
# Protect fields from modification
with self.env.protecting(['field1', 'field2'], self):
    record.write({'field1': 'value'})  # Will be ignored

# Protect specific records
with self.env.protecting([(field, record1)], self):
    record.field = value  # Only affects record1
```

### Registry Class (`orm/registry.py`)

Registry menyimpan semua model classes untuk satu database:
- `registry[model_name]` → model class
- `registry.models` → dict of all models
- `registry.descendants()` → child models via inheritance

---

## 3. Recordset Operations

### Source: `orm/models.py` - Recordset Methods

Recordset adalah collection of records. Selalu iterate dengan `for record in self:`.

### Browse & Search

```python
# Browse - get records by IDs
record = self.env['res.partner'].browse([1, 2, 3])

# Empty recordset
empty = self.env['res.partner']

# Search - returns recordset
partners = self.env['res.partner'].search([
    ('active', '=', True),
    ('country_id.code', '=', 'ID')
])
```

### Recordset Properties (`orm/models.py` line 362 - __slots__)

```python
record.env        # Environment
record._ids       # Tuple of record IDs
record._prefetch_ids  # IDs for prefetching

# Single record check
record.id         # integer ID (bukan tuple jika single)
bool(record)      # False if empty
len(record)       # Number of records
```

### Recordset Operations

```python
# Union
rec1 | rec2

# Intersection
rec1 & rec2

# Difference
rec1 - rec2

# Check membership
rec1 in rec2

# Filter
filtered = records.filtered(lambda r: r.active)

# Map
names = records.mapped(lambda r: r.name)

# Sorted
sorted_records = records.sorted(lambda r: r.create_date, reverse=True)

# Concat
concat_records = rec1 + rec2

# Exercise caution with mapped - it can return non-recordset types
names_list = records.mapped('name')  # Returns list of values, not records
partner_records = records.mapped('partner_id')  # Returns recordset of partners
```

---

## 4. Field Types & Definitions

### Source: `orm/fields.py` (line 92+) dan sub-modules

### Field Base Attributes (`orm/fields.py` line 248+)

```python
class Char(fields.Field):
    type = 'char'
    _column_type = ('varchar', 'varchar')

    def __init__(self, string=..., **kwargs):
        # string: label (required)
        # help: tooltip
        # readonly: default False
        # required: default False
        # index: 'btree'|'btree_not_null'|'trigram'|None
        # default: value or callable
        # groups: 'base.group_user' (comma-separated)
        # company_dependent: bool
        # copy: bool (default True, except computed)
        # store: bool (default True, False for computed)
        # translate: bool (for text fields)
        # groups: access control
        super().__init__(string=string, **kwargs)
```

### Field Types di Odoo 19

| Field Type | Module | Description |
|------------|--------|-------------|
| `Char` | `fields_textual.py` | String field |
| `Text` | `fields_textual.py` | Multiline text |
| `Html` | `fields_textual.py` | HTML content |
| `Integer` | `fields_numeric.py` | Integer number |
| `Float` | `fields_numeric.py` | Floating point |
| `Monetary` | `fields_numeric.py` | Currency amount |
| `Boolean` | `fields_selection.py` | True/False |
| `Date` | `fields_temporal.py` | Date only |
| `Datetime` | `fields_temporal.py` | Date + time |
| `Binary` | `fields_binary.py` | File data |
| `Selection` | `fields_selection.py` | Dropdown enum |
| `Many2one` | `fields_relational.py` | Foreign key → one |
| `One2many` | `fields_relational.py` | Inverse of M2O → many |
| `Many2many` | `fields_relational.py` | Many-to-many |
| `Reference` | `fields_reference.py` | Dynamic reference |
| `Properties` | `fields_properties.py` | Dynamic properties |
| `Json` | `fields_misc.py` | JSON data |
| `Xmlid` | `fields_misc.py` | External ID |

### Field Parameters

```python
# Basic parameters
name = fields.Char(
    string='Name',           # Label
    help='Tooltip text',    # Help text
    readonly=True,          # Read-only
    required=True,          # Mandatory
    index='btree',          # Database index
    default='value',        # or default=lambda self: ...
    groups='base.group_user',  # Access groups
    copy=False,             # Don't copy on duplicate
    store=True,             # Stored in DB
    related='partner_id.name',  # Related field
    compute='_compute_name',   # Computed field
    inverse='_inverse_name',   # Inverse operation
    search='_search_name',     # Custom search
    precompute=True,        # Compute before insert
    compute_sudo=True,       # Bypass access rights
)

# Selection field
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirm', 'Confirmed'),
    ('done', 'Done'),
], string='Status', default='draft')

# Many2one
partner_id = fields.Many2one(
    'res.partner',
    string='Partner',
    ondelete='cascade',  # 'cascade', 'restrict', 'set null'
)

# One2many (inverse of Many2one)
line_ids = fields.One2many(
    'sale.order.line',
    'order_id',  # inverse field
    string='Order Lines',
)

# Many2many
tag_ids = fields.Many2many(
    'res.partner.category',
    'res_partner_res_partner_category_rel',  # auto if omitted
    'partner_id',
    'category_id',
    string='Tags',
)

# Company-dependent (property field)
property_product_pricelist = fields.Many2one(
    'product.pricelist',
    company_dependent=True,
    string='Pricelist',
)
```

### Relational Field Parameters

```python
# Many2one specific
partner_id = fields.Many2one(
    'res.partner',
    index=True,              # Add index
    tracking=True,          # Enable mail tracking
    check_company=True,      # Check company consistency
    ondelete='restrict',     # 'cascade', 'restrict', 'null', 'cascade'
)

# Context for active_id, etc.
wizard_line_ids = fields.Many2one(
    'wizard.line',
    context={'active_id': active_id},
)

# Domain filter
user_id = fields.Many2one(
    'res.users',
    domain=[('active', '=', True)],
)
```

---

## 5. Computed & Related Fields

### Source: `orm/fields.py` line 202+ dan `orm/models.py`

### Computed Fields

```python
# Definition
total_amount = fields.Float(
    compute='_compute_total',
    store=True,           # Store in DB (recomputed on dependency change)
    precompute=True,       # Compute before insert
)

# Compute method
@api.depends('price_unit', 'quantity', 'tax_ids')
def _compute_total(self):
    for record in self:
        record.total_amount = record.price_unit * record.quantity
```

### @api.depends Details

```python
# Single field dependency
@api.depends('field_a')

# Multiple field dependencies
@api.depends('field_a', 'field_b')

# Dot notation for related fields
@api.depends('partner_id.country_id.code')

# Callable as dependency
@api.depends(lambda self: self.mapped('line_ids.amount'))

# Recursive dependencies (must declare!)
parent_total = fields.Float(
    compute='_compute_parent_total',
    recursive=True,
    store=True,
)
```

### @api.depends_context

```python
# Context-dependent computation
amount = fields.Float(
    compute='_compute_amount',
    depends_context=['company', 'currency'],
)

@api.depends_context('company', 'currency')
def _compute_amount(self):
    company = self.env.company
    currency = self.env.context.get('currency') or company.currency_id
    for record in self:
        record.amount = currency.compute(record.amount_company, record)
```

### Inverse Fields (Writable Computed)

```python
# Read-write computed field
full_name = fields.Char(
    compute='_compute_full_name',
    inverse='_inverse_full_name',
    store=True,
)

def _compute_full_name(self):
    for record in self:
        record.full_name = f"{record.first_name} {record.last_name}"

def _inverse_full_name(self):
    for record in self:
        parts = record.full_name.split(' ', 1)
        record.first_name = parts[0]
        record.last_name = parts[1] if len(parts) > 1 else ''
```

### Search on Computed Fields

```python
full_name = fields.Char(
    compute='_compute_full_name',
    search='_search_full_name',
)

def _search_full_name(self, operator, value):
    # Return a domain that filters by computed value
    return [
        '|',
        ('first_name', operator, value),
        ('last_name', operator, value),
    ]
```

### Related Fields (Shorthand for Computed + Related)

```python
# Automatically creates: compute, inverse, and search
country_name = fields.Char(
    related='partner_id.country_id.name',
    string='Country Name',
    store=True,  # Optional: store in DB
)
```

---

## 6. API Decorators

### Source: `orm/decorators.py`

### @api.model

```python
# self is a recordset but contents not relevant
# No access rights checks on record contents
# Used for model-level operations

@api.model
def get_sequence(self, code):
    # self may be empty or have any records
    return self.env['ir.sequence'].search([('code', '=', code)])

# Note: @api.model on create() auto-applies @model_create_multi
```

### @api.model_create_multi

```python
# Allows calling create with single dict OR list of dicts
record = model.create({'name': 'A'})
records = model.create([{'name': 'A'}, {'name': 'B'}])

# Implementation
@api.model
@api.model_create_multi
def create(self, vals_list):
    # vals_list is always a list
    for vals in vals_list:
        ...
    return records
```

### @api.depends (see Computed Fields)

### @api.constrains

```python
# Decorator untuk Python constraints
# Dipanggil ketika field yang di-list berubah

@api.constrains('name', 'partner_id')
def _check_name(self):
    for record in self:
        if not record.name:
            raise ValidationError("Name is required")

# Warning: tidak dipanggil jika field tidak ada di vals!
# Gunakan override create() jika perlu always check
```

### @api.onchange

```python
# Dipanggil dari form view saat field berubah
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.address = self.partner_id.address

# Return warning/notification
return {
    'warning': {
        'title': 'Warning',
        'message': 'Invalid quantity',
        'type': 'notification',  # atau 'dialog'
    }
}

# Catatan:
# - self adalah pseudo-record (belum tentu ada di DB)
# - CRUD operations tidak boleh dipanggil
# - Hanya set field values
```

### @api.ondelete

```python
# Dipanggil saat record akan di-delete

@api.ondelete(at_uninstall=False)
def _unlink_if_active(self):
    if self.active:
        raise UserError("Cannot delete active records")

# at_uninstall=True: tetap dipanggil saat uninstall module
# at_uninstall=False: tidak dipanggil saat uninstall (biasanya)
```

### @api.depends_context (see Computed Fields)

### @api.readonly

```python
# Boleh dipanggil dengan readonly cursor via RPC

@api.model
@api.readonly
def get_data(self):
    # Bisa dijalankan dengan cursor readonly
    ...
```

### @api.private

```python
# Tidak bisa dipanggil via RPC

@api.model
@api.private
def _internal_method(self):
    ...
```

### @api.autovacuum

```python
# Dipanggil oleh daily vacuum cron

@api.autovacuum
def _cleanup_old_records(self):
    # Return (done, remaining)
    old = self.search([('create_date', '<', fields.Date.today() - 30)])
    old.unlink()
    return (len(old), 0)
```

---

## 7. Domain Syntax & Operators

### Source: `orm/domains.py` (line 184+)

### Domain Structure

```python
# Domain = [(field, operator, value), ...]
# AND implicit between tuples
# OR explicit dengan '&' atau '|'

[('field', 'operator', value)]

# Multiple conditions (AND)
[('field1', '=', 'a'), ('field2', '>', 5)]

# OR conditions
['|', ('field1', '=', 'a'), ('field2', '=', 'b')]

# NOT
('field', '!=', 'value')  # simplified
'!', ('field', '=', 'value')  # explicit

# Nested with parentheses (using Domain class)
Domain('|', ('a', '=', 1), ('b', '=', 2))
```

### Domain Operators (`orm/domains.py` line 333+ dan `orm/utils.py`)

| Operator | SQL Equivalent | Description |
|----------|----------------|-------------|
| `=` | `=` | Equal |
| `!=` | `<>` | Not equal |
| `>` | `>` | Greater than |
| `<` | `<` | Less than |
| `>=` | `>=` | Greater or equal |
| `<=` | `<=` | Less or equal |
| `=?` | `IS NOT DISTINCT FROM` | None-safe equality |
| `=like` | `LIKE` | SQL LIKE with `%` |
| `=ilike` | `ILIKE` | Case-insensitive LIKE |
| `like` | `LIKE` | Pattern with `%` |
| `ilike` | `ILIKE` | Case-insensitive pattern |
| `not like` | `NOT LIKE` | No match |
| `not ilike` | `NOT ILIKE` | No match (case-ins) |
| `in` | `IN` | Value in list |
| `not in` | `NOT IN` | Value not in list |
| `child_of` | `child_of` | Record hierarchy |
| `parent_of` | `parent_of` | Record hierarchy |

### Special Operators

```python
# child_of - records in hierarchy (uses parent_path)
[('parent_id', 'child_of', [1, 2])]  # Children of 1 or 2

# parent_of - records above in hierarchy
[('id', 'parent_of', [5])]  # All ancestors of 5

# in with empty list - always false (no record matches)
[('field', 'in', [])]  # Matches nothing

# =? - None treated as "not specified"
[('date', '=?', None)]  # Matches records where date is NULL
[('date', '=?', some_date)]  # Matches records where date = some_date
```

### Domain on Relational Fields

```python
# Many2one traversal
[('partner_id.country_id.code', '=', 'ID')]

# One2many/Many2many (exists condition)
[('line_ids.product_id', 'in', [1, 2])]  # Has any line with product 1 or 2

# Count condition
[('line_ids', '=', False)]  # No lines
[('line_ids', '!=', False)]  # Has at least one line
```

### Domain Class Methods (`orm/domains.py` line 278+)

```python
from odoo.fields import Domain as DomainClass

# TRUE domain - matches everything
Domain.TRUE()  # [] equivalent

# FALSE domain - matches nothing
Domain.FALSE()  # [(1, '=', 1)] equivalent

# AND/OR combinations
domain1 = [('a', '=', 1)]
domain2 = [('b', '=', 2)]
combined = Domain.AND([domain1, domain2])
combined = Domain.OR([domain1, domain2])

# Optimize domain
optimized = domain.optimize(model)
```

### Domain as Expression Object (`orm/domains.py` line 186+)

```python
from odoo.orm.domains import Domain

# Create domain programmatically
d = Domain('field', '=', 'value')
d = Domain('field1', '=', 1) & Domain('field2', '=', 2)
d = Domain('field1', '=', 1) | Domain('field2', '=', 2)
d = ~Domain('field', '=', 'value')  # Negation

# Validate domain
d.validate(model)

# Iterate conditions
for condition in d.iter_conditions():
    print(condition)
```

---

## 8. CRUD Operations Deep Dive

### Source: `orm/models.py` - CRUD Methods

### create()

```python
# Create single record
record = self.env['my.model'].create({'name': 'Test'})

# Create multiple records (batch)
records = self.env['my.model'].create([
    {'name': 'Test 1'},
    {'name': 'Test 2'},
])

# Internal flow (models.py):
# 1. _add_missing_default_values()
# 2. _validate_fields()
# 3. _compute_data_for_graph()
# 4. Insert into DB
# 5. _validate_fields() untuk stored computed fields
# 6. invalidate_cache()
```

### write()

```python
# Update single field
record.write({'name': 'New Name'})

# Update multiple fields
record.write({
    'name': 'New Name',
    'active': False,
})

# Update multiple records
records.write({'active': False})

# Special field handling:
# - many2one: set ID atau False
# - one2many: [(Command.create, 0, vals), ...]
# - many2many: [(Command.set, 0, [id1, id2]), ...]
```

### read()

```python
# Read all fields
data = record.read()[0]  # Returns list with one dict

# Read specific fields
data = record.read(['name', 'partner_id'])[0]

# With related fields
data = record.read(['name', 'partner_id.name', 'partner_id.country_id.code'])[0]

# read() returns list of dicts, even for single record
```

### search()

```python
# Basic search
records = self.env['my.model'].search([('active', '=', True)])

# With pagination
records = self.env['my.model'].search(
    [('active', '=', True)],
    offset=10,
    limit=5,
    order='create_date desc',
)

# Search all (empty domain)
all_records = self.env['my.model'].search([])

# Search count only
count = self.env['my.model'].search_count([('active', '=', True)])
```

### unlink()

```python
# Delete records
record.unlink()

# Flow:
# 1. Check @api.ondelete methods
# 2. Cascade delete children (_inherits)
# 3. Delete from DB
# 4. Invalidate cache
```

### copy()

```python
# Copy record with all fields (except defaults)
copy = record.copy()

# Copy with override
copy = record.copy({'name': 'Copy of ' + record.name})

# Fields dengan copy=False tidak di-copy
```

### browse() & flush()

```python
# Browse by IDs
records = self.env['my.model'].browse([1, 2, 3])

# Flush pending writes
record.flush()  # Flush specific record
self.flush()    # Flush all in recordset
self.env.flush_all()  # Flush everything

# Invalidate cache
self.env.invalidate_all()
```

### filtered() & sorted()

```python
# Filter
active = records.filtered(lambda r: r.active)
by_partner = records.filtered(lambda r: r.partner_id == partner)

# Sorted
ordered = records.sorted(lambda r: r.sequence)
ordered = records.sorted('create_date', reverse=True)

# mapped - collect values or traverse relations
names = records.mapped('name')  # List of names
partners = records.mapped('partner_id')  # Recordset of partners
lines = records.mapped('line_ids')  # Recordset of all lines
```

---

## 9. Inheritance Mechanisms

### Source: `orm/models.py` (line 396+) dan `orm/model_classes.py`

### _inherit (Extension)

```python
# Extend existing model (in-place)
class MyExtension(models.Model):
    _inherit = 'res.partner'

    new_field = fields.Char('New Field')

# Result: res.partner sekarang punya new_field
```

### _inherit with _name (New Model)

```python
# Create new model inheriting from another
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['res.partner', 'mail.thread']

# Creates 'my.model' dengan semua fields dari res.partner + mail.thread
```

### _inherits (Delegation)

```python
# Composition-based inheritance
# Does NOT create new table - delegates to parent table

class MyUser(models.Model):
    _name = 'my.user'
    _inherits = {
        'res.users': 'user_id',
    }

    user_id = fields.Many2one(
        'res.users',
        required=True,
        ondelete='cascade',
        delegate=True,  # Required for _inherits
    )

# my.user has all res.users fields via delegation
# Reading user_id.name returns res.users.name
# Writing user_id.name writes to res.users record
```

### Model Class Setup (`orm/model_classes.py`)

```python
# Model class creation flow:
# 1. MetaModel.__new__() collects _field_definitions
# 2. Determines base classes (reversed MRO)
# 3. add_to_registry() creates/extends model class
# 4. _prepare_setup() prepares class
# 5. _setup() sets up fields
# 6. _setup_fields() completes field setup
```

### Field Inheritance

```python
# Override field dari parent
class MyExtension(models.Model):
    _inherit = 'res.partner'

    # Override name field
    name = fields.Char(
        string='Partner Name',
        track_visibility='onchange',  # Add tracking
    )
```

---

## 10. Constraints (Python & SQL)

### Source: `orm/models.py` (line 519+)

### Python Constraints with @api.constrains

```python
from odoo.exceptions import ValidationError

@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if record.start_date and record.end_date:
            if record.start_date > record.end_date:
                raise ValidationError(
                    "Start date must be before end date"
                )

@api.constrains('name')
def _check_unique_name(self):
    for record in self:
        if self.search_count([
            ('name', '=', record.name),
            ('id', '!=', record.id),
        ]):
            raise ValidationError(
                "Name must be unique: %s" % record.name
            )
```

### SQL Constraints (model-level)

```python
# Define via _sql_constraints in model
class MyModel(models.Model):
    _name = 'my.model'

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code must be unique'),
        ('check_dates', 'check(start_date <= end_date)', 'Invalid dates'),
    ]

# New Odoo 19 style - using model_attribute
from odoo.orm.table_objects import Constraint

class MyModel(models.Model):
    _name = 'my.model'

    @Constraint(model)
    def unique_code(self):
        return SQL(
            'unique_code',
            'code IS NOT NULL',
            'Code is required',
        )
```

### @api.ondelete (see Decorators)

### Validation with ValidationError

```python
from odoo.exceptions import ValidationError

raise ValidationError("Simple error message")

raise ValidationError(
    "Error with field: %s" % self.env.context.get('field_name')
)

# Also available:
from odoo.exceptions import UserError, AccessError, MissingError
```

---

## 11. Prefetching & Cache

### Source: `orm/models.py` dan `orm/fields.py` (1550+)

### Prefetching Mechanism

```python
# Prefetching: Odoo loads data in batch for efficiency
# DILAKUKAN OTOMATIS, tapi perlu mengerti untuk optimize

# Batch reading (automatic)
for record in records:  # Records loaded in batch
    print(record.name)   # Uses prefetched data

# Prefetch specific fields
records.fetch(['name', 'partner_id'])

# Manual prefetching untuk relations
records.mapped('partner_id.country_id')
```

### Record Cache

```python
# Cache structure (orm/fields.py line 1530+)
# Cache stored per field per environment

# Check cache
if field in record._cache:
    value = record._cache[field]

# Manual cache operations
record.flush()          # Write cache to DB
record.invalidate()     # Invalidate specific field cache
self.env.invalidate_all()  # Invalidate all

# Prefetch IDs untuk batch operations
records._prefetch_ids
```

### Prefetch Tips

```python
# Good: iterate over all records
for record in records:
    print(record.name)  # Single SQL for all

# Bad: iterate over individual records
for record in records:
    individual_record = self.env['model'].browse(record.id)
    print(individual_record.name)  # N SQL queries!

# Good: use mapped for related records
partners = records.mapped('partner_id')  # Single query
```

### Lazy Computation

```python
# Fields tidak di-compute sampai di-access
record.name  # Trigger computation

# force_compute untuk eager computation
record._compute_data_for_graph()
```

---

## 12. Command Pattern (Relational Fields)

### Source: `orm/commands.py`

```python
from odoo.fields import Command

# Command identifiers
Command.CREATE   # = 0  Create new record
Command.UPDATE   # = 1  Update existing record
Command.DELETE   # = 2  Delete record from DB
Command.UNLINK   # = 3  Remove relation only (not delete)
Command.LINK     # = 4  Add existing relation
Command.CLEAR    # = 5  Remove all relations
Command.SET      # = 6  Replace all relations
```

### Using Commands

```python
# One2many field: line_ids (order_id = inverse)

# Create new line (linked to current order)
order.write({
    'line_ids': [
        Command.create({'product_id': 1, 'quantity': 5}),
    ],
})

# Update existing line
order.write({
    'line_ids': [
        Command.update(line_id, {'quantity': 10}),
    ],
})

# Delete line (cascade if ondelete=cascade)
order.write({
    'line_ids': [Command.delete(line_id)],
})

# Unlink (remove relation, keep record)
order.write({
    'line_ids': [Command.unlink(line_id)],
})

# Link to existing line
order.write({
    'line_ids': [Command.link(existing_line_id)],
})

# Clear all lines
order.write({
    'line_ids': [Command.clear()],
})

# Set (replace all)
order.write({
    'line_ids': [Command.set([id1, id2, id3])],
})

# Multiple commands
order.write({
    'line_ids': [
        Command.delete(line1_id),
        Command.create({'product_id': 2, 'quantity': 3}),
        Command.link(existing_line_id),
    ],
})
```

### Command Class Methods (Preferred)

```python
# Instead of raw tuple, use class methods
vals = Command.create({'product_id': 1, 'quantity': 5})
# Returns (0, 0, {'product_id': 1, 'quantity': 5})

vals = Command.update(record_id, {'quantity': 10})
# Returns (1, record_id, {'quantity': 10})

vals = Command.delete(record_id)
# Returns (2, record_id, 0)

# Etc.
```

---

## 13. Override Patterns

### Source: ORM Best Practices

### Safe Override Guidelines

```python
class MyModel(models.Model):
    _name = 'my.model'

    # WRONG - breaks ORM
    def create(self, vals):
        # Missing super()!
        self.env['my.model'].create(vals)

    # RIGHT - call super
    def create(self, vals):
        # Pre-processing
        vals['name'] = self._prepare_name(vals)
        # Call parent
        record = super().create(vals)
        # Post-processing
        record._post_create()
        return record
```

### Super Call Patterns

```python
# Full override with super
def create(self, vals_list):
    # Handle single dict
    if isinstance(vals_list, dict):
        vals_list = [vals_list]

    # Process each
    for vals in vals_list:
        vals['custom_field'] = 'value'

    return super().create(vals_list)

# Calling other methods
@api.model
def default_get(self, fields):
    result = super().default_get(fields)
    result['custom_field'] = 'default'
    return result
```

### Method Resolution Order (MRO)

```python
# When overriding, call super() untuk chain ke parent
# Model class MRO:
# [my.model, my.model.inherit.module1, my.model.inherit.module2, models.Model, BaseModel]

# super() calls next class in MRO
```

### Decorator Patterns for Overrides

```python
# Use same decorator as parent
@api.model
def create(self, vals_list):
    return super().create(vals_list)

# Add new dependencies on computed field
# Must use @api.depends with all dependencies
@api.depends('field_a', 'field_b', 'parent_id.custom_field')
def _compute_custom(self):
    ...
```

### Extension with _inherit

```python
# Module A
class ModelA(models.Model):
    _name = 'my.model'
    _inherit = 'base'

    field_a = fields.Char()

# Module B
class ModelB(models.Model):
    _name = 'my.model'  # Same name extends
    _inherit = 'my.model'

    field_b = fields.Char()

# Result: my.model has field_a AND field_b
```

---

## Common Patterns & Anti-Patterns

### Good Patterns

```python
# Batch operations
for record in self:
    record.write({'state': 'done'})

# Use search with domain
active_records = self.search([('active', '=', True)])

# Use mapped untuk traverse
partner_ids = records.mapped('partner_id')

# Proper error handling
try:
    record.unlink()
except Exception as e:
    raise UserError("Cannot delete: %s" % str(e))
```

### Anti-Patterns

```python
# BAD: N+1 queries
for record in records:
    partner_name = self.env['res.partner'].browse(record.partner_id.id).name

# GOOD: Prefetched
for record in records:
    partner_name = record.partner_id.name

# BAD: Search in loop
for partner in partners:
    if self.search([('partner_id', '=', partner.id)]):
        ...

# GOOD: Single search with IN
partner_ids = partners.ids
existing = self.search([('partner_id', 'in', partner_ids)])

# BAD: Multiple write calls
for record in records:
    record.write({'field': 'value'})

# GOOD: Single write
records.write({'field': 'value'})
```

---

## Reference File Locations

### Key Source Files

| Path | Description |
|------|-------------|
| `odoo19.0-roedl/odoo/odoo/orm/models.py` | BaseModel class (7,127 lines) |
| `odoo19.0-roedl/odoo/odoo/orm/fields.py` | Field class and base fields (1,939 lines) |
| `odoo19.0-roedl/odoo/odoo/orm/fields_relational.py` | Relational fields (M2O, O2M, M2M) |
| `odoo19.0-roedl/odoo/odoo/orm/fields_numeric.py` | Numeric fields (Integer, Float, Monetary) |
| `odoo19.0-roedl/odoo/odoo/orm/fields_temporal.py` | Date/Datetime fields |
| `odoo19.0-roedl/odoo/odoo/orm/fields_textual.py` | Char, Text, Html fields |
| `odoo19.0-roedl/odoo/odoo/orm/fields_selection.py` | Selection, Boolean fields |
| `odoo19.0-roedl/odoo/odoo/orm/environments.py` | Environment class (964 lines) |
| `odoo19.0-roedl/odoo/odoo/orm/domains.py` | Domain class (1,988 lines) |
| `odoo19.0-roedl/odoo/odoo/orm/decorators.py` | API decorators (@api.*) |
| `odoo19.0-roedl/odoo/odoo/orm/commands.py` | Command enum |
| `odoo19.0-roedl/odoo/odoo/orm/model_classes.py` | Model class setup |
| `odoo19.0-roedl/odoo/odoo/orm/registry.py` | Registry class |
| `odoo19.0-roedl/odoo/odoo/orm/utils.py` | ORM utilities |
| `odoo19.0-roedl/odoo/odoo/osv/expression.py` | Domain expression SQL |
