---
description: Create a new Odoo 19 module with complete structure. Use when user wants to create a new custom Odoo module with models, views, security, and demo data.
---


Create a new Odoo 19 module with proper structure and conventions.

## Steps

1. **Parse module name** from user input:
   - Extract module name (e.g., "my_custom_module")
   - Parse optional flags: --category, --depends, --application, --author, --license, --version

2. **Ask for missing required information**:
   - Module name (if not provided)
   - Category: Sales, Purchase, Accounting, Inventory, Manufacturing, Project, Website, HR, Marketing, Warehouse, Base, Other, Uncategorized
   - Dependencies: comma-separated list (default: base)
   - Is it an application? (default: No)
   - Author name (default: User's name or company)
   - License (default: LGPL-3)
   - Version (default: 19.0.1.0.0)
   - Summary: Brief description of module functionality

3. **Verify module doesn't exist**:
   - Check if module folder already exists in the current Odoo addons path
   - If exists, ask to confirm overwrite or choose different name
   - Search in common locations: /addons/, /custom-addons/, /odoo/addons/, etc.

4. **Determine module path**:
   - Ask user where to create the module (default: current directory)
   - Full path should be: `{base_path}/{module_name}/`

5. **Create module structure**:
   ```
   {module_name}/
   ├── __init__.py
   ├── __manifest__.py
   ├── models/
   │   ├── __init__.py
   │   └── {module_name}.py
   ├── views/
   │   └── {module_name}_views.xml
   ├── security/
   │   ├── ir.model.access.csv
   │   └── {module_name}_security.xml
   ├── demo/
   │   └── {module_name}_demo.xml
   ├── data/
   │   └── {module_name}_data.xml
   ├── i18n/
   │   └── {module_name}.pot
   ├── static/
   │   └── src/
   │       ├── js/
   │       ├── scss/
   │       └── xml/
   ├── lib/
   │   └── .gitkeep
   ├── report/
   │   └── .gitkeep
   ├── tests/
   │   ├── __init__.py
   │   └── test_{module_name}.py
   └── README.md
   ```

6. **Generate __manifest__.py** following Odoo 19 conventions:
   ```python
   # -*- coding: utf-8 -*-
   {
       "name": "{Human Readable Module Name}",
       "summary": "{Brief summary of module functionality}",
       "description": """
           Long description.
           Multi-line if needed.
       """,
       "author": "{Author Name}",
       "website": "{Website URL}",
       "category": "{Category}",
       "version": "{version}",
       "license": "{license}",
       "depends": [
           "base",
           {additional_dependencies}
       ],
       "data": [
           "security/{module_name}_security.xml",
           "security/ir.model.access.csv",
           "views/{module_name}_views.xml",
       ],
       "demo": [
           "demo/{module_name}_demo.xml",
       ],
       "assets": {
           "web.assets_backend": [
               "{module_name}/static/src/js/*.js",
               "{module_name}/static/src/scss/*.scss",
           ],
           "web.assets_frontend": [
               "{module_name}/static/src/js/*.js",
               "{module_name}/static/src/scss/*.scss",
           ],
       },
       "images": [],
       "installable": True,
       "application": {is_app},
       "auto_install": False,
       "post_init_hook": None,
       "pre_init_hook": None,
       "uninstall_hook": None,
       "external_dependencies": {
           "python": [],
           "binary": [],
       },
       "css": [],
       "js": [],
       "qweb": [],
   }
   ```

7. **Create __init__.py**:
   ```python
   # -*- coding: utf-8 -*-

   from . import models
   ```

8. **Create models/__init__.py**:
   ```python
   # -*- coding: utf-8 -*-

   from . import {module_name}
   ```

9. **Create models/{module_name}.py** with base model:
   ```python
   # -*- coding: utf-8 -*-

   from odoo import models, fields, api


   class {ModelClassName}(models.Model):
       _name = '{module_name}.{model_name}'
       _description = '{Model Description}'

       name = fields.Char(string='Name', required=True)
       active = fields.Boolean(string='Active', default=True)

       # Add your fields here
   ```

10. **Create views/{module_name}_views.xml** with basic structure:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data>
            <!-- Tree View -->
            <record id="view_{module_name}_tree" model="ir.ui.view">
                <field name="name">{module_name}.tree</field>
                <field name="model">{module_name}.{model_name}</field>
                <field name="arch" type="xml">
                    <tree string="{Model Name}">
                        <field name="name"/>
                        <field name="active"/>
                    </tree>
                </field>
            </record>

            <!-- Form View -->
            <record id="view_{module_name}_form" model="ir.ui.view">
                <field name="name">{module_name}.form</field>
                <field name="model">{module_name}.{model_name}</field>
                <field name="arch" type="xml">
                    <form string="{Model Name}">
                        <sheet>
                            <group>
                                <field name="name"/>
                                <field name="active"/>
                            </group>
                        </sheet>
                    </form>
                </field>
            </record>

            <!-- Action -->
            <record id="action_{module_name}" model="ir.actions.act_window">
                <field name="name">{Model Name}</field>
                <field name="res_model">{module_name}.{model_name}</field>
                <field name="view_mode">tree,form</field>
                <field name="help" type="html">
                    <p class="o_view_nocontent_smiling_face">
                        Create your first {model_name}
                    </p>
                </field>
            </record>

            <!-- Menu Item -->
            <menuitem id="menu_{module_name}"
                      name="{Model Name}"
                      action="action_{module_name}"
                      sequence="10"/>
        </data>
    </odoo>
    ```

11. **Create security/ir.model.access.csv** with header:
    ```csv
    id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
    access_{module_name}_{model_name}_user,{module_name}_{model_name}_user,model_{module_name}_{model_name},base.group_user,1,0,0,0
    ```

12. **Create security/{module_name}_security.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data noupdate="1">
            <!-- Security Groups -->
            <record id="group_{module_name}_user" model="res.groups">
                <field name="name">{Module Name} User</field>
                <field name="category_id" ref="base.module_category_{category_lower}"/>
                <field name="comment">Users with access to {module_name}</field>
            </record>

            <record id="group_{module_name}_manager" model="res.groups">
                <field name="name">{Module Name} Manager</field>
                <field name="category_id" ref="base.module_category_{category_lower}"/>
                <field name="implied_ids" eval="[(4, ref('group_{module_name}_user'))]"/>
                <field name="comment">Managers with full access to {module_name}</field>
            </record>
        </data>
    </odoo>
    ```

13. **Create demo/{module_name}_demo.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data noupdate="1">
            <!-- Demo Data -->
            <record id="{module_name}_demo_1" model="{module_name}.{model_name}">
                <field name="name">Demo Record 1</field>
                <field name="active">True</field>
            </record>
        </data>
    </odoo>
    ```

14. **Create i18n/{module_name}.pot** with template:
    ```pot
    # Translation of Odoo Server.
    # This file contains the translation of the following modules:
    #	* {module_name}
    #
    msgid ""
    msgstr ""
    "Project-Id-Version: Odoo Server 19.0\n"
    "Report-Msgid-Bugs-To: \n"
    "POT-Creation-Date: {date}\n"
    "PO-Revision-Date: {date}\n"
    "Last-Translator: \n"
    "Language-Team: \n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n"
    "Plural-Forms: \n"

    #. module: {module_name}
    #: model:ir.model.fields,field_description:{module_name}.field_{module_name}_{model_name}_name
    msgid "Name"
    msgstr ""
    ```

15. **Create static/src/js/{module_name}.js**:
    ```javascript
    odoo.define('{module_name}.{module_name}', function (require) {
        "use strict";

        var core = require('web.core');
        var Widget = require('web.Widget');

        var {ModuleClassName} = Widget.extend({
            template: '{ModuleClassName}Template',

            init: function (parent, options) {
                this._super.apply(this, arguments);
                // Your initialization code
            },

            start: function () {
                var self = this;
                return this._super().then(function () {
                    // Your startup code
                });
            },
        });

        core.action_registry.add('{module_name}_action', {ModuleClassName});

        return {ModuleClassName};
    });
    ```

16. **Create static/src/scss/{module_name}.scss**:
    ```scss
    // {Module Name} styles
    .o_{module_name} {
        // Your styles here
    }
    ```

17. **Create tests/test_{module_name}.py**:
    ```python
    # -*- coding: utf-8 -*-

    from odoo.tests import TransactionCase


    class Test{ModelClassName}(TransactionCase):
        def setUp(self):
            super(Test{ModelClassName}, self).setUp()
            # Setup test data

        def test_{model_name}_creation(self):
            """Test creating a {model_name}"""
            record = self.env['{module_name}.{model_name}'].create({
                'name': 'Test Record',
            })
            self.assertTrue(record.id)
            self.assertEqual(record.name, 'Test Record')
    ```

18. **Create README.md**:
    ```markdown
    # {Module Name}

    {Brief description}

    ## Features

    - Feature 1
    - Feature 2
    - Feature 3

    ## Installation

    1. Copy the module to your Odoo addons directory
    2. Update your apps list
    3. Install the module from Apps menu

    ## Configuration

    Configuration instructions here

    ## Usage

    Usage instructions here

    ## Bug Tracker

    Bugs are tracked on [GitHub Issues](https://github.com/your/repo/issues).

    ## Credits

    * Author: {Author}
    * Contributors: {Contributors}

    ## Maintainer

    {Maintainer}
    ```

19. **Create .gitkeep files**:
    - `lib/.gitkeep`
    - `report/.gitkeep`

20. **Show summary** with:
    - Module path
    - Dependencies
    - Next steps:
      * Update module list in Odoo
      * Install module
      * Add models/views
      * Translate the module
      * Add security rules
      * Write tests

21. **Offer to create**:
    - Initial model with specific fields
    - Security rules
    - Menu items
    - Reports

## Example Usage

```
/module-new my_custom_module --category="Sales" --depends="sale,sale_management" --application
/module-new project_extension --category="Project" --depends="project" --author="My Company" --version="19.0.1.0.1"
```

## Important Notes

- **Odoo 19 version**: Always use version "19.0.x.y.z" format
- **Module naming**: Use snake_case for technical names
- **License**: Common licenses are LGPL-3, OPL-1, OEEL-1
- **Dependencies**: Always include "base" as minimum dependency
- **Python encoding**: Always include `# -*- coding: utf-8 -*-` at top of Python files
- **Model naming**: Use `{module_name}.{model_name}` format for _name
- **XML format**: Always use UTF-8 encoding in XML declaration
- **Security**: Always set up proper access rights and security groups
- **Testing**: Include basic test structure for quality assurance
- **i18n**: Include .pot file for translations
- **Assets**: Properly organize static files in assets section
- **Hooks**: Use post_init_hook, pre_init_hook, uninstall_hook when needed
- **External dependencies**: Specify any external Python or binary dependencies
- **Git tracking**: Create .gitkeep for empty directories to be tracked

## Odoo 19 Specific Changes

- New module categories available
- Enhanced security framework
- Updated ORM features
- Improved web assets management
- Better testing framework
- Enhanced reporting capabilities
