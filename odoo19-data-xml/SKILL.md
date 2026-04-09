---
description: Create data XML file with record elements and ref references for Odoo 19 modules. Use when user wants to create a data XML file for loading initial data.
---


# Odoo 19 Data XML File Creation

This skill creates data XML files for loading initial data in Odoo 19 modules, including configuration records, security settings, and reference data.

## Overview

Data XML files in Odoo 19 are used to load essential data when a module is installed. Unlike demo files, these records are loaded every time the module is installed or updated (unless marked with `noupdate="1"`).

## Steps to Create Data XML File

### 1. **Determine File Location**

Data files should be placed in:
```
{module}/data/
```

For security files:
```
{module}/security/
```

### 2. **File Naming Convention**

Use descriptive names following this pattern:
- `data_{model_name}.xml` - General data for a model
- `security_{model_name}.xml` - Security/access control data
- `{feature}_data.xml` - Feature-specific data
- `ir_cron_data.xml` - Scheduled actions
- `sequence_data.xml` - Number sequences

### 3. **XML Structure**

Create the file with these essential elements:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Data records go here -->
    </data>
</odoo>
```

### 4. **Create Data Records**

For each record, use the `<record>` tag with:
- **id**: Unique identifier (external ID)
- **model**: Model name

#### Basic Record Structure

```xml
<record id="my_record_id" model="my.model">
    <field name="name">Record Name</field>
    <field name="code">CODE_001</field>
    <field name="active" eval="True"/>
</record>
```

### 5. **Field Value Types**

#### String Fields
```xml
<field name="name">My Record Name</field>
<field name="description">Detailed description text</field>
```

#### Numeric Fields
```xml
<field name="sequence" eval="10"/>
<field name="amount" eval="999.99"/>
<field name="quantity" eval="100"/>
```

#### Boolean Fields
```xml
<field name="active" eval="True"/>
<field name="is_default" eval="False"/>
```

#### Date/DateTime Fields
```xml
<field name="date_from">2024-01-01</field>
<field name="datetime_field">2024-01-01 10:00:00</field>
<field name="create_date" eval="time.strftime('%Y-%m-%d %H:%M:%S')"/>
```

#### Selection Fields
```xml
<field name="state">draft</field>
<field name="priority">1</field>
```

### 6. **Reference Other Records**

Using `ref` attribute to reference other records:

#### Many2one References
```xml
<record id="my_partner" model="res.partner">
    <field name="name">Test Partner</field>
    <field name="country_id" ref="base.us"/>
    <field name="parent_id" ref="base.main_partner"/>
</record>
```

#### Using Module Prefix
```xml
<field name="category_id" ref="product.product_category_all"/>
<field name="uom_id" ref="uom.product_uom_unit"/>
<field name="company_id" ref="base.main_company"/>
```

### 7. **Complex Field Types**

#### One2many Relations
```xml
<record id="order_1" model="sale.order">
    <field name="name">SO001</field>
    <field name="partner_id" ref="base.partner_demo"/>
    <field name="order_line" eval="[(6, 0, [
        ref('order_line_1'),
        ref('order_line_2')
    ])]"/>
</record>

<record id="order_line_1" model="sale.order.line">
    <field name="order_id" ref="order_1"/>
    <field name="product_id" ref="product.product_product_1"/>
    <field name="product_uom_qty" eval="10.0"/>
</record>
```

#### Many2many Relations
```xml
<record id="group_custom" model="res.groups">
    <field name="name">Custom Group</field>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    <field name="category_id" ref="base.module_category_extra"/>
</record>
```

#### Evaluation Expressions
```xml
<field name="code" eval="'PREFIX-%s' % str(record.id).zfill(5)"/>
<field name="total" eval="record.price * record.quantity"/>
<field name="date_end" eval="(DateTime.today() + timedelta(days=30)).strftime('%Y-%m-%d')"/>
```

## Common Data File Types

### 1. **Security Groups**

**File: `security/res_groups.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- User Group -->
        <record id="group_custom_user" model="res.groups">
            <field name="name">Custom User</field>
            <field name="category_id" ref="base.module_category_custom"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
            <field name="comment">Users with custom access rights</field>
        </record>

        <!-- Manager Group -->
        <record id="group_custom_manager" model="res.groups">
            <field name="name">Custom Manager</field>
            <field name="category_id" ref="base.module_category_custom"/>
            <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
            <field name="comment">Managers with full access</field>
        </record>

        <!-- Administrator Group -->
        <record id="group_custom_admin" model="res.groups">
            <field name="name">Custom Administrator</field>
            <field name="category_id" ref="base.module_category_custom"/>
            <field name="implied_ids" eval="[(4, ref('group_custom_manager'))]"/>
            <field name="comment">Administrators with system access</field>
            <field name="users" eval="[(4, ref('base.user_admin'))]"/>
        </record>
    </data>
</odoo>
```

### 2. **Access Rights (CSV Format)**

**File: `security/ir.model.access.csv`**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,group_custom_user,1,1,0,0
access_custom_model_manager,custom.model.manager,model_custom_model,group_custom_manager,1,1,1,0
access_custom_model_admin,custom.model.admin,model_custom_model,group_custom_admin,1,1,1,1
```

### 3. **Record Rules**

**File: `security/ir_rule.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- User Rule: See own records only -->
        <record id="custom_model_user_rule" model="ir.rule">
            <field name="name">Custom Model: User Own Records</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- Manager Rule: See all records -->
        <record id="custom_model_manager_rule" model="ir.rule">
            <field name="name">Custom Model: Manager All Records</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('group_custom_manager'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- Global Rule: Multi-company -->
        <record id="custom_model_company_rule" model="ir.rule">
            <field name="name">Custom Model: Multi-company</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
            <field name="global" eval="True"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>
    </data>
</odoo>
```

### 4. **Sequences**

**File: `data/ir_sequence_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Code Sequence -->
        <record id="sequence_custom_code" model="ir.sequence">
            <field name="name">Custom Code Sequence</field>
            <field name="code">custom.code</field>
            <field name="prefix">CC/%(year)s/</field>
            <field name="padding">5</field>
            <field name="number_next">1</field>
            <field name="number_increment">1</field>
            <field name="company_id" eval="False"/>
        </record>

        <!-- Reference Sequence with date range -->
        <record id="sequence_custom_ref" model="ir.sequence">
            <field name="name">Custom Reference Sequence</field>
            <field name="code">custom.reference</field>
            <field name="prefix">REF/%(range_year)s%(range_month)s/</field>
            <field name="padding">6</field>
            <field name="number_next">1</field>
            <field name="number_increment">1</field>
            <field name="use_date_range" eval="True"/>
            <field name="date_range_ids" eval="[(0, 0, {
                'date_from': time.strftime('%Y-%m-01'),
                'date_to': (DateTime.today() + relativedelta(months=1, day=1, days=-1)).strftime('%Y-%m-%d'),
                'number_next': 1
            })]"/>
        </record>
    </data>
</odoo>
```

### 5. **Menu Items**

**File: `data/ir_ui_menu_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Main Menu -->
        <record id="menu_custom_root" model="ir.ui.menu">
            <field name="name">Custom Module</field>
            <field name="sequence" eval="10"/>
            <field name="web_icon">custom_module,static/description/icon.png</field>
            <field name="parent_id" ref="base.menu_custom_root"/>
        </record>

        <!-- Sub Menu -->
        <record id="menu_custom_records" model="ir.ui.menu">
            <field name="name">Records</field>
            <field name="sequence" eval="1"/>
            <field name="action" ref="action_custom_records"/>
            <field name="parent_id" ref="menu_custom_root"/>
        </record>

        <!-- Configuration Menu -->
        <record id="menu_custom_config" model="ir.ui.menu">
            <field name="name">Configuration</field>
            <field name="sequence" eval="99"/>
            <field name="action" ref="action_custom_config"/>
            <field name="parent_id" ref="menu_custom_root"/>
            <field name="groups_id" eval="[(4, ref('group_custom_manager'))]"/>
        </record>
    </data>
</odoo>
```

### 6. **Actions**

**File: `data/ir_actions_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Window Action -->
        <record id="action_custom_records" model="ir.actions.act_window">
            <field name="name">Records</field>
            <field name="res_model">custom.model</field>
            <field name="view_mode">tree,form,kanban,calendar,pivot,graph</field>
            <field name="domain">[]</field>
            <field name="context">{}</field>
            <field name="search_view_id" ref="view_custom_search"/>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Create your first record!
                </p>
            </field>
        </record>

        <!-- Server Action -->
        <record id="action_custom_server" model="ir.actions.server">
            <field name="name">Custom Server Action</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="state">code</field>
            <field name="code">
for record in records:
    record.action_method()
            </field>
        </record>

        <!-- Client Action -->
        <record id="action_custom_client" model="ir.actions.client">
            <field name="name">Custom Client Action</field>
            <field name="tag">custom_module.action</field>
            <field name="params" eval="{'key': 'value'}"/>
        </record>

        <!-- URL Action -->
        <record id="action_custom_url" model="ir.actions.act_url">
            <field name="name">Documentation</field>
            <field name="url">https://www.odoo.com/documentation</field>
            <field name="target">new</field>
        </record>
    </data>
</odoo>
```

### 7. **Scheduled Actions (Cron)**

**File: `data/ir_cron_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Daily Cron Job -->
        <record id="cron_custom_daily" model="ir.cron">
            <field name="name">Daily Process</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="state">code</field>
            <field name="code">model.cron_daily_process()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="doall" eval="False"/>
            <field name="active" eval="True"/>
            <field name="user_id" ref="base.user_root"/>
            <field name="nextcall" eval="(DateTime.now() + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')"/>
        </record>

        <!-- Hourly Cron Job -->
        <record id="cron_custom_hourly" model="ir.cron">
            <field name="name">Hourly Sync</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="state">code</field>
            <field name="code">model.cron_hourly_sync()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">hours</field>
            <field name="numbercall">-1</field>
            <field name="doall" eval="False"/>
            <field name="active" eval="True"/>
        </record>

        <!-- Weekly Cron Job -->
        <record id="cron_custom_weekly" model="ir.cron">
            <field name="name">Weekly Report</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="state">code</field>
            <field name="code">model.cron_weekly_report()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">weeks</field>
            <field name="numbercall">-1</field>
            <field name="doall" eval="True"/>
            <field name="active" eval="True"/>
            <field name="day_of_week">0</field>
        </record>

        <!-- Monthly Cron Job -->
        <record id="cron_custom_monthly" model="ir.cron">
            <field name="name">Monthly Cleanup</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="state">code</field>
            <field name="code">model.cron_monthly_cleanup()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">months</field>
            <field name="numbercall">-1</field>
            <field name="doall" eval="False"/>
            <field name="active" eval="True"/>
            <field name="day">1</field>
        </record>
    </data>
</odoo>
```

### 8. **Email Templates**

**File: `data/mail_template_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Email Template -->
        <record id="email_template_custom" model="mail.template">
            <field name="name">Custom Template</field>
            <field name="model_id" ref="model_custom_model"/>
            <field name="subject">Custom Record: {{ object.name }}</field>
            <field name="email_from">{{ object.user_id.email_formatted or user.email_formatted }}</field>
            <field name="email_to">{{ object.partner_id.email }}</field>
            <field name="lang">{{ object.partner_id.lang }}</field>
            <field name="auto_delete" eval="True"/>
            <field name="body_html" type="html">
<div style="margin: 0px; padding: 0px;">
    <p>Hello ${object.partner_id.name},</p>
    <p>Your custom record <strong>${object.name}</strong> has been created.</p>
    <p>Details:</p>
    <ul>
        <li>Date: ${object.date}</li>
        <li>Amount: ${object.amount}</li>
        <li>State: ${object.state}</li>
    </ul>
    <p>Thank you for your business!</p>
</div>
            </field>
            <field name="report_template" ref="report_custom_pdf"/>
            <field name="report_name">{{ object.name.replace('/', '_') }}</field>
        </record>
    </data>
</odoo>
```

### 9. **Configuration Data**

**File: `data/res_config_settings_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Default Settings -->
        <record id="custom_config_settings" model="res.config.settings">
            <field name="custom_field_1">default_value_1</field>
            <field name="custom_field_2" eval="True"/>
            <field name="custom_field_3" eval="100"/>
        </record>

        <!-- System Parameters -->
        <record id="param_custom_1" model="ir.config_parameter">
            <field name="key">custom.param.name</field>
            <field name="value">param_value</field>
        </record>

        <record id="param_custom_api" model="ir.config_parameter">
            <field name="key">custom.api.endpoint</field>
            <field name="value">https://api.example.com</field>
        </record>
    </data>
</odoo>
```

## Module Manifest Integration

Update `__manifest__.py` to include data files:

```python
{
    'name': 'Your Module Name',
    'version': '19.0.1.0.0',
    'category': 'Category',
    'summary': 'Module description',
    'description': 'Long description',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        # Security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

        # Data
        'data/ir_sequence_data.xml',
        'data/ir_ui_menu_data.xml',
        'data/ir_actions_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'data/res_config_settings_data.xml',

        # Views
        'views/custom_views.xml',

        # Reports
        'reports/custom_reports.xml',
    ],
    'demo': [
        'demo/demo_custom.xml',
    ],
    'installable': True,
    'application': True,
}
```

## Best Practices

### 1. **Use External ID Prefixes**
```xml
<!-- Good -->
<record id="my_module_record_1" model="my.model">

<!-- Avoid -->
<record id="record_1" model="my.model">
```

### 2. **Reference Records Properly**
```xml
<!-- Use module prefix for cross-module references -->
<field name="category_id" ref="product.product_category_all"/>
<field name="company_id" ref="base.main_company"/>

<!-- Omit module prefix for same-module references -->
<field name="parent_id" ref="parent_record_id"/>
```

### 3. **Use noupdate Flags Wisely**
```xml
<!-- Always update (default) -->
<record id="config_data" model="config.model">

<!-- Never update after initial creation -->
<record id="static_data" model="static.model" noupdate="1">
```

### 4. **Organize Data Files**
- Security files in `security/` directory
- Configuration data in `data/` directory
- Separate files by feature/functionality

### 5. **Use Proper Field Types**
```xml
<!-- String -->
<field name="name">Value</field>

<!-- Integer -->
<field name="count" eval="10"/>

<!-- Float -->
<field name="amount" eval="99.99"/>

<!-- Boolean -->
<field name="active" eval="True"/>

<!-- Date -->
<field name="date">2024-01-01</field>

<!-- DateTime -->
<field name="datetime">2024-01-01 10:00:00</field>

<!-- Many2one -->
<field name="partner_id" ref="base.partner_demo"/>

<!-- One2many/Many2many -->
<field name="line_ids" eval="[(6, 0, [ref('line_1'), ref('line_2')])]"/>
```

### 6. **Add Comments**
```xml
<!-- User Group -->
<record id="group_user" model="res.groups">

<!-- Manager Group (inherits user rights) -->
<record id="group_manager" model="res.groups">
```

### 7. **Test Data Loading**
```bash
# Update module to load data
./odoo-bin -c odoo.conf -u your_module --stop-after-init

# Install with data
./odoo-bin -c odoo.conf -i your_module --stop-after-init
```

## Advanced Patterns

### Dynamic Values
```xml
<field name="name" eval="'Record %s' % str(record.id).zfill(5)"/>
<field name="date" eval="DateTime.now()"/>
<field name="total" eval="sum(line.price for line in record.line_ids)"/>
```

### Conditional Fields
```xml
<field name="code" eval="'PREFIX-%s' % str(record.id).zfill(5) if record.id else 'DRAFT'"/>
<field name="amount" eval="record.price * record.quantity"/>
```

### Search References
```xml
<field name="default_user" search="[('login', '=', 'admin')]" model="res.users"/>
```

### Update Existing Records
```xml
<record id="base.user_admin" model="res.users">
    <field name="signature">Administrator</field>
</record>
```

### Delete Records
```xml
<record id="unwanted_record" model="unwanted.model">
    <field name="id" eval="False"/>
</record>
```

## Usage Examples

### Example 1: Create Security Data
```bash
/data-xml module=my_module model=res.groups record_type=security
```

### Example 2: Create Menu Data
```bash
/data-xml module=my_module model=ir.ui.menu record_type=menu file_name=menu_data.xml
```

### Example 3: Create Cron Data
```bash
/data-xml module=my_module model=ir.cron record_type=automation
```

### Example 4: Create Configuration Data
```bash
/data-xml module=my_module model=res.config.settings file_name=config_data.xml
```

## Notes

- Data files are loaded every time the module is installed or updated (unless noupdate="1")
- Use `ref()` to reference records from other modules with module prefix
- CSV files for access rights must be in `security/` directory
- Test data loading before deployment
- Ensure all referenced records exist (add proper dependencies in manifest)
- Use external IDs for all records that may be referenced elsewhere
- Keep data files organized and well-documented
