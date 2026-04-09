---
description: Create validation methods using @api.constrains decorator for Odoo 19 models. Use when user wants to add a constraint to a model.
---


# Odoo 19 Constraint Method Creation

Create validation methods using @api.constrains decorator to enforce business rules.

## Instructions

1. **Constraint Method Pattern:**

```python
from odoo import api, models, _
from odoo.exceptions import ValidationError

@api.constrains('field1', 'field2')
def _check_field_name(self):
    for record in self:
        if record.field1 and record.field2:
            if record.field1 > record.field2:
                raise ValidationError(_('Field1 must be less than Field2'))
```

2. **Key Rules:**
   - Use `@api.constrains()` decorator with field names
   - Method runs when specified fields are written
   - Use `ValidationError` for validation failures
   - Always use `_()` for translatable error messages
   - Loop through `self` to validate each record
   - Handle empty/null values appropriately

3. **Error Message Best Practices:**
   - Be clear and specific
   - Mention the field names involved
   - Suggest corrective action if possible
   - Keep messages user-friendly

4. **Validation Types:**
   - Value range validation
   - Dependency validation
   - Uniqueness validation
   - Format validation
   - Business rule validation

## Usage Examples

### Numeric Range Validation

```bash
/method-constraint _check_age "age" "Age must be between 18 and 100" "Validate age is >= 18 and <= 100"
```

Output:
```python
@api.constrains('age')
def _check_age(self):
    for record in self:
        if record.age and (record.age < 18 or record.age > 100):
            raise ValidationError(_('Age must be between 18 and 100.'))
```

### Date Range Validation

```bash
/method-constraint _check_dates "start_date,end_date" "Start date must be before end date" "Ensure start_date <= end_date when both are set"
```

Output:
```python
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if record.start_date and record.end_date:
            if record.start_date > record.end_date:
                raise ValidationError(_('Start date must be before or equal to end date.'))
```

### Email Format Validation

```bash
/method-constraint _check_email "email" "Invalid email format" "Validate email field contains valid email format"
```

Output:
```python
import re

@api.constrains('email')
def _check_email(self):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    for record in self:
        if record.email:
            if not re.match(email_pattern, record.email):
                raise ValidationError(_('Please enter a valid email address.'))
```

### Unique Field Combination

```bash
/method-constraint _check_unique_code "code,category_id" "Code must be unique per category" "Ensure code is unique within the same category"
```

Output:
```python
@api.constrains('code', 'category_id')
def _check_unique_code(self):
    for record in self:
        if record.code and record.category_id:
            domain = [
                ('code', '=', record.code),
                ('category_id', '=', record.category_id.id),
                ('id', '!=', record.id)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    'Code "%s" already exists in category "%s". '
                    'Please use a different code.'
                ) % (record.code, record.category_id.name))
```

### Phone Number Validation

```bash
/method-constraint _check_phone "phone" "Invalid phone number format" "Validate phone contains only digits, spaces, +, -, (, )"
```

Output:
```python
import re

@api.constrains('phone')
def _check_phone(self):
    for record in self:
        if record.phone:
            # Remove common separators
            cleaned = re.sub(r'[\s\-\(\)\+]', '', record.phone)
            if not cleaned.isdigit() or len(cleaned) < 10:
                raise ValidationError(_(
                    'Please enter a valid phone number '
                    '(at least 10 digits).'
                ))
```

### Positive Number Validation

```bash
/method-constraint _check_positive "quantity,price" "Quantity and price must be positive" "Ensure fields are > 0 when set"
```

Output:
```python
@api.constrains('quantity', 'price')
def _check_positive(self):
    for record in self:
        if record.quantity is not None and record.quantity <= 0:
            raise ValidationError(_('Quantity must be a positive number.'))
        if record.price is not None and record.price <= 0:
            raise ValidationError(_('Price must be a positive number.'))
```

### URL Validation

```bash
/method-constraint _check_url "website" "Invalid URL format" "Validate website field contains valid URL"
```

Output:
```python
import re

@api.constrains('website')
def _check_url(self):
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    for record in self:
        if record.website:
            if not url_pattern.match(record.website):
                raise ValidationError(_('Please enter a valid URL (starting with http:// or https://)'))
```

### Percentage Validation

```bash
/method-constraint _check_percentage "discount_rate" "Discount must be between 0 and 100" "Validate discount_rate is between 0 and 100"
```

Output:
```python
@api.constrains('discount_rate')
def _check_percentage(self):
    for record in self:
        if record.discount_rate is not None:
            if record.discount_rate < 0 or record.discount_rate > 100:
                raise ValidationError(_(
                    'Discount rate must be between 0 and 100 percent.'
                ))
```

### Dependent Field Validation

```bash
/method-constraint _check_accounting "journal_id,account_id" "Account must belong to journal company" "Ensure account.company_id == journal.company_id"
```

Output:
```python
@api.constrains('journal_id', 'account_id')
def _check_accounting(self):
    for record in self:
        if record.journal_id and record.account_id:
            if record.journal_id.company_id != record.account_id.company_id:
                raise ValidationError(_(
                    'The account must belong to the same company as the journal. '
                    'Journal: %s, Account: %s'
                ) % (record.journal_id.name, record.account_id.name))
```

### VAT Number Validation

```bash
/method-constraint _check_vat "vat,company_id" "Invalid VAT number for country" "Validate VAT number format based on company country"
```

Output:
```python
from stdnum import vat

@api.constrains('vat', 'country_id')
def _check_vat(self):
    for record in self:
        if record.vat and record.country_id:
            try:
                # Check if country code matches
                if not record.vat.startswith(record.country_id.code.upper()):
                    raise ValueError()
                # Validate VAT number format
                vat.validate(record.vat)
            except (ValueError, ValidationError):
                raise ValidationError(_(
                    'The VAT number "%s" is not valid for country "%s". '
                    'Please check the format.'
                ) % (record.vat, record.country_id.name))
```

### IBAN Validation

```bash
/method-constraint _check_iban "iban" "Invalid IBAN format" "Validate IBAN number format"
```

Output:
```python
from stdnum import iban

@api.constrains('iban')
def _check_iban(self):
    for record in self:
        if record.iban:
            try:
                iban.validate(record.iban)
            except Exception:
                raise ValidationError(_(
                    'The IBAN "%s" is not valid. '
                    'Please check the format and try again.'
                ) % record.iban)
```

### Social Security Number Validation

```bash
/method-constraint _check_ssn "ssn" "Invalid SSN format" "Validate SSN has format XXX-XX-XXXX"
```

Output:
```python
import re

@api.constrains('ssn')
def _check_ssn(self):
    ssn_pattern = r'^\d{3}-\d{2}-\d{4}$'
    for record in self:
        if record.ssn:
            if not re.match(ssn_pattern, record.ssn):
                raise ValidationError(_(
                    'Social Security Number must be in format XXX-XX-XXXX.'
                ))
            # Additional check for obvious invalid numbers
            cleaned = record.ssn.replace('-', '')
            if cleaned in ['000000000', '111111111', '999999999']:
                raise ValidationError(_('Please enter a valid Social Security Number.'))
```

### Minimum Order Amount

```bash
/method-constraint _check_minimum_order "amount_total,partner_id" "Order total below minimum" "Ensure amount_total >= partner.minimum_order_amount"
```

Output:
```python
@api.constrains('amount_total', 'partner_id')
def _check_minimum_order(self):
    for record in self:
        if record.partner_id and record.amount_total:
            minimum = record.partner_id.minimum_order_amount or 0
            if record.amount_total < minimum:
                raise ValidationError(_(
                    'Order total (%.2f) is below the minimum required amount '
                    '(%.2f) for customer "%s".'
                ) % (record.amount_total, minimum, record.partner_id.name))
```

### Required Together

```bash
/method-constraint _check_delivery_required "delivery_date,delivery_address" "Both delivery date and address are required" "Ensure if delivery_date is set then delivery_address is also set, and vice versa"
```

Output:
```python
@api.constrains('delivery_date', 'delivery_address')
def _check_delivery_required(self):
    for record in self:
        has_date = bool(record.delivery_date)
        has_address = bool(record.delivery_address)
        if has_date != has_address:
            raise ValidationError(_(
                'Both delivery date and delivery address must be specified together.'
            ))
```

### No Overlapping Dates

```bash
/method-constraint _check_overlapping "employee_id,start_date,end_date" "Employee already has leave in this period" "Check for overlapping date ranges for same employee"
```

Output:
```python
@api.constrains('employee_id', 'start_date', 'end_date')
def _check_overlapping(self):
    for record in self:
        if record.employee_id and record.start_date and record.end_date:
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id),
                ('state', '!=', 'cancel'),
                '|',
                '&', ('start_date', '<=', record.start_date), ('end_date', '>=', record.start_date),
                '&', ('start_date', '<=', record.end_date), ('end_date', '>=', record.end_date),
            ]
            if self.search_count(domain):
                raise ValidationError(_(
                    'Employee "%s" already has leave in this period. '
                    'Please check the dates.'
                ) % record.employee_id.name)
```

### File Size Validation

```bash
/method-constraint _check_file_size "attachment_file" "File size exceeds limit" "Ensure file size is less than 10MB"
```

Output:
```python
@api.constrains('attachment_file')
def _check_file_size(self):
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    for record in self:
        if record.attachment_file:
            file_size = len(record.attachment_file) * 3 / 4  # Base64 approximation
            if file_size > max_size:
                size_mb = file_size / (1024 * 1024)
                raise ValidationError(_(
                    'File size (%.2f MB) exceeds the maximum allowed size of 10 MB.'
                ) % size_mb)
```

## Best Practices

1. **Performance:**
   - Keep constraints simple and fast
   - Avoid expensive database queries
   - Use `search_count()` instead of `search()` when checking existence
   - Cache expensive calculations

2. **User Experience:**
   - Provide clear, actionable error messages
   - Include the problematic values in the message
   - Suggest how to fix the issue
   - Use field labels instead of technical names

3. **Validation Strategy:**
   - Validate at the field level when possible (using field attributes)
   - Use constraints for cross-field validation
   - Use constraints for complex business rules
   - Document constraints in code comments

4. **Internationalization:**
   - Always wrap error messages in `_()` for translation
   - Avoid concatenating translated strings
   - Use string formatting with `_()` wrapper

5. **Error Handling:**
   - Validate None/empty values appropriately
   - Handle different data types gracefully
   - Consider the business context

## Common Validation Patterns

### Range Check
```python
if value < min or value > max:
    raise ValidationError(_('Value must be between %s and %s') % (min, max))
```

### Uniqueness Check
```python
if self.search_count([('field', '=', value), ('id', '!=', record.id)]) > 0:
    raise ValidationError(_('Value must be unique'))
```

### Dependency Check
```python
if field1 and not field2:
    raise ValidationError(_('Field2 is required when Field1 is set'))
```

### Format Check
```python
if not re.match(pattern, value):
    raise ValidationError(_('Invalid format'))
```

### Existence Check
```python
if not record.relation_id:
    raise ValidationError(_('Please select a valid relation'))
```

## SQL Constraints Alternative

For simple uniqueness or database-level constraints, use SQL constraints:

```python
_sql_constraints = [
    ('code_unique', 'UNIQUE(code)', 'Code must be unique!'),
    ('check_positive', 'CHECK(amount >= 0)', 'Amount must be positive!'),
]
```

## Next Steps

After creating constraints:
- Test with valid and invalid data
- Ensure error messages are clear
- Add unit tests for constraint validation
- Consider adding user documentation
