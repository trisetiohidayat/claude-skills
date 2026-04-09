---
name: odoo-code-quality
description: |
  Code quality review dan best practices untuk Odoo development. Gunakan skill ini ketika:
  - Review code untuk quality issues
  - Validasi code patterns dan formatting
  - Check code complexity dan maintainability
  - Ensure adherence to Odoo conventions
  - Refactor existing code

  Fokus pada readability, maintainability, dan Odoo-specific best practices.
---

# Odoo Code Quality Review Skill

## Overview

Skill ini membantu melakukan code quality review terhadap Odoo code untuk memastikan adherence ke best practices dan Odoo conventions.

## Code Quality Checklist

### 1. Naming Conventions

#### ✅ WAJIB: Follow Odoo Naming

| Element | Convention | Example |
|---------|-----------|---------|
| **Model** | `snake_case`, descriptive | `sale.order`, `hr.employee` |
| **Field** | `snake_case` | `partner_id`, `order_line` |
| **Method** | `snake_case`, action-oriented | `def action_confirm()`, `def _compute_total()` |
| **Variable** | `snake_case`, descriptive | `order_ids`, `total_amount` |
| **Class** | `PascalCase` | `class SaleOrder(models.Model):` |
| **Constant** | `UPPER_SNAKE_CASE` | `MAX_AMOUNT = 10000` |

#### ❌ DILARANG

```python
# SALAH - Poor naming
class SO(models.Model):
    x = fields.Char()  # Tidak descriptive
    def do_something(self):  # Tidak action-oriented

# BENAR - Good naming
class SaleOrder(models.Model):
    name = fields.Char(string="Order Reference")
    def action_confirm(self):  # Action-oriented
```

### 2. Code Structure

#### ✅ WAJIB: Organize Code Properly

```python
# Recommended structure
class SaleOrder(models.Model):
    # 1. _name, _description
    _name = 'sale.order'
    _description = 'Sales Order'

    # 2. _inherit (if any)
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # 3. _rec_name (if custom)
    _rec_name = 'name'

    # 4. _order
    _order = 'date_order desc, id'

    # 5. Fields - all field definitions first
    name = fields.Char(...)
    state = fields.Selection(...)
    partner_id = fields.Many2one(...)

    # 6. Computed fields
    amount_total = fields.Float(compute='_compute_amount', store=True)

    # 7. @api.constrains
    @api.constrains('date_order')
    def _check_date(self):
        pass

    # 8. @api.depends (for computed)
    @api.depends('order_line.price_total')
    def _compute_amount(self):
        pass

    # 9. CRUD methods (create, write, unlink)
    def write(self, vals):
        pass

    # 10. Action methods
    def action_confirm(self):
        pass

    # 11. Private methods
    def _prepare_invoice(self):
        pass
```

### 3. Method Organization

#### ✅ Best Practices

| Method Type | Prefix | Example |
|-------------|--------|---------|
| **Action** | `action_` | `action_confirm()`, `action_cancel()` |
| **Compute** | `_compute_` | `_compute_amount_total()` |
| **Onchange** | `_onchange_` | `_onchange_partner_id()` |
| **Constraint** | `_check_` | `_check_date_order()` |
| **Private** | `_` (underscore) | `_prepare_invoice()` |
| **Const** | `_const_` | `_constrains()` |

### 4. Import Organization

#### ✅ WAJIB: Proper Imports

```python
# 1. Standard library
import logging
import re
from datetime import datetime

# 2. Odoo imports
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import date_utils

# 3. Third party (with try/except for optional)
try:
    import pandas as pd
except ImportError:
    pass
```

### 5. Docstrings

#### ✅ WAJIB: Document Methods

```python
def action_confirm(self):
    """Confirm the sales order.

    This method will:
    1. Validate the order has lines
    2. Update the state to 'sale'
    3. Trigger stock procurement
    4. Send notification email

    Raises:
        UserError: If order has no lines
    """
    pass
```

### 6. Error Handling

#### ✅ Best Practices

```python
# BENAR - Specific exception handling
def action_confirm(self):
    if not self.order_line:
        raise UserError(_("Please add at least one product line."))

    if self.state != 'draft':
        raise UserError(_("Only draft orders can be confirmed."))

    # Use proper exception type
    if not self.partner_id:
        raise ValidationError(_("Customer is required."))
```

#### ❌ DILARANG

```python
# SALAH - Generic exception
def action_confirm(self):
    try:
        self.write({'state': 'sale'})
    except Exception as e:
        raise  # Too generic
```

### 7. Logging

#### ✅ Best Practices

```python
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    def action_confirm(self):
        _logger.info('Confirming order %s', self.name)
        # ... logic
        _logger.info('Order %s confirmed successfully', self.name)
```

### 8. Super() Usage

#### ✅ Best Practices

```python
# BENAR - Call super properly
def write(self, vals):
    # Custom logic before
    _logger.info('Writing order: %s', vals)
    result = super().write(vals)
    # Custom logic after
    self._notify_confirmation()
    return result
```

### 9. API Decorators

#### ✅ WAJIB: Proper Decorator Usage

| Decorator | Usage |
|-----------|-------|
| `@api.model` | For default values, methods that don't need recordset |
| `@api.multi` | Default, for recordset methods |
| `@api.depends` | For computed fields |
| `@api.constrains` | For validation |
| `@api.onchange` | For UI changes |

```python
# BENAR
@api.model
def default_get(self, fields):
    return super().default_get(fields)

@api.multi
def action_confirm(self):
    pass

@api.depends('order_line.price_total')
def _compute_amount(self):
    pass

@api.constrains('date_order')
def _check_date(self):
    pass

@api.onchange('partner_id')
def _onchange_partner(self):
    pass
```

### 10. Performance Considerations

#### ✅ Best Practices

```python
# BENAR - Use mapped/browse efficiently
def _get_product_names(self):
    # Good - single query
    return self.order_line.mapped('product_id.name')

# SALAH - Loop with multiple queries
def _get_product_names(self):
    result = []
    for line in self.order_line:
        result.append(line.product_id.name)  # N+1 problem!
    return result
```

### 11. Security - Record Rules

#### ✅ Best Practices

```python
# Always check access rights
def unlink(self):
    self.check_access_rights('unlink')
    self.check_access_rule('unlink')
    return super().unlink()

# Or use sudo() with caution
def _get_all_records(self):
    # Only when intentional
    return self.sudo().search([])
```

### 12. Context Usage

#### ✅ Best Practices

```python
# BENAR - Use context properly
def action_send_mail(self):
    template = self.env.ref('module.email_template')
    template.with_context(
        lang=self.partner_id.lang,
        mail_create_nosubscribe=True,
    ).send_mail(self.id)

# Avoid modifying context unnecessarily
def process_something(self):
    # Don't do: self = self.with_context({}) without need
```

### 13. Query Optimization

#### ✅ Best Practices

```python
# BENAR - Efficient queries
def get_partners_with_orders(self):
    return self.env['res.partner'].search([
        ('order_ids', '!=', False)
    ])

# Use read_group for aggregation
def get_sales_summary(self):
    return self.env['sale.order'].read_group(
        domain=[('state', '=', 'sale')],
        fields=['date_order:year', 'amount_total:sum'],
        groupby=['date_order:year']
    )
```

### 14. Test Quality

#### ✅ Best Practices

```python
class TestSaleOrder(models.TransactionCase):
    def test_confirm_order_creates_procurement(self):
        """Test that confirming order creates procurement."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 10,
            })]
        })
        order.action_confirm()
        self.assertTrue(order.picking_ids)
```

## Code Quality Metrics

### Complexity Indicators

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **Method Lines** | < 30 | 30-50 | > 50 |
| **Class Lines** | < 200 | 200-500 | > 500 |
| **Cyclomatic Complexity** | < 5 | 5-10 | > 10 |
| **Parameters** | < 4 | 4-6 | > 6 |

### Quality Checklist

- [ ] No duplicate code
- [ ] No magic numbers (use constants)
- [ ] Proper error messages
- [ ] Logging for important operations
- [ ] Access rights checked
- [ ] Transactions handled properly
- [ ] No hardcoded values
- [ ] Proper string formatting

## Quick Review Guide

### Before Commit

- [ ] Code follows naming conventions
- [ ] Methods have proper structure
- [ ] Imports organized correctly
- [ ] Docstrings for complex methods
- [ ] Error handling specific
- [ ] No performance issues (N+1)
- [ ] Tests cover new functionality

### Code Review Points

1. **Readability** - Can others understand this code?
2. **Maintainability** - Easy to modify later?
3. **Performance** - Any N+1 queries?
4. **Security** - Any vulnerabilities?
5. **Testing** - Is it testable?

## Related Skills

- `odoo-security-review`: Security-focused review
- `odoo-debug-tdd`: Debugging with tests
- `odoo19-test-unit`: Test creation
