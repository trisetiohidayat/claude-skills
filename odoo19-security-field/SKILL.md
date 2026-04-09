---
description: Create field-level permissions using groups parameter in Odoo 19 model fields. Use when user wants to add field-level security to a model.
---


# /security-field - Create Field-Level Permissions

Creates field-level access permissions in Odoo 19 models by adding the `groups` parameter to field definitions. Field-level permissions control who can read or write specific fields.

## Parameters

- **model_name** (required): Technical model name (e.g., 'project.project', 'sale.order')
- **field_name** (required): Name of the field to secure (e.g., 'cost_price', 'notes')
- **groups** (optional): Comma-separated list of group XML IDs that can access this field
- **groups_full_name** (optional): Alternative to groups, use for calculation fields with full XML IDs

## What This Skill Does

1. Locates the model file in the module
2. Adds the `groups` parameter to the specified field
3. Handles both regular fields and computed fields
4. Adds group imports if not already present
5. Validates that the field exists in the model
6. Provides documentation on field-level security behavior

## Usage Examples

### Example 1: Basic Field Read Restriction
```
/security-field model_name=product.product field_name=standard_price groups="product.group_costing_access"
```

Before:
```python
standard_price = fields.Float('Cost')
```

After:
```python
standard_price = fields.Float(
    'Cost',
    groups='product.group_costing_access'
)
```

### Example 2: Multiple Groups
```
/security-field model_name=project.project field_name=budget_total groups="project.group_project_manager,account.group_account_user"
```

Before:
```python
budget_total = fields.Float('Budget')
```

After:
```python
budget_total = fields.Float(
    'Budget',
    groups='project.group_project_manager,account.group_account_user'
)
```

### Example 3: Computed Field with Groups
```
/security-field model_name=sale.order field_name=margin_total groups="sale.group_sale_manager" groups_full_name=True
```

Before:
```python
margin_total = fields.Float(
    'Margin',
    compute='_compute_margin_total',
    store=True
)
```

After:
```python
margin_total = fields.Float(
    'Margin',
    compute='_compute_margin_total',
    store=True,
    groups='sale.group_sale_manager'
)

@api.depends('order_line', 'order_line.margin')
def _compute_margin_total(self):
    # ... existing computation code ...
```

### Example 4: Text/Notes Field
```
/security-field model_name=hr.employee field_name=notes groups="hr.group_hr_manager"
```

Before:
```python
notes = fields.Text('Notes')
```

After:
```python
notes = fields.Text(
    'Notes',
    groups='hr.group_hr_manager'
)
```

### Example 5: Selection Field
```
/security-field model_name=project.task field_name=priority groups="project.group_project_manager"
```

Before:
```python
priority = fields.Selection([
    ('0', 'Low'),
    ('1', 'Normal'),
    ('2', 'High'),
], 'Priority')
```

After:
```python
priority = fields.Selection([
    ('0', 'Low'),
    ('1', 'Normal'),
    ('2', 'High'),
], 'Priority',
    groups='project.group_project_manager'
)
```

### Example 6: Many2one Field
```
/security-field model_name=sale.order field_name=approved_by groups="sales_team.group_sale_manager"
```

Before:
```python
approved_by = fields.Many2one('res.users', 'Approved By')
```

After:
```python
approved_by = fields.Many2one(
    'res.users',
    'Approved By',
    groups='sales_team.group_sale_manager'
)
```

### Example 7: One2many Field
```
/security-field model_name=account.move field_name=line_ids groups="account.group_account_manager"
```

Before:
```python
line_ids = fields.One2many('account.move.line', 'move_id', 'Journal Items')
```

After:
```python
line_ids = fields.One2many(
    'account.move.line',
    'move_id',
    'Journal Items',
    groups='account.group_account_manager'
)
```

### Example 8: Boolean Field
```
/security-field model_name=project.project field_name=is_confidential groups="base.group_system"
```

Before:
```python
is_confidential = fields.Boolean('Confidential')
```

After:
```python
is_confidential = fields.Boolean(
    'Confidential',
    groups='base.group_system'
)
```

## Field-Level Security Behavior

### How Groups Parameter Works

1. **Read Access**: Users must belong to at least one specified group to READ the field
2. **Write Access**: Users must belong to at least one specified group to WRITE the field
3. **Field Visibility**: If user lacks access, field is completely hidden from views
4. **Search/Filter**: Restricted fields cannot be used in search or filters
5. **Export**: Restricted fields are excluded from exports
6. **API**: Field is excluded from JSON-RPC and XML-RPC responses

### Default Behavior (No Groups)
```python
# Accessible to all users with model access
name = fields.Char('Name')
```

### Single Group Restriction
```python
# Only users in product.group_costing_access
cost_price = fields.Float('Cost', groups='product.group_costing_access')
```

### Multiple Groups (OR Logic)
```python
# Users in EITHER manager OR accounting group
budget = fields.Float('Budget', groups='project.group_project_manager,account.group_account_user')
```

## Odoo 19 Conventions

1. **Group Format**: Comma-separated string of XML IDs
2. **Short Format**: Use `module.group_name` (not full external ID)
3. **Position**: `groups` parameter typically placed last in field definition
4. **Field Types**: Works with ALL field types (Char, Float, Many2one, One2many, etc.)
5. **Computed Fields**: Add `groups` parameter after `compute` and `store`
6. **Related Fields**: Inherits security from source field
7. **View Rendering**: Hidden fields are completely removed from view rendering
8. **Performance**: Field-level security has minimal performance impact

## Best Practices

1. **Principle of Least Privilege**: Restrict sensitive fields by default
2. **Document Rationale**: Comment WHY field is restricted
3. **Use Existing Groups**: Leverage standard Odoo groups when possible
4. **Create Custom Groups**: For module-specific field security
5. **Test Thoroughly**: Test with users in/out of groups
6. **Consider Dependencies**: Ensure referenced groups exist
7. **Field Naming**: No special naming needed for restricted fields
8. **View Independent**: Works automatically in all views (tree, form, search, etc.)

## Common Use Cases

### 1. Financial Data
```python
# Cost prices for accounting/managers only
standard_price = fields.Float(
    'Cost',
    groups='account.group_account_user,product.group_costing_access'
)

# Margin calculations for managers only
margin = fields.Float(
    'Margin',
    compute='_compute_margin',
    groups='sales_team.group_sale_manager'
)
```

### 2. HR Sensitive Data
```python
# Salary information for HR managers only
salary = fields.Float(
    'Salary',
    groups='hr.group_hr_manager'
)

# Performance reviews for managers only
review_notes = fields.Text(
    'Review Notes',
    groups='hr.group_hr_manager'
)
```

### 3. Internal Notes
```python
# Internal notes not visible to customers
internal_notes = fields.Text(
    'Internal Notes',
    groups='base.group_user'
)
```

### 4. System/Technical Fields
```python
# Technical fields for system administrators
technical_id = fields.Char(
    'Technical ID',
    groups='base.group_system'
)

# Debug information
debug_info = fields.Text(
    'Debug Info',
    groups='base.group_system'
)
```

### 5: Approval Workflows
```python
# Approval fields for managers
approved_by = fields.Many2one(
    'res.users',
    'Approved By',
    groups='sales_team.group_sale_manager'
)

approved_date = fields.Datetime(
    'Approved Date',
    groups='sales_team.group_sale_manager'
)
```

## Integration with Views

Field-level security automatically works across all views:

### Form View
```xml
<field name="cost_price"/>
<!-- Hidden if user lacks access -->
```

### Tree View
```xml
<tree>
    <field name="name"/>
    <field name="cost_price"/>
    <!-- Column hidden if user lacks access -->
</tree>
```

### Search View
```xml
<search>
    <field name="name"/>
    <field name="cost_price"/>
    <!-- Filter hidden if user lacks access -->
</search>
```

## Complete Model Example

```python
from odoo import models, fields, api

class ProjectProject(models.Model):
    _name = 'project.project'
    _description = 'Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Public fields (all users with model access)
    name = fields.Char('Project Name', required=True, tracking=True)
    description = fields.Text('Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('done', 'Done'),
    ], 'Status', default='draft', tracking=True)

    # Restricted: Managers only
    budget_total = fields.Float(
        'Total Budget',
        groups='project.group_project_manager'
    )

    # Restricted: Accounting only
    cost_analytic_account = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        groups='account.group_account_user'
    )

    # Restricted: Both managers and accounting (OR logic)
    margin = fields.Float(
        'Margin',
        compute='_compute_margin',
        store=True,
        groups='project.group_project_manager,account.group_account_user'
    )

    # Restricted: Internal users only (not portal)
    internal_notes = fields.Text(
        'Internal Notes',
        groups='base.group_user'
    )

    # Restricted: System administrators only
    technical_reference = fields.Char(
        'Technical Ref',
        groups='base.group_system'
    )

    @api.depends('task_ids', 'task_ids.cost')
    def _compute_margin(self):
        for project in self:
            project.margin = sum(project.task_ids.mapped('cost')) - project.budget_total
```

## Security Groups to Use

### Standard Odoo Groups

```python
# Sales
'sales_team.group_sale_salesman'         # Sales user
'sales_team.group_sale_manager'          # Sales manager

# Accounting
'account.group_account_user'             # Accounting advisor
'account.group_account_manager'          # Accounting manager

# HR
'hr.group_hr_user'                       # HR officer
'hr.group_hr_manager'                    # HR manager

# Project
'project.group_project_user'             # Project user
'project.group_project_manager'          # Project manager

# Inventory
'stock.group_stock_user'                 # Inventory user
'stock.group_stock_manager'              # Inventory manager

# Manufacturing
'mrp.group_mrp_user'                     # Manufacturing user
'mrp.group_mrp_manager'                  # Manufacturing manager

# Base/System
'base.group_user'                        # All internal users
'base.group_portal'                      # Portal users
'base.group_public'                      # Public users
'base.group_system'                      # System administrators
```

## Advanced: Conditional Field Access with Compute

Sometimes you want different behavior based on groups:

```python
@api.depends_context('uid')
def _compute_field_name(self):
    for record in self:
        if record.env.user.has_group('my_module.group_manager'):
            record.field_name = record._get_manager_value()
        else:
            record.field_name = record._get_user_value()
```

However, using the `groups` parameter is simpler and preferred.

## Testing Field-Level Security

```python
# Test in Odoo shell
./odoo-bin shell -c odoo.conf

# Test as different users
manager = env['res.users'].search([('login', '=', 'manager@example.com')])
user = env['res.users'].search([('login', '=', 'user@example.com')])

# Test field access
product = env['product.product'].sudo(user).search([])[0]

# Check if field is accessible
try:
    print(product.standard_price)  # Should fail for non-privileged users
except AccessError:
    print("Field access denied as expected")

# Test with manager
product = env['product.product'].sudo(manager).search([])[0]
print(product.standard_price)  # Should work
```

## Integration Checklist

- [ ] Field exists in model
- [ ] Groups parameter added to field definition
- [ ] Groups referenced actually exist
- [ ] Field tested with users in the group
- [ ] Field tested with users NOT in the group
- [ ] Views render correctly for both cases
- [ ] Search/filter behavior verified
- [ ] Export behavior verified
- [ ] API access verified
- [ ] No broken references or imports

## Common Pitfalls

- ❌ Forgetting to add groups parameter (leaves field unrestricted)
- ❌ Using wrong group XML ID format
- ❌ Not testing with users outside the group
- ❌ Assuming field is hidden but it's still accessible via API
- ❌ Not clearing cache after changes
- ❌ Using groups that don't exist
- ❌ Over-restricting fields (too many users lose access)
- ❌ Forgetting that related fields inherit security from source

## Troubleshooting

### Field Still Visible After Adding Groups
- Clear cache and restart server
- Verify user is NOT in the specified group
- Check that field definition was reloaded (module upgrade)
- Confirm correct group XML ID

### Field Not Visible for Authorized Users
- Verify user IS in the specified group
- Check group XML ID is correct
- Ensure field is defined in model
- Check for typos in groups parameter

### Computed Field Issues
- Add groups parameter after compute/store
- Ensure computed field still calculates correctly
- Test that computation works for authorized users

## Notes

- Field-level security is VIEW-LEVEL (not record-level)
- It controls which USERS can see which FIELDS
- Record rules control which RECORDS users can see
- ACLs control which MODELS users can access
- All three work together: ACL → Record Rules → Field Security
- Field-level security is enforced server-side, not just UI
- Restricted fields are completely removed from API responses
- Use field-level security sparingly (it can be confusing)
- Document restricted fields thoroughly for developers
