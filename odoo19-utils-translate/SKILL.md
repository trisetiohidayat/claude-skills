---
description: Create i18n translations with _() for Odoo 19 models. Use when user wants to add translations to a module.
---


# Odoo 19 Translation Utility (/utils-translate)

This skill helps you add proper i18n (internationalization) translations to your Odoo 19 modules using the `_()` translation function.

## Translation Function Overview

In Odoo 19, translations are handled using the `_()` function, which is imported at the module level:

```python
from odoo import _
```

## When to Use Translations

You should mark strings for translation in these contexts:

1. **Field labels and help text**
2. **Selection field options**
3. **Validation error messages**
4. **User-facing notifications**
5. **View tooltips and placeholders**
6. **Button labels**
7. **Menu items**

## Translation in Models

### Field Labels and Help Text

```python
from odoo import _, models, fields, api

class Book(models.Model):
    _name = 'library.book'
    _description = _('Book')  # Model name should be translatable

    name = fields.Char(
        string=_('Book Title'),  # Field label
        help=_('Enter the title of the book'),  # Help text
        required=True
    )

    isbn = fields.Char(
        string=_('ISBN'),
        help=_('International Standard Book Number')
    )

    state = fields.Selection([
        ('draft', _('Draft')),
        ('available', _('Available')),
        ('borrowed', _('Borrowed')),
        ('lost', _('Lost')),
    ], string=_('Status'), default='draft', required=True)
```

### Computed Field Display Names

```python
display_name = fields.Char(
    string=_('Display Name'),
    compute='_compute_display_name'
)

@api.depends('name', 'isbn')
def _compute_display_name(self):
    for record in self:
        if record.name and record.isbn:
            record.display_name = _('%s (ISBN: %s)') % (record.name, record.isbn)
        else:
            record.display_name = record.name or _('Untitled')
```

### Validation Error Messages

```python
from odoo.exceptions import ValidationError

@api.constrains('isbn')
def _check_isbn(self):
    for record in self:
        if record.isbn and not self._validate_isbn(record.isbn):
            raise ValidationError(
                _('The ISBN "%s" is not valid. Please enter a valid ISBN.') % record.isbn
            )
```

### Onchange Warnings

```python
@api.onchange('publication_date')
def _onchange_publication_date(self):
    if self.publication_date and self.publication_date > fields.Date.today():
        return {
            'warning': {
                'title': _('Invalid Date'),
                'message': _('Publication date cannot be in the future.')
            }
        }
```

## Translation in Views

### Form View Labels

```xml
<record id="view_book_form" model="ir.ui.view">
    <field name="name">library.book.form</field>
    <field name="model">library.book</field>
    <field name="arch" type="xml">
        <form string="Book">
            <sheet>
                <group>
                    <group>
                        <field name="name"/>
                        <field name="isbn"/>
                    </group>
                    <group>
                        <field name="publication_date"/>
                        <field name="category_id"/>
                    </group>
                </group>
                <notebook>
                    <page string="Description" name="description">
                        <field name="description" placeholder="Enter a detailed description..."/>
                    </page>
                    <page string="Borrowing History" name="history">
                        <field name="borrowing_ids">
                            <tree>
                                <field name="borrower_id"/>
                                <field name="borrow_date"/>
                                <field name="return_date"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

**Note:** In views, string attributes are automatically extracted for translation. You don't need to use `_()` in XML files.

### Action and Menu Labels

```xml
<!-- Action Window -->
<record id="action_library_book" model="ir.actions.act_window">
    <field name="name">Books</field>
    <field name="res_model">library.book</field>
    <field name="view_mode">tree,form</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first book!
        </p>
    </field>
</record>

<!-- Menu Item -->
<menuitem id="menu_library_root"
          name="Library"
          sequence="10"/>
<menuitem id="menu_library_book"
          name="Books"
          parent="menu_library_root"
          action="action_library_book"
          sequence="10"/>
```

## Translation in Controllers

```python
from odoo import http
from odoo.http import request
from odoo import _

class LibraryController(http.Controller):

    @http.route('/library/book/<int:book_id>', type='http', auth='user')
    def book_detail(self, book_id):
        book = request.env['library.book'].browse(book_id)
        if not book.exists():
            return request.render(
                'http.404',
                {
                    'message': _('The requested book does not exist.')
                }
            )
        return request.render('library.book_detail', {'book': book})
```

## Translation in Security and Data Files

### Group Names

```xml
<odoo>
    <data noupdate="1">
        <record id="group_library_user" model="res.groups">
            <field name="name">Library User</field>
            <field name="category_id" ref="base.module_category_library"/>
            <field name="comment">Regular users of the library system.</field>
        </record>

        <record id="group_library_manager" model="res.groups">
            <field name="name">Library Manager</field>
            <field name="category_id" ref="base.module_category_library"/>
            <field name="implied_ids" eval="[(4, ref('group_library_user'))]"/>
            <field name="comment">Managers with full access to library features.</field>
        </record>
    </data>
</odoo>
```

## String Formatting with Translations

When using string formatting with translations, always use named placeholders for better reusability:

```python
# Good - Named placeholders
message = _('Book "%(book_name)s" has been borrowed by %(borrower)s') % {
    'book_name': self.name,
    'borrower': borrower.name
}

# Avoid - Positional placeholders (harder to translate)
message = _('Book "%s" has been borrowed by %s') % (self.name, borrower.name)
```

## Plural Forms

For messages with plural forms, use `_n()`:

```python
from odoo import _n

count = len(self.borrowing_ids)
message = _n(
    'This book has been borrowed %(count)d time',
    'This book has been borrowed %(count)d times',
    count
) % {'count': count}
```

## Generating Translation Templates

After adding translatable strings to your module:

1. **Update your module's POT template file:**
   ```bash
   cd /path/to/odoo
   ./odoo-bin -c odoo.conf -d your_db --i18n-export=your_module/i18n/your_module.pot --init=your_module --stop-after-init
   ```

2. **Create a translation file for a language:**
   ```bash
   cp your_module/i18n/your_module.pot your_module/i18n/fr_FR.po
   ```

3. **Edit the .po file** with a translation tool like Poedit

4. **Load translations** in Odoo:
   - Go to Settings > Translations > Import Translation
   - Or restart Odoo (translations are loaded automatically)

## Translation Best Practices

1. **Keep strings simple and complete**
   ```python
   # Good
   _('Book not found')

   # Avoid
   _('The book you are looking for could not be found in the database')
   ```

2. **Use separate strings for different contexts**
   ```python
   # Good - Context-specific
   _('Book')  # Noun
   _('Book (verb)')  # Action

   # Better - Use context parameter if available
   _('Book', context='noun')
   ```

3. **Don't translate technical terms**
   ```python
   # Don't translate field names, model names, technical codes
   record['state'] = 'draft'  # No translation
   _('Draft')  # Translate display value
   ```

4. **Translate user messages only**
   ```python
   # User-facing
   raise ValidationError(_('Invalid ISBN format'))

   # Developer/debug messages - no translation
   logging.debug('Processing ISBN validation for record %s', record.id)
   ```

5. **Keep placeholders descriptive**
   ```python
   # Good
   _('Order %(order_name)s for customer %(customer_name)s') % {
       'order_name': order.name,
       'customer_name': customer.name
   }

   # Avoid
   _('Order %s for %s') % (order.name, customer.name)
   ```

## Common Translation Patterns

### Success Messages

```python
def action_confirm(self):
    self.write({'state': 'confirmed'})
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'message': _('The book has been successfully confirmed.'),
            'type': 'success',
        }
    }
```

### Warning Messages

```python
def action_archive(self):
    if self.borrowing_ids.filtered(lambda b: not b.return_date):
        return {
            'warning': {
                'title': _('Cannot Archive'),
                'message': _(
                    'This book cannot be archived because it has '
                    'unreturned borrowings.'
                )
            }
        }
    self.write({'active': False})
```

### Confirmation Dialogs

```python
def action_return(self):
    return {
        'type': 'ir.actions.act_window',
        'name': _('Return Book'),
        'res_model': 'library.book.return.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_book_id': self.id}
    }
```

## Module Structure for Translations

Ensure your module has the proper structure:

```
your_module/
├── i18n/
│   ├── your_module.pot      # Translation template
│   ├── fr_FR.po             # French translation
│   ├── de_DE.po             # German translation
│   └── es_ES.po             # Spanish translation
├── models/
│   └── your_model.py        # Model with _() imports
├── views/
│   └── your_views.xml       # Views (auto-extracted)
└── __manifest__.py
```

## Testing Translations

Change the user language in Odoo to test translations:

1. Go to Settings > Users & Companies > Users
2. Open your user
3. Set "Language" to test language
4. Reload the page
5. Verify all strings are properly translated

## Summary

- Import `_` from `odoo` at module level
- Mark all user-facing strings with `_()`
- Use named placeholders for string formatting
- Keep strings simple and context-appropriate
- Generate POT files after adding translatable strings
- Don't translate technical identifiers or debug messages
- Test translations by changing user language
