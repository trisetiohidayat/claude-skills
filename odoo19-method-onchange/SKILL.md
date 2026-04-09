---
description: Create @api.onchange methods for Odoo 19 models that trigger when field values change. Use when user wants to add an onchange method.
---


# Odoo 19 Onchange Method Creation

Create @api.onchange methods to automatically modify field values when other fields change.

## Instructions

1. **Onchange Method Pattern:**

```python
@api.onchange('field1', 'field2')
def _onchange_field1(self):
    for record in self:
        if record.field1:
            record.field2 = some_value
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('A message to the user')
                }
            }
```

2. **Key Rules:**
   - Use `@api.onchange()` decorator with trigger fields
   - Method runs when specified fields change in the form
   - Only works in UI forms, not in programmatic writes
   - Changes are not saved until record is saved
   - Can return warnings to inform users
   - Loop through `self` even though onchange typically affects single record

3. **When to Use Onchange:**
   - Auto-fill related fields
   - Validate field combinations
   - Show warnings based on field values
   - Update dependent fields
   - Filter domain of relational fields

4. **When NOT to Use Onchange:**
   - For data integrity (use @api.constrains)
   - For computed values (use compute fields)
   - For critical business logic (use overrides)

5. **Return Values:**
   - None (silent change)
   - Dictionary with 'warning' key
   - Dictionary with 'domain' key

## Usage Examples

### Simple Field Copy

```bash
/method-onchange _onchange_partner_id "partner_id" "partner_email,partner_phone" "Copy email and phone from partner"
```

Output:
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    for record in self:
        if record.partner_id:
            record.partner_email = record.partner_id.email
            record.partner_phone = record.partner_id.phone
```

### Price Calculation

```bash
/method-onchange _onchange_product_id "product_id" "price_unit,description,name" "Update price and description from product"
```

Output:
```python
@api.onchange('product_id')
def _onchange_product_id(self):
    for record in self:
        if record.product_id:
            record.price_unit = record.product_id.list_price
            record.description = record.product_id.name
            if record.product_id.description_sale:
                record.description += '\n' + record.product_id.description_sale
```

### Dynamic Domain

```bash
/method-onchange _onchange_category_id "category_id" "product_id" "Filter products by category"
```

Output:
```python
@api.onchange('category_id')
def _onchange_category_id(self):
    for record in self:
        if record.category_id:
            return {
                'domain': {
                    'product_id': [('categ_id', '=', record.category_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'product_id': []
                }
            }
```

### Date Calculation

```bash
/method-onchange _onchange_start_date "start_date" "end_date" "Set end_date 7 days after start_date"
```

Output:
```python
from datetime import timedelta

@api.onchange('start_date')
def _onchange_start_date(self):
    for record in self:
        if record.start_date:
            record.end_date = record.start_date + timedelta(days=7)
```

### Price with Warning

```bash
/method-onchange _onchange_discount "discount" "price_unit" "Warn if discount exceeds 20%"
```

Output:
```python
@api.onchange('discount')
def _onchange_discount(self):
    for record in self:
        if record.discount and record.discount > 20:
            return {
                'warning': {
                    'title': _('High Discount'),
                    'message': _(
                        'Discount is %.2f%%. Manager approval may be required.'
                    ) % record.discount
                }
            }
```

### Automatic Name Generation

```bash
/method-onchange _onchange_first_name "first_name,last_name" "name" "Combine first and last name"
```

Output:
```python
@api.onchange('first_name', 'last_name')
def _onchange_first_name(self):
    for record in self:
        if record.first_name or record.last_name:
            record.name = f"{record.first_name or ''} {record.last_name or ''}".strip()
```

### Tax Calculation

```bash
/method-onchange _onchange_amount_tax "amount,tax_id" "amount_tax" "Calculate tax amount"
```

Output:
```python
@api.onchange('amount', 'tax_id')
def _onchange_amount_tax(self):
    for record in self:
        if record.amount and record.tax_id:
            record.amount_tax = record.amount * record.tax_id.amount / 100
        else:
            record.amount_tax = 0.0
```

### Account Selection Filter

```bash
/method-onchange _onchange_journal_id "journal_id" "account_id" "Filter accounts by journal company"
```

Output:
```python
@api.onchange('journal_id')
def _onchange_journal_id(self):
    for record in self:
        if record.journal_id:
            return {
                'domain': {
                    'account_id': [
                        ('company_id', '=', record.journal_id.company_id.id),
                        ('deprecated', '=', False)
                    ]
                }
            }
        return {
            'domain': {'account_id': []}
        }
```

### Quantity-Based Price Break

```bash
/method-onchange _onchange_quantity "quantity,product_id" "price_unit" "Apply quantity-based price break"
```

Output:
```python
@api.onchange('quantity', 'product_id')
def _onchange_quantity(self):
    for record in self:
        if record.product_id and record.quantity:
            # Simple price break logic
            if record.quantity >= 100:
                record.price_unit = record.product_id.list_price * 0.8  # 20% discount
            elif record.quantity >= 50:
                record.price_unit = record.product_id.list_price * 0.9  # 10% discount
            else:
                record.price_unit = record.product_id.list_price
```

### Clear Dependent Fields

```bash
/method-onchange _onchange_order_type "order_type" "partner_id,warehouse_id" "Clear partner and warehouse when type changes"
```

Output:
```python
@api.onchange('order_type')
def _onchange_order_type(self):
    for record in self:
        if record.order_type:
            # Clear related fields when order type changes
            record.partner_id = False
            record.warehouse_id = False
```

### Weight Calculation

```bash
/method-onchange _onchange_weight_details "weight_unit,quantity" "total_weight" "Calculate total weight"
```

Output:
```python
@api.onchange('weight_unit', 'quantity')
def _onchange_weight_details(self):
    for record in self:
        if record.weight_unit and record.quantity:
            record.total_weight = record.weight_unit * record.quantity
        else:
            record.total_weight = 0.0
```

### Company-Dependent Filter

```bash
/method-onchange _onchange_company_id "company_id" "journal_id,account_id" "Filter journal and account by company"
```

Output:
```python
@api.onchange('company_id')
def _onchange_company_id(self):
    for record in self:
        record.journal_id = False
        record.account_id = False
        if record.company_id:
            return {
                'domain': {
                    'journal_id': [('company_id', '=', record.company_id.id)],
                    'account_id': [('company_id', '=', record.company_id.id)]
                }
            }
        return {
            'domain': {
                'journal_id': [],
                'account_id': []
            }
        }
```

### Email Validation Warning

```bash
/method-onchange _onchange_email "email" "email" "Warn if email is already in use"
```

Output:
```python
@api.onchange('email')
def _onchange_email(self):
    for record in self:
        if record.email:
            # Check if email already exists
            existing = self.search([
                ('email', '=', record.email),
                ('id', '!=', record.id)
            ], limit=1)
            if existing:
                return {
                    'warning': {
                        'title': _('Duplicate Email'),
                        'message': _(
                            'This email address is already used by %s. '
                            'Duplicates may cause issues.'
                        ) % existing[0].name
                    }
                }
```

### Total with Tax Breakdown

```bash
/method-onchange _onchange_subtotal_tax "subtotal,tax_ids" "total,tax_amount" "Calculate total and tax breakdown"
```

Output:
```python
@api.onchange('subtotal', 'tax_ids')
def _onchange_subtotal_tax(self):
    for record in self:
        if record.subtotal and record.tax_ids:
            # Calculate total tax
            record.tax_amount = sum(
                record.subtotal * tax.amount / 100
                for tax in record.tax_ids
            )
            record.total = record.subtotal + record.tax_amount
        else:
            record.tax_amount = 0.0
            record.total = record.subtotal or 0.0
```

### Product Category Filter

```bash
/method-onchange _onchange_product_type "product_type" "categ_id" "Filter category by product type"
```

Output:
```python
@api.onchange('product_type')
def _onchange_product_type(self):
    for record in self:
        record.categ_id = False
        if record.product_type == 'service':
            return {
                'domain': {
                    'categ_id': [('parent_id.name', 'ilike', 'Services')]
                }
            }
        elif record.product_type == 'product':
            return {
                'domain': {
                    'categ_id': [('parent_id.name', 'ilike', 'Products')]
                }
            }
        return {
            'domain': {'categ_id': []}
        }
```

### Priority-Based Warning

```bash
/method-onchange _onchange_priority "priority,deadline" "priority" "Warn if high priority has no deadline"
```

Output:
```python
@api.onchange('priority', 'deadline')
def _onchange_priority(self):
    for record in self:
        if record.priority == '2' and not record.deadline:  # High priority
            return {
                'warning': {
                    'title': _('Missing Deadline'),
                    'message': _(
                        'High priority tasks should have a deadline. '
                        'Consider setting one.'
                    )
                }
            }
```

### Currency Conversion

```bash
/method-onchange _onchange_amount_currency "amount,currency_id,company_currency_id" "amount_company_currency" "Convert to company currency"
```

Output:
```python
from odoo import fields

@api.onchange('amount', 'currency_id')
def _onchange_amount_currency(self):
    for record in self:
        if record.amount and record.currency_id:
            record.amount_company_currency = record.currency_id._convert(
                record.amount,
                record.company_id.currency_id,
                record.company_id,
                fields.Date.today()
            )
        else:
            record.amount_company_currency = 0.0
```

## Best Practices

1. **Performance:**
   - Keep onchange logic simple and fast
   - Avoid heavy database queries
   - Don't fetch unnecessary related records
   - Consider using computed fields for complex calculations

2. **User Experience:**
   - Use warnings to inform users of potential issues
   - Don't use warnings for information (use help text instead)
   - Make sure automatic changes are intuitive
   - Preserve user input when possible

3. **Domain Updates:**
   - Always provide domain for all possible states
   - Clear dependent fields when domain changes
   - Test domain filters thoroughly

4. **Error Handling:**
   - Handle None/empty values gracefully
   - Don't raise exceptions in onchange methods
   - Use warnings for non-critical issues
   - Validate before making changes

5. **Consistency:**
   - Use predictable naming: `_onchange_{trigger_field}`
   - Document side effects in comments
   - Keep logic simple and readable

## Onchange vs Computed Fields

| Feature | Onchange | Computed Field |
|---------|----------|----------------|
| Trigger | Form field change | Dependency change |
| Storage | Not saved | Can be stored |
| Searchable | No | Yes (if stored) |
| Use case | UX improvements | Data derivation |
| Performance | UI only | Database level |

## Return Value Examples

### Warning Only
```python
return {
    'warning': {
        'title': _('Warning Title'),
        'message': _('Warning message here')
    }
}
```

### Domain Only
```python
return {
    'domain': {
        'field_id': [('active', '=', True)]
    }
}
```

### Both Warning and Domain
```python
return {
    'warning': {
        'title': _('Warning'),
        'message': _('Message')
    },
    'domain': {
        'field_id': [('state', '=', 'active')]
    }
}
```

## Common Patterns

### Reset Fields
```python
@api.onchange('field1')
def _onchange_field1(self):
    if self.field1:
        self.field2 = False
        self.field3 = False
```

### Copy from Relation
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.street = self.partner_id.street
        self.city = self.partner_id.city
        self.zip = self.partner_id.zip
```

### Calculate Values
```python
@api.onchange('quantity', 'unit_price')
def _onchange_quantity(self):
    if self.quantity and self.unit_price:
        self.total = self.quantity * self.unit_price
```

### Filter Choices
```python
@api.onchange('country_id')
def _onchange_country_id(self):
    if self.country_id:
        return {
            'domain': {
                'state_id': [('country_id', '=', self.country_id.id)]
            }
        }
```

## Limitations

1. **No Database Writes:**
   - Onchange only modifies the form
   - Changes not saved until record saved
   - Won't trigger other onchange methods

2. **Form Only:**
   - Works in UI forms only
   - Not triggered by programmatic writes
   - Not triggered by imports

3. **Recordset:**
   - Usually single record in form context
   - But should always loop through self

## Next Steps

After creating onchange methods:
- Test in form view
- Verify user experience
- Consider edge cases
- Add help text to explain automatic changes
- Document in model comments
