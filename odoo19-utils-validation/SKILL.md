---
description: Create validation helpers for email, phone, URL for Odoo 19 models. Use when user wants to add validation to a module.
---


# Odoo 19 Validation Utility (/utils-validation)

This skill helps you create validation helper methods for common data validation patterns in Odoo 19 models.

## Validation Overview

Odoo 19 provides several built-in validation mechanisms:

1. **Field constraints** (`required=True`, pattern matching)
2. **`@api.constrains` decorators** for custom validation logic
3. **Python validation helpers** for common formats
4. **Odoo's built-in validation utilities** in `odoo.tools`

## Built-in Odoo Validators

Odoo provides several useful validation functions in `odoo.tools`:

```python
from odoo.tools import email_validation, phone_validation
```

### Email Validation

```python
from odoo import models, fields, api
from odoo.tools import email_validation
from odoo.exceptions import ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                # Using Odoo's email validation
                if not email_validation.email_validate(record.email):
                    raise ValidationError(_('Invalid email address: %s') % record.email)
```

### Phone Validation

```python
from odoo import models, fields, api
from odoo.tools import phone_validation
from odoo.exceptions import ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('phone', 'mobile')
    def _check_phone(self):
        for record in self:
            if record.phone:
                # Validate and format phone number
                try:
                    record.phone = phone_validation.phone_format(
                        record.phone,
                        country_code=record.country_id.code if record.country_id else None
                    )
                except Exception as e:
                    raise ValidationError(_('Invalid phone number: %s') % record.phone)
```

## Custom Validation Helpers

Create a dedicated validation utility module:

```
your_module/
├── utils/
│   ├── __init__.py
│   └── validators.py
└── models/
    └── your_model.py
```

### `/utils/validators.py`

```python
"""
Validation helpers for Odoo 19 models.
Common validation utilities for email, phone, URL, and other formats.
"""

import re
from odoo import _
from odoo.exceptions import ValidationError

class ValidationHelpers:
    """Collection of validation helper methods"""

    # Email Validation Patterns
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    # URL Validation Patterns
    URL_PATTERN = re.compile(
        r'^(https?:\/\/)?'  # Optional protocol
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # Domain
        r'(\/[^\s]*)?$'  # Optional path
    )

    # Phone Validation Patterns (International)
    PHONE_PATTERN = re.compile(
        r'^\+?[\d\s\-\(\)]+$'
    )

    # ZIP Code Patterns by Country
    ZIPCODE_PATTERNS = {
        'US': r'^\d{5}(-\d{4})?$',           # 12345 or 12345-6789
        'CA': r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$',  # A1A 1A1
        'UK': r'^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$',
        'DE': r'^\d{5}$',                    # 12345
        'FR': r'^\d{5}$',                    # 12345
        'IT': r'^\d{5}$',                    # 12345
        'ES': r'^\d{5}$',                    # 12345
        'NL': r'^\d{4} ?[A-Za-z]{2}$',       # 1234 AB
        'BE': r'^\d{4}$',                    # 1234
        'CH': r'^\d{4}$',                    # 1234
        'AT': r'^\d{4}$',                    # 1234
        'AU': r'^\d{4}$',                    # 1234
        'JP': r'^\d{3}-\d{4}$',              # 123-4567
        'IN': r'^\d{6}$',                    # 123456
        'BR': r'^\d{5}-\d{3}$',              # 12345-678
        'MX': r'^\d{5}$',                    # 12345
        'CN': r'^\d{6}$',                    # 123456
        'RU': r'^\d{6}$',                    # 123456
    }

    # VAT Number Patterns (European)
    VAT_PATTERNS = {
        'AT': r'^ATU\d{8}$',                 # Austria
        'BE': r'^BE0?\d{9}$',                # Belgium
        'BG': r'^BG\d{9,10}$',               # Bulgaria
        'CY': r'^CY\d{8}[A-Z]$',             # Cyprus
        'CZ': r'^CZ\d{8,10}$',               # Czech Republic
        'DE': r'^DE\d{9}$',                  # Germany
        'DK': r'^DK\d{8}$',                  # Denmark
        'EE': r'^EE\d{9}$',                  # Estonia
        'EL': r'^EL\d{9}$',                  # Greece
        'ES': r'^ES[A-Z0-9]\d{7}[A-Z0-9]$',  # Spain
        'FI': r'^FI\d{8}$',                  # Finland
        'FR': r'^FR[A-Z0-9]{2}\d{9}$',       # France
        'GB': r'^GB\d{9}$',                  # United Kingdom
        'GR': r'^GR\d{9}$',                  # Greece
        'HR': r'^HR\d{11}$',                 # Croatia
        'HU': r'^HU\d{8}$',                  # Hungary
        'IE': r'^IE[A-Z0-9]{8,9}$',          # Ireland
        'IT': r'^IT\d{11}$',                 # Italy
        'LT': r'^LT\d{9,12}$',               # Lithuania
        'LU': r'^LU\d{8}$',                  # Luxembourg
        'LV': r'^LV\d{11}$',                 # Latvia
        'MT': r'^MT\d{8}$',                  # Malta
        'NL': r'^NL\d{9}B\d{2}$',            # Netherlands
        'PL': r'^PL\d{10}$',                 # Poland
        'PT': r'^PT\d{9}$',                  # Portugal
        'RO': r'^RO\d{2,10}$',               # Romania
        'SE': r'^SE\d{12}$',                 # Sweden
        'SI': r'^SI\d{8}$',                  # Slovenia
        'SK': r'^SK\d{10}$',                 # Slovakia
    }

    # IBAN Validation
    IBAN_MIN_LENGTH = 15
    IBAN_MAX_LENGTH = 34

    @staticmethod
    def validate_email(email):
        """
        Validate email address format.

        Args:
            email (str): Email address to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not email:
            return False
        return bool(ValidationHelpers.EMAIL_PATTERN.match(email.strip()))

    @staticmethod
    def validate_phone(phone, country_code=None):
        """
        Validate phone number format.

        Args:
            phone (str): Phone number to validate
            country_code (str): ISO country code for validation

        Returns:
            bool: True if valid, False otherwise
        """
        if not phone:
            return False

        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        # Must contain only digits and optional +
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned

        return bool(ValidationHelpers.PHONE_PATTERN.match(phone))

    @staticmethod
    def validate_url(url):
        """
        Validate URL format.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not url:
            return False
        return bool(ValidationHelpers.URL_PATTERN.match(url.strip()))

    @staticmethod
    def validate_zipcode(zipcode, country_code):
        """
        Validate ZIP/postal code based on country.

        Args:
            zipcode (str): ZIP code to validate
            country_code (str): ISO country code (e.g., 'US', 'CA', 'UK')

        Returns:
            bool: True if valid, False otherwise
        """
        if not zipcode or not country_code:
            return True  # Don't validate if missing

        pattern = ValidationHelpers.ZIPCODE_PATTERNS.get(country_code.upper())
        if not pattern:
            return True  # No pattern defined, accept any

        return bool(re.match(pattern, zipcode.strip()))

    @staticmethod
    def validate_vat(vat_number, country_code):
        """
        Validate VAT number based on country.

        Args:
            vat_number (str): VAT number to validate
            country_code (str): ISO country code

        Returns:
            bool: True if valid, False otherwise
        """
        if not vat_number or not country_code:
            return True

        vat_number = vat_number.strip().upper()
        country_code = country_code.upper()

        # Add country prefix if missing
        if not vat_number.startswith(country_code):
            vat_number = country_code + vat_number

        pattern = ValidationHelpers.VAT_PATTERNS.get(country_code)
        if not pattern:
            return True  # No pattern defined

        return bool(re.match(pattern, vat_number))

    @staticmethod
    def validate_iban(iban):
        """
        Validate IBAN (International Bank Account Number).

        Args:
            iban (str): IBAN to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not iban:
            return False

        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()

        # Check length
        if not (ValidationHelpers.IBAN_MIN_LENGTH <= len(iban) <= ValidationHelpers.IBAN_MAX_LENGTH):
            return False

        # Check country code (first 2 letters)
        if not iban[:2].isalpha():
            return False

        # Move first 4 characters to end
        moved = iban[4:] + iban[:4]

        # Replace letters with numbers
        numeric = ''
        for char in moved:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)

        # Check if divisible by 97
        return int(numeric) % 97 == 1

    @staticmethod
    def validate_ssn(ssn, country_code='US'):
        """
        Validate Social Security Number (or national ID).

        Args:
            ssn (str): SSN to validate
            country_code (str): Country code for validation rules

        Returns:
            bool: True if valid, False otherwise
        """
        if not ssn:
            return False

        ssn = ssn.replace('-', '').replace(' ', '')

        if country_code == 'US':
            # US SSN: 9 digits, no leading 000, no leading 666
            if len(ssn) != 9 or not ssn.isdigit():
                return False
            if ssn.startswith('000') or ssn.startswith('666'):
                return False
            if ssn[3:5] == '00' or ssn[5:] == '0000':
                return False
            return True

        # Add other countries as needed
        return True

    @staticmethod
    def validate_credit_card(card_number):
        """
        Validate credit card number using Luhn algorithm.

        Args:
            card_number (str): Card number to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not card_number:
            return False

        # Remove spaces and dashes
        card_number = card_number.replace(' ', '').replace('-', '')

        if not card_number.isdigit() or len(card_number) < 13:
            return False

        # Luhn algorithm
        total = 0
        reverse_digits = card_number[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n

        return total % 10 == 0

    @staticmethod
    def validate_ip_address(ip_address):
        """
        Validate IPv4 or IPv6 address.

        Args:
            ip_address (str): IP address to validate

        Returns:
            bool: True if valid, False otherwise
        """
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_date_format(date_str, format='%Y-%m-%d'):
        """
        Validate date string format.

        Args:
            date_str (str): Date string to validate
            format (str): Expected date format

        Returns:
            bool: True if valid, False otherwise
        """
        from datetime import datetime
        try:
            datetime.strptime(date_str, format)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_hex_color(color):
        """
        Validate hexadecimal color code.

        Args:
            color (str): Color code (e.g., '#FF0000' or 'FF0000')

        Returns:
            bool: True if valid, False otherwise
        """
        if not color:
            return False
        color = color.lstrip('#')
        return bool(re.match(r'^[0-9A-Fa-f]{6}$', color))

    @staticmethod
    def validate_username(username):
        """
        Validate username format.

        Args:
            username (str): Username to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not username:
            return False
        # Alphanumeric, underscore, hyphen, 3-30 characters
        pattern = r'^[a-zA-Z0-9_-]{3,30}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_password_strength(password):
        """
        Check password strength (returns strength level).

        Args:
            password (str): Password to validate

        Returns:
            str: 'weak', 'medium', 'strong'
        """
        if not password:
            return 'weak'

        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1

        if score <= 2:
            return 'weak'
        elif score <= 4:
            return 'medium'
        else:
            return 'strong'
```

## Using Validation Helpers in Models

### Model with Email Validation

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ..utils.validators import ValidationHelpers

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'

    name = fields.Char('Name', required=True)
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    website = fields.Char('Website')
    zipcode = fields.Char('ZIP Code')
    country_id = fields.Many2one('res.country', 'Country')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and not ValidationHelpers.validate_email(record.email):
                raise ValidationError(
                    _('Invalid email address: %s') % record.email
                )

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not ValidationHelpers.validate_phone(record.phone):
                raise ValidationError(
                    _('Invalid phone number: %s') % record.phone
                )

    @api.constrains('website')
    def _check_website(self):
        for record in self:
            if record.website and not ValidationHelpers.validate_url(record.website):
                raise ValidationError(
                    _('Invalid website URL: %s') % record.website
                )

    @api.constrains('zipcode', 'country_id')
    def _check_zipcode(self):
        for record in self:
            if record.zipcode and record.country_id:
                if not ValidationHelpers.validate_zipcode(
                    record.zipcode,
                    record.country_id.code
                ):
                    raise ValidationError(
                        _('Invalid ZIP code for %s: %s') % (
                            record.country_id.name,
                            record.zipcode
                        )
                    )
```

### Bank Account with IBAN/VAT Validation

```python
class CompanyBank(models.Model):
    _name = 'company.bank'
    _description = 'Company Bank Account'

    company_id = fields.Many2one('res.company', 'Company', required=True)
    bank_name = fields.Char('Bank Name', required=True)
    account_number = fields.Char('Account Number')
    iban = fields.Char('IBAN')
    vat_number = fields.Char('VAT Number')
    country_id = fields.Many2one('res.country', 'Country')

    @api.constrains('iban')
    def _check_iban(self):
        for record in self:
            if record.iban and not ValidationHelpers.validate_iban(record.iban):
                raise ValidationError(
                    _('Invalid IBAN: %s') % record.iban
                )

    @api.constrains('vat_number', 'country_id')
    def _check_vat(self):
        for record in self:
            if record.vat_number and record.country_id:
                if not ValidationHelpers.validate_vat(
                    record.vat_number,
                    record.country_id.code
                ):
                    raise ValidationError(
                        _('Invalid VAT number for %s: %s') % (
                            record.country_id.name,
                            record.vat_number
                        )
                    )
```

### Online Store with Credit Card Validation

```python
class PaymentCard(models.Model):
    _name = 'payment.card'
    _description = 'Payment Card'

    partner_id = fields.Many2one('res.partner', 'Cardholder', required=True)
    card_number = fields.Char('Card Number', required=True)
    cardholder_name = fields.Char('Cardholder Name', required=True)
    expiry_month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        # ... etc
    ], 'Expiry Month', required=True)
    expiry_year = fields.Integer('Expiry Year', required=True)
    cvv = fields.Char('CVV', size=3, required=True)

    @api.constrains('card_number')
    def _check_card_number(self):
        for record in self:
            if record.card_number:
                # Remove spaces for validation
                cleaned = record.card_number.replace(' ', '')
                if not ValidationHelpers.validate_credit_card(cleaned):
                    raise ValidationError(
                        _('Invalid credit card number: %s') % record.card_number
                    )

    @api.constrains('expiry_month', 'expiry_year')
    def _check_expiry(self):
        from datetime import datetime
        for record in self:
            if record.expiry_month and record.expiry_year:
                expiry_date = datetime(
                    record.expiry_year,
                    int(record.expiry_month),
                    1
                )
                if expiry_date < datetime.now():
                    raise ValidationError(_('Card has expired'))
```

## Validation with Error Messages

### Contextual Validation Messages

```python
class Book(models.Model):
    _name = 'library.book'
    _description = 'Book'

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and not ValidationHelpers.validate_email(record.email):
                raise ValidationError(
                    _(
                        'The email address "%(email)s" for book "%(book)s" is invalid. '
                        'Please enter a valid email address (e.g., user@example.com).'
                    ) % {
                        'email': record.email,
                        'book': record.name
                    }
                )
```

### Multiple Validations in One Method

```python
@api.constrains('email', 'phone', 'website')
def _check_contact_info(self):
    for record in self:
        errors = []

        if record.email and not ValidationHelpers.validate_email(record.email):
            errors.append(_('Email address is invalid'))

        if record.phone and not ValidationHelpers.validate_phone(record.phone):
            errors.append(_('Phone number is invalid'))

        if record.website and not ValidationHelpers.validate_url(record.website):
            errors.append(_('Website URL is invalid'))

        if errors:
            raise ValidationError(
                _('Please correct the following errors:\n- %s') % '\n- '.join(errors)
            )
```

## Onchange Validation

### Real-time Validation Feedback

```python
class Partner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('email')
    def _onchange_email(self):
        if self.email and not ValidationHelpers.validate_email(self.email):
            return {
                'warning': {
                    'title': _('Invalid Email'),
                    'message': _(
                        'The email address "%s" does not appear to be valid. '
                        'Please check the format.'
                    ) % self.email
                }
            }

    @api.onchange('zipcode', 'country_id')
    def _onchange_zipcode(self):
        if self.zipcode and self.country_id:
            if not ValidationHelpers.validate_zipcode(
                self.zipcode,
                self.country_id.code
            ):
                return {
                    'warning': {
                        'title': _('Invalid ZIP Code'),
                        'message': _(
                            'The ZIP code "%s" is not valid for %s. '
                            'Expected format: %s'
                        ) % (
                            self.zipcode,
                            self.country_id.name,
                            self._get_zipcode_format(self.country_id.code)
                        )
                    }
                }
```

## Validation in Compute Methods

```python
class Product(models.Model):
    _inherit = 'product.template'

    is_valid_barcode = fields.Boolean(
        'Valid Barcode',
        compute='_compute_barcode_validation',
        store=True
    )

    @api.depends('barcode')
    def _compute_barcode_validation(self):
        for record in self:
            if record.barcode:
                # Basic barcode validation (12-13 digits)
                record.is_valid_barcode = (
                    record.barcode.isdigit() and
                    len(record.barcode) in [12, 13]
                )
            else:
                record.is_valid_barcode = False
```

## Summary

- Create a `utils/validators.py` file for reusable validation helpers
- Use `@api.constrains` for server-side validation
- Use `@api.onchange` for client-side validation feedback
- Leverage Odoo's built-in validators (`email_validation`, `phone_validation`)
- Provide clear, actionable error messages
- Consider country-specific validation for ZIP codes and VAT numbers
- Test validation thoroughly with valid and invalid inputs
