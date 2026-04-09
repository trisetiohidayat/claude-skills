---
description: Create Odoo 19 addon module structure with controllers, static, lib, wizard directories. Use when user wants to create a new Odoo addon module with advanced features.
---


You are helping the user create a new Odoo 19 addon module with advanced features including controllers, web assets, wizards, and external library support.

## Steps

1. **Parse module name** from user input:
   - Extract module name (e.g., "my_addon_module")
   - Parse optional flags:
     - --category: Module category
     - --depends: Comma-separated dependencies
     - --application: Is it an application?
     - --has-controllers: Include HTTP controllers
     - --has-wizards: Include transient model wizards
     - --has-website: Include website front-end components
     - --has-lib: Include external libraries
     - --has-api: Include REST API endpoints
     - --author: Module author
     - --version: Module version

2. **Ask for missing required information**:
   - Module name (if not provided)
   - Category (default: Uncategorized)
   - Dependencies (default: base, web)
   - Which components to include:
     * Controllers? (for HTTP routes)
     * Wizards? (for transient models)
     * Website? (for front-end)
     * API? (for REST endpoints)
     * External libraries? (for third-party code)
   - Summary: Brief description

3. **Verify module doesn't exist**:
   - Check if module folder exists
   - Confirm overwrite if needed

4. **Determine module path**:
   - Ask user for location (default: current directory)
   - Full path: `{base_path}/{module_name}/`

5. **Create comprehensive addon structure**:
   ```
   {module_name}/
   ├── __init__.py
   ├── __manifest__.py
   ├── models/
   │   ├── __init__.py
   │   ├── {module_name}.py
   │   └── {module_name}_mixins.py
   ├── controllers/
   │   ├── __init__.py
   │   ├── main.py
   │   └── api.py
   ├── views/
   │   ├── {module_name}_views.xml
   │   ├── {module_name}_templates.xml
   │   └── assets.xml
   ├── security/
   │   ├── ir.model.access.csv
   │   ├── {module_name}_security.xml
   │   └── {module_name}_ir_rule.xml
   ├── demo/
   │   └── {module_name}_demo.xml
   ├── data/
   │   └── {module_name}_data.xml
   ├── wizard/
   │   ├── __init__.py
   │   ├── {module_name}_wizard.py
   │   └── {module_name}_wizard_views.xml
   ├── lib/
   │   └── .gitkeep
   ├── static/
   │   ├── src/
   │   │   ├── js/
   │   │   │   ├── widgets/
   │   │   │   ├── views/
   │   │   │   └── {module_name}.js
   │   │   ├── scss/
   │   │   │   ├── {module_name}.scss
   │   │   │   └── views/
   │   │   ├── css/
   │   │   ├── xml/
   │   │   └── img/
   │   └── description/
   │       ├── icon.png
   │       └── index.html
   ├── report/
   │   ├── __init__.py
   │   ├── {module_name}_report.xml
   │   └── reports/
   │       └── {module_name}_report.py
   ├── i18n/
   │   └── {module_name}.pot
   ├── tests/
   │   ├── __init__.py
   │   ├── test_{module_name}.py
   │   └── test_controller.py
   ├── api/
   │   ├── __init__.py
   │   └── endpoints.py
   ├── scripts/
   │   └── .gitkeep
   ├── models/
   ├── README.md
   ├── __init__.py
   └── __manifest__.py
   ```

6. **Generate __manifest__.py** for addon:
   ```python
   # -*- coding: utf-8 -*-
   {
       "name": "{Human Readable Addon Name}",
       "summary": "{Brief summary of addon functionality}",
       "description": """
           Long description of the addon.
           Can be multi-line.
       """,
       "author": "{Author Name}",
       "website": "{Website URL}",
       "category": "{Category}",
       "version": "{version}",
       "license": "LGPL-3",

       # Dependencies
       "depends": [
           "base",
           "web",
           {additional_dependencies}
       ],

       # Data files
       "data": [
           "security/{module_name}_security.xml",
           "security/ir.model.access.csv",
           "security/{module_name}_ir_rule.xml",
           "views/{module_name}_views.xml",
           "views/{module_name}_templates.xml",
           "views/assets.xml",
           "wizard/{module_name}_wizard_views.xml",
           {report_files}
       ],

       # Demo files
       "demo": [
           "demo/{module_name}_demo.xml",
       ],

       # Web assets
       "assets": {
           "web.assets_backend": [
               "{module_name}/static/src/js/{module_name}.js",
               "{module_name}/static/src/scss/{module_name}.scss",
               "{module_name}/static/src/xml/*.xml",
           ],
           "web.assets_frontend": [
               "{module_name}/static/src/js/{module_name}.js",
               "{module_name}/static/src/scss/{module_name}.scss",
           ],
           "web.qweb_suite_tests": [
               "{module_name}/static/tests/**/*.js",
           ],
       },

       # QWeb templates
       "qweb": [
           "static/src/xml/*.xml",
       ],

       # Images
       "images": ["static/description/icon.png"],

       # Install settings
       "installable": True,
       "application": {is_app},
       "auto_install": False,

       # Hooks
       "post_init_hook": "post_init_hook",
       "pre_init_hook": None,
       "uninstall_hook": "uninstall_hook",

       # External dependencies
       "external_dependencies": {
           "python": [
               # "requests>=2.25.0",
               # "python-dateutil",
           ],
           "binary": [
               # "libreoffice",
               # "pdftk",
           ],
       },

       # CSS/JS shortcuts
       "css": [],
       "js": [],
   }
   ```

7. **Create __init__.py** with hooks:
   ```python
   # -*- coding: utf-8 -*-

   from . import models
   from . import controllers
   from . import wizard
   from . import report
   from . import api

   def post_init_hook(env):
       """Post-installation hook"""
       # Your post-installation logic
       pass

   def uninstall_hook(env):
       """Uninstallation hook"""
       # Your cleanup logic
       pass
   ```

8. **Create models/__init__.py**:
   ```python
   # -*- coding: utf-8 -*-

   from . import {module_name}
   from . import {module_name}_mixins
   ```

9. **Create models/{module_name}.py**:
   ```python
   # -*- coding: utf-8 -*-

   from odoo import models, fields, api, _
   from odoo.exceptions import ValidationError


   class {ModelClassName}(models.Model):
       _name = '{module_name}.{model_name}'
       _description = '{Model Description}'
       _inherit = ['mail.thread', 'mail.activity.mixin']

       name = fields.Char(string='Name', required=True, tracking=True)
       active = fields.Boolean(string='Active', default=True)
       description = fields.Text(string='Description')
       notes = fields.Html(string='Notes')

       # Relations
       company_id = fields.Many2one(
           'res.company',
          string='Company',
          default=lambda self: self.env.company,
      )
      user_id = fields.Many2one(
          'res.users',
          string='Responsible',
          default=lambda self: self.env.user,
          tracking=True,
      )

      # Computed fields
      display_name = fields.Char(compute='_compute_display_name', store=True)

      @api.depends('name')
      def _compute_display_name(self):
          for record in self:
              record.display_name = record.name

      # Constraints
      @api.constrains('name')
      def _check_name(self):
          for record in self:
              if not record.name or len(record.name.strip()) < 3:
                  raise ValidationError(_('Name must be at least 3 characters long.'))

      # Actions
      def action_activate(self):
          self.write({'active': True})

      def action_deactivate(self):
          self.write({'active': False})
  ```

10. **Create models/{module_name}_mixins.py**:
    ```python
    # -*- coding: utf-8 -*-

    from odoo import models, fields, api


    class {ModelName}Mixin(models.AbstractModel):
        _name = '{module_name}.mixin'
        _description = '{Module Name} Mixin'

        # Common fields shared across models
        ref = fields.Char(string='Reference', copy=False)
        date = fields.Date(string='Date', default=fields.Date.context_today)

        # Common methods
        def generate_ref(self):
            self.ensure_one()
            # Your reference generation logic
            pass
    ```

11. **Create controllers/main.py** (if has-controllers):
    ```python
    # -*- coding: utf-8 -*-

    from odoo import http
    from odoo.http import request


    class {ControllerName}Controller(http.Controller):

        @http.route(['/{module_name}', '/{module_name}/page/<int:page>'], type='http', auth="public", website=True)
        def index(self, page=1, **kwargs):
            # Your controller logic
            return request.render('{module_name}.index_template', {
                'page': page,
            })

        @http.route(['/{module_name}/detail/<model("{module_name}.{model_name}"):obj>'], type='http', auth="public", website=True)
        def detail(self, obj, **kwargs):
            return request.render('{module_name}.detail_template', {
                'object': obj,
            })

        @http.route('/{module_name}/json', type='json', auth="user", methods=['POST'], csrf=True)
        def json_endpoint(self, **kwargs):
            # Your JSON API logic
            return {
                'result': 'success',
                'data': kwargs,
            }
    ```

12. **Create controllers/api.py** (if has-api):
    ```python
    # -*- coding: utf-8 -*-

    import json
    from odoo import http
    from odoo.http import request
    from odoo.exceptions import AccessDenied, ValidationError


    class {ModuleApiName}Api(http.Controller):

        @http.route('/api/{module_name}/list', type='json', auth="user", methods=['GET'], csrf=False)
        def get_list(self, domain=None, fields=None, limit=80, offset=0):
            """REST API endpoint to list records"""
            if not request.env.user.has_group('{module_name}.group_{module_name}_user'):
                raise AccessDenied(_("You don't have access to this resource"))

            Model = request.env['{module_name}.{model_name}']
            records = Model.search(domain or [], limit=limit, offset=offset)

            return {
                'status': 'success',
                'count': len(records),
                'data': records.read(fields) if fields else records.read(),
            }

        @http.route('/api/{module_name}/create', type='json', auth="user", methods=['POST'], csrf=False)
        def create_record(self, **kwargs):
            """REST API endpoint to create record"""
            if not request.env.user.has_group('{module_name}.group_{module_name}_user'):
                raise AccessDenied(_("You don't have access to this resource"))

            try:
                record = request.env['{module_name}.{model_name}'].create(kwargs)
                return {
                    'status': 'success',
                    'id': record.id,
                    'data': record.read(),
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': str(e),
                }

        @http.route('/api/{module_name}/update/<int:record_id>', type='json', auth="user", methods=['PUT'], csrf=False)
        def update_record(self, record_id, **kwargs):
            """REST API endpoint to update record"""
            if not request.env.user.has_group('{module_name}.group_{module_name}_user'):
                raise AccessDenied(_("You don't have access to this resource"))

            record = request.env['{module_name}.{model_name}'].browse(record_id)
            if not record.exists():
                return {
                    'status': 'error',
                    'message': 'Record not found',
                }

            try:
                record.write(kwargs)
                return {
                    'status': 'success',
                    'data': record.read(),
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': str(e),
                }
    ```

13. **Create controllers/__init__.py**:
    ```python
    # -*- coding: utf-8 -*-

    from . import main
    from . import api
    ```

14. **Create wizard/__init__.py** (if has-wizards):
    ```python
    # -*- coding: utf-8 -*-

    from . import {module_name}_wizard
    ```

15. **Create wizard/{module_name}_wizard.py**:
    ```python
    # -*- coding: utf-8 -*-

    from odoo import models, fields, api, _
    from odoo.exceptions import UserError


    class {WizardName}Wizard(models.TransientModel):
        _name = '{module_name}.wizard'
        _description = '{Wizard Description}'

        # Transient model fields
        name = fields.Char(string='Name', required=True)
        date_from = fields.Date(string='From Date', required=True, default=fields.Date.context_today)
        date_to = fields.Date(string='To Date', required=True, default=fields.Date.context_today)
        options = fields.Selection([
            ('option1', 'Option 1'),
            ('option2', 'Option 2'),
        ], string='Options', default='option1')
        notes = fields.Text(string='Notes')

        # Relations
        record_ids = fields.Many2many(
            '{module_name}.{model_name}',
            string='{ModelName} Records',
        )

        def action_confirm(self):
            """Execute wizard action"""
            self.ensure_one()
            # Your wizard logic here
            return {'type': 'ir.actions.act_window_close'}

        def action_process(self):
            """Process selected records"""
            records = self.record_ids
            # Your processing logic
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Processed %d records') % len(records),
                    'type': 'success',
                }
            }
    ```

16. **Create wizard/{module_name}_wizard_views.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data>
            <!-- Wizard Form View -->
            <record id="view_{module_name}_wizard_form" model="ir.ui.view">
                <field name="name">{module_name}.wizard.form</field>
                <field name="model">{module_name}.wizard</field>
                <field name="arch" type="xml">
                    <form string="{Wizard Name}">
                        <group>
                            <field name="name"/>
                            <field name="date_from"/>
                            <field name="date_to"/>
                            <field name="options"/>
                        </group>
                        <group>
                            <field name="notes"/>
                            <field name="record_ids" widget="many2many_tags"/>
                        </group>
                        <footer>
                            <button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
                            <button name="action_process" string="Process" type="object" class="btn-primary"/>
                            <button string="Cancel" class="btn-secondary" special="cancel"/>
                        </footer>
                    </form>
                </field>
            </record>

            <!-- Wizard Action -->
            <record id="action_{module_name}_wizard" model="ir.actions.act_window">
                <field name="name">{Wizard Name}</field>
                <field name="res_model">{module_name}.wizard</field>
                <field name="view_mode">form</field>
                <field name="target">new</field>
            </record>
        </data>
    </odoo>
    ```

17. **Create views/{module_name}_views.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data>
            <!-- Tree View -->
            <record id="view_{module_name}_tree" model="ir.ui.view">
                <field name="name">{module_name}.tree</field>
                <field name="model">{module_name}.{model_name}</field>
                <field name="arch" type="xml">
                    <tree string="{Model Name}" default_order="name">
                        <field name="name"/>
                        <field name="user_id"/>
                        <field name="company_id"/>
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
                        <header>
                            <button name="action_activate" string="Activate" type="object" class="btn-primary" attrs="{'invisible': [('active', '=', True)]}"/>
                            <button name="action_deactivate" string="Deactivate" type="object" class="btn-secondary" attrs="{'invisible': [('active', '=', False)]}"/>
                        </header>
                        <sheet>
                            <div class="oe_button_box" name="button_box">
                                <!-- Button box widgets -->
                            </div>
                            <group>
                                <group>
                                    <field name="name" widget="text"/>
                                    <field name="user_id"/>
                                </group>
                                <group>
                                    <field name="company_id"/>
                                    <field name="active"/>
                                </group>
                            </group>
                            <notebook>
                                <page string="Description">
                                    <field name="description"/>
                                </page>
                                <page string="Notes">
                                    <field name="notes"/>
                                </page>
                            </notebook>
                        </sheet>
                        <div class="oe_chatter">
                            <field name="message_follower_ids"/>
                            <field name="activity_ids"/>
                            <field name="message_ids"/>
                        </div>
                    </form>
                </field>
            </record>

            <!-- Search View -->
            <record id="view_{module_name}_search" model="ir.ui.view">
                <field name="name">{module_name}.search</field>
                <field name="model">{module_name}.{model_name}</field>
                <field name="arch" type="xml">
                    <search string="{Model Name}">
                        <field name="name" string="Name"/>
                        <field name="user_id"/>
                        <field name="company_id"/>
                        <filter string="Active" name="active" domain="[('active', '=', True)]"/>
                        <filter string="Inactive" name="inactive" domain="[('active', '=', False)]"/>
                        <separator/>
                        <group expand="0" string="Group By">
                            <filter string="User" name="user_id" context="{'group_by': 'user_id'}"/>
                            <filter string="Company" name="company_id" context="{'group_by': 'company_id'}"/>
                        </group>
                    </search>
                </field>
            </record>

            <!-- Action -->
            <record id="action_{module_name}" model="ir.actions.act_window">
                <field name="name">{Model Name}</field>
                <field name="res_model">{module_name}.{model_name}</field>
                <field name="view_mode">tree,form</field>
                <field name="domain">[]</field>
                <field name="context">{}</field>
                <field name="help" type="html">
                    <p class="o_view_nocontent_smiling_face">
                        Create your first {model_name}
                    </p>
                </field>
            </record>

            <!-- Menu Item -->
            <menuitem id="menu_{module_name}_root"
                      name="{Module Name}"
                      sequence="10"
                      web_icon="{module_name},static/description/icon.png"/>
            <menuitem id="menu_{module_name}"
                      name="{Model Name}"
                      parent="menu_{module_name}_root"
                      action="action_{module_name}"
                      sequence="10"/>
        </data>
    </odoo>
    ```

18. **Create views/{module_name}_templates.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <template id="index_template" name="{Module Name} Index">
            <t t-call="website.layout">
                <div id="wrap" class="oe_structure oe_empty">
                    <section class="container">
                        <h1>{Module Name}</h1>
                        <p>Welcome to {module_name}</p>
                    </section>
                </div>
            </t>
        </template>

        <template id="detail_template" name="{Module Name} Detail">
            <t t-call="website.layout">
                <div id="wrap" class="oe_structure">
                    <section class="container">
                        <h1 t-field="object.name"/>
                        <div t-field="object.description"/>
                    </section>
                </div>
            </t>
        </template>
    </odoo>
    ```

19. **Create views/assets.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <template id="assets_backend" inherit_id="web.assets_backend" name="{Module Name} Backend Assets">
            <xpath expr="." position="inside">
                <script type="text/javascript" src="/{module_name}/static/src/js/{module_name}.js"/>
                <link rel="stylesheet" type="text/scss" href="/{module_name}/static/src/scss/{module_name}.scss"/>
            </xpath>
        </template>

        <template id="assets_frontend" inherit_id="web.assets_frontend" name="{Module Name} Frontend Assets">
            <xpath expr="." position="inside">
                <script type="text/javascript" src="/{module_name}/static/src/js/{module_name}.js"/>
                <link rel="stylesheet" type="text/scss" href="/{module_name}/static/src/scss/{module_name}.scss"/>
            </xpath>
        </template>
    </odoo>
    ```

20. **Create static/src/js/{module_name}.js**:
    ```javascript
    odoo.define('{module_name}.{module_name}', function (require) {
        "use strict";

        var core = require('web.core');
        var Widget = require('web.Widget');
        var web_client = require('web.web_client');

        var {ModuleClassName} = Widget.extend({
            template: '{ModuleClassName}Template',

            events: {
                'click .o_button_example': '_onButtonClick',
            },

            init: function (parent, options) {
                this._super.apply(this, arguments);
                this.options = options || {};
            },

            start: function () {
                var self = this;
                return this._super().then(function () {
                    // Your startup code
                });
            },

            _onButtonClick: function (e) {
                e.preventDefault();
                // Your button click handler
            },
        });

        // Register widget
        core.action_registry.add('{module_name}_action', {ModuleClassName});

        return {ModuleClassName};
    });
    ```

21. **Create static/src/scss/{module_name}.scss**:
    ```scss
    // {Module Name} styles
    .o_{module_name} {
        // Main styles

        &.button {
            // Button styles
        }
    }

    // Custom widget styles
    .o_widget_{module_name}_example {
        padding: 16px;
        background-color: #f8f9fa;
        border-radius: 4px;

        .example-title {
            font-size: 16px;
            font-weight: bold;
        }
    }
    ```

22. **Create api/endpoints.py** (if has-api):
    ```python
    # -*- coding: utf-8 -*-

    from odoo import models
    from odoo.exceptions import ValidationError


    class {ModuleApiName}Endpoint(models.AbstractModel):
        _name = '{module_name}.endpoint'
        _description = '{Module Name} API Endpoints'

        # Additional API helper methods
        @api.model
        def get_records(self, domain=None, fields=None):
            """Get records with optional domain and fields"""
            return self.search(domain or []).read(fields or [])

        @api.model
        def create_record(self, vals):
            """Create a new record"""
            return self.create(vals)
    ```

23. **Create api/__init__.py**:
    ```python
    # -*- coding: utf-8 -*-

    from . import endpoints
    ```

24. **Create report/reports/{module_name}_report.py**:
    ```python
    # -*- coding: utf-8 -*-

    from odoo import models, api


    class {ReportName}Report(models.AbstractModel):
        _name = 'report.{module_name}.{module_name}_report_template'
        _description = '{Report Name} Report'

        @api.model
        def _get_report_values(self, docids, data=None):
            """Get report values"""
            docs = self.env['{module_name}.{model_name}'].browse(docids)
            return {
                'doc_ids': docids,
                'doc_model': '{module_name}.{model_name}',
                'docs': docs,
                'data': data,
            }
    ```

25. **Create report/{module_name}_report.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data>
            <report
                id="{module_name}_report"
                model="{module_name}.{model_name}"
                string="{Report Name}"
                report_type="qweb-pdf"
                name="{module_name}.{module_name}_report_template"
                file="{module_name}_report"
                print_report_name="'{Report Name} - %s' % (object.name or '')"
                binding_model_id="{module_name}.{model_name}"
                binding_type="report"/>

            <template id="{module_name}_report_template">
                <t t-call="web.html_container">
                    <t t-foreach="docs" t-as="o">
                        <t t-call="web.external_layout">
                            <div class="page">
                                <h2>{Report Name}</h2>
                                <div t-field="o.name"/>
                                <!-- Add more report content -->
                            </div>
                        </t>
                    </t>
                </t>
            </template>
        </data>
    </odoo>
    ```

26. **Create security/{module_name}_ir_rule.xml**:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data noupdate="1">
            <!-- Record Rules -->
            <record id="{module_name}_{model_name}_rule_user" model="ir.rule">
                <field name="name">{ModelName}: User: See own records only</field>
                <field name="model_id" ref="model_{module_name}_{model_name}"/>
                <field name="domain_force">[('user_id', '=', user.id)]</field>
                <field name="groups" eval="[(4, ref('{module_name}.group_{module_name}_user'))]"/>
                <field name="perm_read" eval="True"/>
                <field name="perm_write" eval="True"/>
                <field name="perm_create" eval="True"/>
                <field name="perm_unlink" eval="False"/>
            </record>

            <record id="{module_name}_{model_name}_rule_manager" model="ir.rule">
                <field name="name">{ModelName}: Manager: See all records</field>
                <field name="model_id" ref="model_{module_name}_{model_name}"/>
                <field name="domain_force">[(1, '=', 1)]</field>
                <field name="groups" eval="[(4, ref('{module_name}.group_{module_name}_manager'))]"/>
                <field name="perm_read" eval="True"/>
                <field name="perm_write" eval="True"/>
                <field name="perm_create" eval="True"/>
                <field name="perm_unlink" eval="True"/>
            </record>
        </data>
    </odoo>
    ```

27. **Create tests/test_{module_name}.py**:
    ```python
    # -*- coding: utf-8 -*-

    from odoo.tests import TransactionCase
    from odoo.exceptions import ValidationError


    class Test{ModelClassName}(TransactionCase):
        def setUp(self):
            super(Test{ModelClassName}, self).setUp()
            self.Model = self.env['{module_name}.{model_name}']

        def test_create_{model_name}(self):
            """Test creating a {model_name}"""
            record = self.Model.create({
                'name': 'Test Record',
            })
            self.assertTrue(record.id)
            self.assertEqual(record.name, 'Test Record')

        def test_name_constraint(self):
            """Test name constraint"""
            with self.assertRaises(ValidationError):
                self.Model.create({'name': 'AB'})

        def test_action_activate(self):
            """Test activate action"""
            record = self.Model.create({'name': 'Test', 'active': False})
            record.action_activate()
            self.assertTrue(record.active)
    ```

28. **Create static/description/index.html**:
    ```html
    <section class="oe_container">
        <div class="oe_row oe_spaced">
            <div class="oe_span12">
                <h2 class="oe_slogan">{Module Name}</h2>
                <h3 class="oe_slogan">{Brief Description}</h3>
            </div>
        </div>
    </section>

    <section class="oe_container">
        <div class="oe_row oe_spaced">
            <div class="oe_span6">
                <h3 class="oe_slogan">Key Features</h3>
                <ul class="oe_unstyled">
                    <li>Feature 1</li>
                    <li>Feature 2</li>
                    <li>Feature 3</li>
                </ul>
            </div>
        </div>
    </section>
    ```

29. **Show summary** with:
    - Module path
    - All components created
    - Next steps:
      * Update module list
      * Install module
      * Configure security
      * Add translations
      * Run tests
      * Set up controllers/routes
      * Configure API endpoints
      * Add reports

## Example Usage

```
/module-addon my_addon --category="Website" --depends="website,website_sale" --has-controllers --has-wizards --has-website
/module-addon api_integration --category="Sales" --depends="sale,sale_management" --has-controllers --has-api --has-lib
/module-addon advanced_module --category="Project" --application --has-wizards --has-api
```

## Important Notes

- **Addons vs Regular Modules**: Addons include additional directories for controllers, wizards, API, lib, and advanced features
- **Controllers**: HTTP routes for web interface
- **Wizards**: Transient models for user interactions
- **API**: REST endpoints for external integrations
- **Lib**: External libraries and third-party code
- **Static**: Organized into js, scss, css, xml, img, description
- **Reports**: QWeb reports for PDF generation
- **Tests**: Both model and controller tests
- **Security**: Comprehensive ACL and record rules
- **i18n**: Translation templates
- **Assets**: Properly organized web assets

## Odoo 19 Addon Specific Features

- Enhanced controller routing with type='http' and type='json'
- Improved wizard framework with transient models
- Advanced API endpoint support
- Better security rule management
- Enhanced reporting capabilities
- Improved static asset management
- Better test framework support
- Advanced mixin support for model extensibility
