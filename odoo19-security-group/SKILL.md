---
description: Create res.groups XML for user access groups in Odoo 19. Use when user wants to create a security group.
---


# /security-group - Create res.groups XML

Creates a `res.groups` XML record for defining user access groups in Odoo 19 security.

## Parameters

- **module_name** (required): Technical name of your module (e.g., 'my_module')
- **group_name** (required): Human-readable name of the group (e.g., 'Project Manager')
- **category** (required): Application category for grouping (e.g., 'Project', 'Sales', 'HR')
- **implied_groups** (optional): List of external IDs of groups that this group implies
- **users** (optional): List of user external IDs to add to this group
- **comment** (optional): Description of the group's purpose

## What This Skill Does

1. Creates or updates the security XML file at: `{module_path}/security/{module_name}_security.xml`
2. Adds a new `res.groups` record with proper XML ID
3. Configures group hierarchy with implied groups
4. Assigns users to the group
5. Adds the security file to `__manifest__.py` data section if not already present

## Usage Examples

### Example 1: Basic Group Creation
```
/security-group module_name=my_project group_name="Project Manager" category="Project"
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- Project Manager Group -->
        <record id="group_project_manager" model="res.groups">
            <field name="name">Project Manager</field>
            <field name="category_id" ref="base.module_category_project_management"/>
            <field name="comment">Users with full access to project management features</field>
        </record>
    </data>
</odoo>
```

### Example 2: Group with Implied Groups
```
/security-group module_name=my_project group_name="Project Director" category="Project" implied_groups=["base.group_user", "my_project.group_project_manager"]
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- Project Director Group -->
        <record id="group_project_director" model="res.groups">
            <field name="name">Project Director</field>
            <field name="category_id" ref="base.module_category_project_management"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user')), (4, ref('my_project.group_project_manager'))]"/>
            <field name="comment">Users with director-level project access</field>
        </record>
    </data>
</odoo>
```

### Example 3: Group with Assigned Users
```
/security-group module_name=my_hr group_name="HR Officer" category="Human Resources" users=["base.user_admin", "base.user_demo"]
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- HR Officer Group -->
        <record id="group_hr_officer" model="res.groups">
            <field name="name">HR Officer</field>
            <field name="category_id" ref="base.module_category_human_resources"/>
            <field name="users" eval="[(4, ref('base.user_admin')), (4, ref('base.user_demo'))]"/>
            <field name="comment">HR officers with employee management access</field>
        </record>
    </data>
</odoo>
```

### Example 4: Multi-level Group Hierarchy
```
/security-group module_name=my_sales group_name="Sales Director" category="Sales" implied_groups=["base.group_user", "sales_team.group_sale_salesman", "sales_team.group_sale_manager"]
```

Generated XML:
```xml
<odoo>
    <data noupdate="1">
        <!-- Sales Director Group -->
        <record id="group_sales_director" model="res.groups">
            <field name="name">Sales Director</field>
            <field name="category_id" ref="base.module_category_sales"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user')), (4, ref('sales_team.group_sale_salesman')), (4, ref('sales_team.group_sale_manager'))]"/>
            <field name="comment">Sales directors with full sales management access</field>
        </record>
    </data>
</odoo>
```

## Odoo 19 Conventions

1. **File Naming**: `{module_name}_security.xml` in the `security/` directory
2. **XML ID Format**: `{module_name}.group_{descriptive_name}`
3. **noupdate="1"**: Security groups should not be updated during module upgrades
4. **Category References**: Use `base.module_category_{category_name}` for standard categories
5. **Group Implies**: Use `eval="[(4, ref(...))]"` syntax for adding implied groups
6. **Multi-company**: Groups inherit company settings automatically

## Common Category References

- `base.module_category_project_management` - Project Management
- `base.module_category_sales` - Sales
- `base.module_category_human_resources` - Human Resources
- `base.module_category_accounting` - Accounting
- `base.module_category_inventory` - Inventory
- `base.module_category_manufacturing` - Manufacturing
- `base.module_category_marketing` - Marketing
- `base.module_category_website` - Website

## Best Practices

1. **Use Descriptive Names**: Group names should clearly indicate their purpose
2. **Follow Hierarchy**: Create base groups first, then extend with implied groups
3. **Add Comments**: Always include comments explaining the group's purpose
4. **Use noupdate="1"**: Prevent accidental modifications during upgrades
5. **Consider Multi-company**: Test group behavior in multi-company environments
6. **Default Groups**: Every custom module should have at least one user group
7. **Portal/Public**: Use `base.group_portal` or `base.group_public` for external access

## Integration Checklist

- [ ] Security file exists at `{module_path}/security/{module_name}_security.xml`
- [ ] XML ID follows naming convention: `{module_name}.group_{name}`
- [ ] Category reference is valid
- [ ] Implied groups exist (check external IDs)
- [ ] Users exist (check external IDs)
- [ ] Security file added to `__manifest__.py` data section
- [ ] noupdate="1" is set on data tag
- [ ] Group tested in Settings > Users & Companies > Groups

## Advanced Example: Portal Group with Application Access

```
/security-group module_name=my_portal group_name="Project Portal" category="Project" implied_groups=["base.group_portal"]
```

```xml
<odoo>
    <data noupdate="1">
        <!-- Project Portal Access -->
        <record id="group_project_portal" model="res.groups">
            <field name="name">Project Portal</field>
            <field name="category_id" ref="base.module_category_project_management"/>
            <field name="implied_ids" eval="[(4, ref('base.group_portal'))]"/>
            <field name="comment">Portal users with access to project information</field>
        </record>
    </data>
</odoo>
```

## Notes

- Groups are cached; clear cache after modifications
- Group changes require users to re-login
- Implied groups automatically grant all permissions of parent groups
- Portal users cannot have admin rights or access to internal groups
