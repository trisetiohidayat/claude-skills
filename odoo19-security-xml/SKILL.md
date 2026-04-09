---
description: Create ir.model.access CSV file for model-level access control (ACL) in Odoo 19. Use when user wants to create access control lists.
---


# /security-xml - Create ir.model.access CSV

Creates `ir.model.access` CSV records for implementing Access Control Lists (ACLs) in Odoo 19. ACLs control CRUD operations at the model level.

## Parameters

- **model_name** (required): Technical model name (e.g., 'project.project', 'sale.order')
- **access_name** (required): Descriptive name for this access right (e.g., 'manager', 'user', 'portal')
- **group_id** (optional): External ID of group this access applies to (empty = all users)
- **perm_read** (optional): Allow read access (default: 1)
- **perm_write** (optional): Allow write access (default: 0)
- **perm_create** (optional): Allow create access (default: 0)
- **perm_unlink** (optional): Allow unlink (delete) access (default: 0)

## What This Skill Does

1. Creates or updates the CSV file at: `{module_path}/security/ir.model.access.csv`
2. Adds a new ACL entry with proper access permissions
3. Configures model-level CRUD operations
4. Sets up group-specific or global access rights
5. Ensures proper CSV formatting (comma-separated, proper quoting)
6. Validates that the model exists in the module

## Usage Examples

### Example 1: Full Access for Manager Group
```
/security-xml model_name=project.project access_name=manager group_id=my_project.group_project_manager perm_read=1 perm_write=1 perm_create=1 perm_unlink=1
```

Generated CSV entry:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_project_project_manager,access_project_project_manager,model_project_project,my_project.group_project_manager,1,1,1,1
```

### Example 2: Read-only for User Group
```
/security-xml model_name=project.project access_name=user group_id=my_project.group_project_user perm_read=1 perm_write=0 perm_create=0 perm_unlink=0
```

Generated CSV entry:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_project_project_user,access_project_project_user,model_project_project,my_project.group_project_user,1,0,0,0
```

### Example 3: Portal Read Access
```
/security-xml model_name=project.project access_name=portal group_id=base.group_portal perm_read=1 perm_write=0 perm_create=0 perm_unlink=0
```

Generated CSV entry:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_project_project_portal,access_project_project_portal,model_project_project,base.group_portal,1,0,0,0
```

### Example 4: Public Read Access (Website Visitors)
```
/security-xml model_name=website.page access_name=public group_id=base.group_public perm_read=1 perm_write=0 perm_create=0 perm_unlink=0
```

Generated CSV entry:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_website_page_public,access_website_page_public,model_website_page,base.group_public,1,0,0,0
```

### Example 5: Complete ACL Set for Custom Model
```
/security-xml model_name=my.model access_name=manager group_id=my_module.group_manager perm_read=1 perm_write=1 perm_create=1 perm_unlink=1
```

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_manager,access_my_model_manager,model_my_model,my_module.group_manager,1,1,1,1
access_my_model_user,access_my_model_user,model_my_model,my_module.group_user,1,1,0,0
access_my_model_portal,access_my_model_portal,model_my_model,base.group_portal,1,0,0,0
```

### Example 6: Standard Employee Access
```
/security-xml model_name=my.model access_name=employee group_id=base.group_user perm_read=1 perm_write=1 perm_create=0 perm_unlink=0
```

Generated CSV entry:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_employee,access_my_model_employee,model_my_model,base.group_user,1,1,0,0
```

## CSV File Structure

The `ir.model.access.csv` file must have the following structure:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model}_{group},access_{model}_{group},model_{model},{group_external_id},1,1,1,1
```

### Column Explanations

- **id**: Unique identifier for this ACL record (XML ID)
- **name**: Human-readable name (usually same as id)
- **model_id:id**: Reference to the model being secured
- **group_id:id**: Reference to the group (empty = global for all users)
- **perm_read**: 1 = allow read, 0 = deny read
- **perm_write**: 1 = allow write, 1 = deny write
- **perm_create**: 1 = allow create, 0 = deny create
- **perm_unlink**: 1 = allow delete, 0 = deny delete

## Odoo 19 Conventions

1. **File Location**: `{module_path}/security/ir.model.access.csv`
2. **File Format**: Comma-separated values (CSV), properly quoted
3. **ID Format**: `access_{model_name}_{access_name}`
4. **Header Required**: First line must contain column names
5. **Model Reference**: `model_{model_name}` (dots become underscores)
6. **Group Reference**: `{module}.{xml_id}` or empty for global
7. **Binary Values**: Use 1 (true) or 0 (false) for permissions
8. **noupdate**: ACLs are loaded without noupdate, can be overridden

## Best Practices

1. **Principle of Least Privilege**: Default to no access, grant minimally
2. **Layered Access**: Create ACLs for manager, user, portal, public
3. **Consistent Naming**: Use `{module}_{model}_{role}` pattern
4. **Document Intent**: Comment sections in CSV file (lines starting with #)
5. **Test Thoroughly**: Test with each user group
6. **Use Groups**: Don't give rights to all users unless necessary
7. **Separate Read/Write**: Consider read-only users carefully
8. **Portal/Public**: Always create explicit ACLs for portal/public users

## Standard ACL Template for New Models

```csv
################################################################################
# Access Control Lists for my.model
################################################################################

# Manager: Full access
access_my_model_manager,access_my_model_manager,model_my_model,my_module.group_manager,1,1,1,1

# User: Read and write, no create/delete
access_my_model_user,access_my_model_user,model_my_model,my_module.group_user,1,1,0,0

# Portal: Read only
access_my_model_portal,access_my_model_portal,model_my_model,base.group_portal,1,0,0,0
```

## Complete Example: Project Management Module

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
################################################################################
# Project Project
################################################################################
access_project_project_manager,access_project_project_manager,model_project_project,project.group_project_manager,1,1,1,1
access_project_project_user,access_project_project_user,model_project_project,project.group_project_user,1,1,1,0
access_project_project_portal,access_project_project_portal,model_project_project,base.group_portal,1,0,0,0

################################################################################
# Project Task
################################################################################
access_project_task_manager,access_project_task_manager,model_project_task,project.group_project_manager,1,1,1,1
access_project_task_user,access_project_task_user,model_project_task,project.group_project_user,1,1,1,0
access_project_task_portal,access_project_task_portal,model_project_task,base.group_portal,1,0,0,0
```

## Access Rights Combinations

### Full Access (Manager)
```csv
access_model_manager,access_model_manager,model_my_model,my_module.group_manager,1,1,1,1
```
- Read: Yes
- Write: Yes
- Create: Yes
- Delete: Yes

### Read-Write Access (User)
```csv
access_model_user,access_model_user,model_my_model,my_module.group_user,1,1,0,0
```
- Read: Yes
- Write: Yes
- Create: No
- Delete: No

### Read-Only Access (Portal/Public)
```csv
access_model_portal,access_model_portal,model_my_model,base.group_portal,1,0,0,0
```
- Read: Yes
- Write: No
- Create: No
- Delete: No

### Create-Only Access (Special Case)
```csv
access_model_create_only,access_model_create_only,model_my_model,my_module.group_creator,0,0,1,0
```
- Read: No (unusual, but possible)
- Write: No
- Create: Yes
- Delete: No

## Integration Checklist

- [ ] CSV file exists at `{module_path}/security/ir.model.access.csv`
- [ ] File has proper header row
- [ ] CSV format is valid (commas, quotes)
- [ ] Model references are correct (`model_{model_name}`)
- [ ] Group references exist
- [ ] Access rights are appropriate
- [ ] At least one group has create/unlink access
- [ ] Portal/public access is explicitly defined
- [ ] File is added to `__manifest__.py` (if custom module)
- [ ] Tested with each user group

## Common Group References

```csv
# Internal Users
base.group_user              # All internal users (Employee)
base.group_system            # System settings (technical)

# Portal/Public
base.group_portal            # Portal users (external)
base.group_public            # Public users (website visitors)

# Standard Odoo Groups
sales_team.group_sale_salesman_all_leads    # Sales: All leads
sales_team.group_sale_manager                # Sales: Manager
account.group_account_user                   # Accounting: Advisor
account.group_account_manager                # Accounting: Manager
hr.group_hr_user                             # HR: Officer
hr.group_hr_manager                          # HR: Manager
project.group_project_manager                # Project: Manager
project.group_project_user                   # Project: User
```

## Common Pitfalls

- ❌ Forgetting portal/public ACLs (portal users can't access anything)
- ❌ Too permissive global ACLs (granting to all users)
- ❌ Inconsistent naming between ACLs and groups
- ❌ Invalid CSV format (missing commas, wrong quotes)
- ❌ Using wrong model reference format (must use underscores)
- ❌ Not testing with different user groups
- ❌ Giving unlink rights without proper consideration
- ❌ Forgetting that admin doesn't bypass ACLs (only bypasses record rules)

## Testing ACLs

```python
# Test in Odoo shell
./odoo-bin shell -c odoo.conf

# Check access
model = env['my.model']
has_read = model.check_access_rights('read')
has_write = model.check_access_rights('write')
has_create = model.check_access_rights('create')
has_unlink = model.check_access_rights('unlink')

print(f"Read: {has_read}, Write: {has_write}, Create: {has_create}, Unlink: {has_unlink}")

# Test as specific user
user = env['res.users'].search([('login', '=', 'testuser@example.com')])
model = env['my.model'].sudo(user).search([])
```

## Troubleshooting

### "Access Error" Message
- Check if ACL exists for the user's group
- Verify group_id reference is correct
- Ensure perm_read, perm_write, etc. are set to 1
- Clear cache and restart Odoo

### CSV Import Errors
- Verify CSV format (use proper quoting)
- Check for trailing commas
- Ensure no spaces around commas in CSV
- Validate header row matches exactly

### Portal Users Can't Access
- Portal users need explicit ACLs
- Always create ACLs with `base.group_portal`
- Test with portal user, not admin

### Admin Can't Access
- ACLs apply to admin too (unlike record rules)
- Create ACL for `base.group_system` if needed
- Or create group ACL with admin in the group

## Advanced: Conditional Access with Groups

Sometimes you want multiple access levels:

```csv
# Level 1: Basic users - read and write existing
access_my_model_basic,access_my_model_basic,model_my_model,my_module.group_basic,1,1,0,0

# Level 2: Advanced users - read, write, create
access_my_model_advanced,access_my_model_advanced,model_my_model,my_module.group_advanced,1,1,1,0

# Level 3: Managers - full access including delete
access_my_model_manager,access_my_model_manager,model_my_model,my_module.group_manager,1,1,1,1
```

## Notes

- ACLs are checked BEFORE record rules
- ACLs are model-level, record rules are record-level
- Both ACLs AND record rules must allow access
- Admin user respects ACLs but bypasses record rules
- Clear cache after ACL changes (they are cached)
- ACLs cannot use domain filters (that's what record rules are for)
- CSV file is loaded on module install/upgrade
