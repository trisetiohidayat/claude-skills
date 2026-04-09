---
description: Create ir.rule XML with domain restrictions for record-level security in Odoo 19. Use when user wants to create a record rule.
---


# /security-rule - Create ir.rule XML

Creates an `ir.rule` XML record for implementing record-level security rules (Record Rules) in Odoo 19.

## Parameters

- **model_name** (required): Technical model name (e.g., 'project.project', 'sale.order')
- **rule_name** (required): Human-readable name of the rule (e.g., 'Project Manager Rule')
- **domain** (required): Domain filter expression for record access
- **groups** (optional): List of group external IDs this rule applies to (empty = global rule)
- **perm_read** (optional): Allow read access (default: 1)
- **perm_write** (optional): Allow write access (default: 1)
- **perm_create** (optional): Allow create access (default: 1)
- **perm_unlink** (optional): Allow unlink (delete) access (default: 1)
- **active** (optional): Enable/disable rule (default: True)

## What This Skill Does

1. Creates or updates the security XML file at: `{module_path}/security/{module_name}_security.xml`
2. Adds a new `ir.rule` record with proper XML ID
3. Configures domain filter for record-level access control
4. Sets up group-specific or global rules
5. Configures CRUD permissions (read, write, create, unlink)
6. Adds the security file to `__manifest__.py` data section if not already present

## Usage Examples

### Example 1: Multi-company Rule (Standard Pattern)
```
/security-rule model_name=my_model.model rule_name="Multi-company Rule" domain="[('company_id', 'in', company_ids)]"
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- Multi-company Rule -->
        <record id="my_model_comp_rule" model="ir.rule">
            <field name="name">Multi-company Rule</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('company_id', 'in', company_ids)]</field>
            <field name="active" eval="True"/>
        </record>
    </data>
</odoo>
```

### Example 2: User-specific Records (Own Records Only)
```
/security-rule model_name=project.task rule_name="User Tasks" domain="[('user_id', '=', user.id)]" groups=["base.group_user"]
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- User Tasks: Access Own Tasks Only -->
        <record id="project_task_user_rule" model="ir.rule">
            <field name="name">User Tasks: Access Own Tasks Only</field>
            <field name="model_id" ref="model_project_task"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>
    </data>
</odoo>
```

### Example 3: Department-based Access
```
/security-rule model_name=hr.employee rule_name="Department Employees" domain="[('department_id.manager_id', '=', user.id)]" groups=["hr.group_hr_manager"]
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- HR Manager: See Department Employees -->
        <record id="hr_employee_department_rule" model="ir.rule">
            <field name="name">HR Manager: See Department Employees</field>
            <field name="model_id" ref="model_hr_employee"/>
            <field name="domain_force">[('department_id.manager_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('hr.group_hr_manager'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>
    </data>
</odoo>
```

### Example 4: Portal User Access (Read-only)
```
/security-rule model_name=project.project rule_name="Portal Projects Read" domain="[('message_partner_ids', 'in', user.partner_id.id)]" groups=["base.group_portal"] perm_read=1 perm_write=0 perm_create=0 perm_unlink=0
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- Portal: Read Own Projects -->
        <record id="project_project_portal_rule" model="ir.rule">
            <field name="name">Portal: Read Own Projects</field>
            <field name="model_id" ref="model_project_project"/>
            <field name="domain_force">[('message_partner_ids', 'in', user.partner_id.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="False"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>
    </data>
</odoo>
```

### Example 5: Manager Full Access vs User Limited Access
```
/security-rule model_name=sale.order rule_name="Manager All Orders" domain="[]" groups=["sales_team.group_sale_manager"]
```

```xml
<!-- Manager: Access All Orders -->
<record id="sale_order_manager_rule" model="ir.rule">
    <field name="name">Manager: Access All Orders</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="domain_force"></field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Example 6: Complex Domain with OR Conditions
```
/security-rule model_name=project.task rule_name="User and Team Tasks" domain="['|', ('user_id', '=', user.id), ('team_id.members', 'in', user.id)]" groups=["base.group_user"]
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- User: Own Tasks + Team Tasks -->
        <record id="project_task_user_team_rule" model="ir.rule">
            <field name="name">User: Own Tasks + Team Tasks</field>
            <field name="model_id" ref="model_project_task"/>
            <field name="domain_force">['|', ('user_id', '=', user.id), ('team_id.members', 'in', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        </record>
    </data>
</odoo>
```

### Example 7: Disable Rule Without Deleting
```
/security-rule model_name=my.model rule_name="Old Rule" domain="[('state', '=', 'draft')]" active=False
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- Deprecated Rule -->
        <record id="my_model_old_rule" model="ir.rule">
            <field name="name">Old Rule</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('state', '=', 'draft')]</field>
            <field name="active" eval="False"/>
        </record>
    </data>
</odoo>
```

## Odoo 19 Conventions

1. **File Location**: `{module_path}/security/{module_name}_security.xml`
2. **XML ID Format**: `{model_name}_{rule_purpose}_rule`
3. **Domain Syntax**: Must be valid Python list expression
4. **Global Rules**: Omit `groups` field for global rules (apply to all users)
5. **Record Rule Priority**: More specific rules should have higher priority
6. **noupdate="1"**: Security rules typically marked as non-updatable
7. **Model Reference**: Use `model_{model_name}` format for model_id references

## Domain Expression Syntax

### Common Domain Variables

- `user.id` - Current user ID
- `user.company_id.id` - Current user's company ID
- `company_ids` - Current user's allowed company IDs
- `user.partner_id.id` - Current user's partner ID

### Typical Domain Patterns

```python
# Own records
[('user_id', '=', user.id)]

# Company records
[('company_id', 'in', company_ids)]

# Follower records
[('message_partner_ids', 'in', user.partner_id.id)]

# Department hierarchy
[('department_id.parent_id', 'child_of', user.employee_id.department_id.id)]

# State-based
[('state', 'in', ['draft', 'sent'])]

# Date-based
[('date', '>=', context_today().strftime('%Y-%m-01'))]

# Complex OR domain
['|',
    ('user_id', '=', user.id),
    ('team_id.members', 'in', user.id)
]

# Complex AND domain
['&',
    ('company_id', 'in', company_ids),
    ('state', '!=', 'cancel')
]
```

## Best Practices

1. **Rule Precedence**: Rules are OR'd together - user gets access if ANY rule allows it
2. **Global vs Group**: Use global rules for base restrictions, group rules for extensions
3. **Test Domains**: Always test domain expressions in Odoo shell before deploying
4. **Performance**: Keep rules simple - complex domains slow down queries
5. **Read-only Access**: Set perm_write/perm_create/perm_unlink to False for portal users
6. **Avoid Deadlocks**: Don't create circular rule dependencies
7. **Document Intent**: Comment why each rule exists
8. **Clear Cache**: Always clear cache after security rule changes

## Security Rule Types

### 1. Multi-company Rules (Required)
```xml
<record id="{model}_comp_rule" model="ir.rule">
    <field name="name">Multi-company Rule</field>
    <field name="model_id" ref="model_{model}"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

### 2. User Isolation Rules
```xml
<record id="{model}_user_rule" model="ir.rule">
    <field name="name">User: Own Records</field>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

### 3. Hierarchy Rules
```xml
<record id="{model}_manager_rule" model="ir.rule">
    <field name="name">Manager: Subordinate Records</field>
    <field name="domain_force">[('parent_id', 'child_of', user.id)]</field>
</record>
```

### 4. Portal Access Rules (Read-only)
```xml
<record id="{model}_portal_rule" model="ir.rule">
    <field name="name">Portal: Following Records</field>
    <field name="domain_force">[('message_partner_ids', 'in', user.partner_id.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

## Integration Checklist

- [ ] Security file exists
- [ ] XML ID follows naming convention
- [ ] Model reference is valid (`model_{model_name}`)
- [ ] Domain expression is syntactically correct
- [ ] Groups exist (if specified)
- [ ] Permissions are appropriate (read/write/create/unlink)
- [ ] noupdate="1" is set
- [ ] Rule tested with different user groups
- [ ] Cache cleared after deployment
- [ ] No conflicting rules with overlapping logic

## Debugging Tips

1. **Enable Rule Logging**: Set `--log-level=debug` to see which rules are applied
2. **Check Rules**: Settings > Technical > Security > Record Rules
3. **Test as User**: Switch user to test rule application
4. **Count Query**: `model.search_count(domain)` to verify filtered results
5. **Clear Cache**: Critical after rule changes - rules are heavily cached
6. **Check Global Rules**: Global rules apply to ALL users, including admin

## Common Pitfalls

- ❌ Creating rules that block admin access (admin should see everything)
- ❌ Forgetting portal rules (portal users default to no access)
- ❌ Over-restrictive domains (users can't see records they should)
- ❌ Circular dependencies between rules
- ❌ Not clearing cache after changes
- ❌ Using `user.id` when `user` is not available in context
- ❌ Complex domains that kill performance

## Advanced Example: Dynamic Rule with Context

```xml
<record id="my_model_state_rule" model="ir.rule">
    <field name="name">User: Draft Documents Only</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        ('state', '=', 'draft'),
        ('create_uid', '=', user.id)
    ]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Notes

- Security rules are record-level filters, not field-level
- Access Control Lists (ACLs) control model-level access
- Record rules are applied AFTER ACLs check
- Admin user bypasses record rules but respects ACLs
- Portal users always need explicit rules to access any data
