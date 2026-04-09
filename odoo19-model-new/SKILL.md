---
description: Generate a new Odoo 19 model class with proper _name, _description setup. Use when user wants to add a new model to an existing module.
---


# Odoo 19 Model Creation

Generate a new Odoo 19 model with proper structure following Odoo 19 conventions.

## Instructions

1. **Determine the file location:**
   - Models should be in: `{module_name}/models/{model_filename}.py`
   - Use singular form for filename (e.g., `book.py` not `books.py`)

2. **Generate the model class structure:**

```python
from odoo import models, fields, _
from odoo.exceptions import ValidationError

class {ModelClassName}(models.Model):
    _name = '{model_name}'
    _description = '{model_description}'
    {inherit_line}
    {order_line}

    # Field definitions will go here
    name = fields.Char(string='Name', required=True)
```

3. **Handle inheritance properly:**
   - For new models: Use `_name` only
   - For extending existing models: Use both `_inherit` and `_name`
   - For mixins: Add after the model definition

4. **Common mixins to include:**
   - `mail.thread` - for messaging and chatter
   - `mail.activity.mixin` - for activities
   - `image.mixin` - for image fields
   - `address.mixin` - for address fields

5. **Add to __init__.py:**
   - Update `models/__init__.py` to import the new model
   - Format: `from . import {model_filename}`

6. **Include these standard patterns:**

```python
# Check if extending existing model
_inherit = '{parent_model}'  # Only if extending
_name = '{model_name}'  # Always include
```

## Usage Examples

### Basic Model

```bash
/model-new library_book book.library "Library Book Management"
```

Output:
```python
# library_book/models/book.py

from odoo import models, fields

class Book(models.Model):
    _name = 'book.library'
    _description = 'Library Book Management'

    name = fields.Char(string='Title', required=True)
    isbn = fields.Char(string='ISBN')
    author_ids = fields.Many2many('res.partner', string='Authors')
```

### Model with Mail Thread

```bash
/model-new sale_order sale.order "Sale Order" inherit="mail.thread"
```

Output:
```python
# sale_order/models/sale_order.py

from odoo import models, fields, _

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Order Reference', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='State', default='draft', tracking=True)
```

### Model with Default Order

```bash
/model-new project_task project.task "Project Task" order="priority desc, sequence asc"
```

Output:
```python
# project_task/models/task.py

from odoo import models, fields, _

class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Project Task'
    _order = 'priority desc, sequence asc'

    name = fields.Char(string='Task', required=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
    ], string='Priority', default='1')
    sequence = fields.Integer(string='Sequence', default=10)
```

### Model with Multiple Features

```bash
/model-new hr_employee hr.employee "Employee" inherit="mail.thread,image.mixin" order="name asc"
```

Output:
```python
# hr_employee/models/employee.py

from odoo import models, fields, _

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _description = 'Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'name asc'

    name = fields.Char(string='Employee Name', required=True, tracking=True)
    image_1920 = fields.Image(string='Image')
    department_id = fields.Many2one('hr.department', string='Department')
    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities')
```

## Best Practices

1. **Naming Conventions:**
   - Use lowercase with underscores for model names
   - Use module prefix for custom models (e.g., `library_book`)
   - Class names should use PascalCase

2. **Description:**
   - Keep descriptions clear and concise
   - Use user-friendly language
   - Avoid technical jargon

3. **Ordering:**
   - Specify logical default order
   - Use 'desc' or 'asc' explicitly
   - Consider multiple fields for sorting

4. **Inheritance:**
   - Include mail.thread for models needing chatter
   - Include mail.activity.mixin for workflows
   - Document custom mixins

5. **Security:**
   - Remember to create access rights in security/
   - Add record rules if needed
   - Consider field-level permissions

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py  # Import new model here
│   └── {model_filename}.py
├── views/
│   └── {model_filename}_views.xml
└── security/
    ├── {model_filename}_security.xml
    └── ir.model.access.csv
```

## Next Steps

After creating the model, use:
- `/field-add` - Add fields to the model
- `/view-form` - Create form views
- `/view-tree` - Create tree views
- `/security-group` - Create security groups
- `/security-rule` - Create record rules
