---
description: Create web.assets.xml or web.assets_backend.xml with proper JS/CSS bundles. Use when user wants to add web assets to a module.
---


# Odoo 19 Web Assets Configuration

Create web.assets.xml or web.assets_backend.xml with proper JS/CSS bundles, file references, and asset loading order following Odoo 19 conventions.

## Instructions

1. **Determine the file location:**
   - Assets file should be: `{module_name}/views/assets.xml`
   - Use consistent naming: `assets.xml` or `web_assets.xml`

2. **Generate the assets XML structure:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Asset bundle definitions -->
    </data>
</odoo>
```

3. **Asset bundle types:**
   - `web.assets_backend` - Backend (admin) interface assets
   - `web.assets_frontend` - Frontend (website) assets
   - `web.assets_common` - Common/shared assets
   - `web.assets_tests` - Test assets
   - `web.assets_editor` - Editor assets
   - `web.assets_dashboard` - Dashboard assets
   - `web.report.assets` - Report/QWeb assets

4. **File type extensions:**
   - `.js` - JavaScript files (ES6 modules)
   - `.css` - CSS stylesheets
   - `.scss` - SASS/SCSS stylesheets
   - `.xml` - QWeb template files

5. **Add files to bundles:**

```xml
<template id="module_name.assets_backend"
          name="Module Name Backend Assets"
          inherit_id="web.assets_backend"
          active="True">

    <!-- JavaScript files -->
    <xpath expr="." position="inside">
        <script type="text/javascript"
                src="/module_name/static/src/js/file1.js"/>
        <script type="text/javascript"
                src="/module_name/static/src/js/file2.js"/>
    </xpath>

    <!-- CSS files -->
    <xpath expr="." position="inside">
        <link rel="stylesheet"
              type="text/scss"
              href="/module_name/static/src/scss/file1.scss"/>
        <link rel="stylesheet"
              type="text/css"
              href="/module_name/static/src/css/file2.css"/>
    </xpath>

</template>
```

6. **Specify file order:**
   - Dependencies first (libraries, frameworks)
   - Core files (utilities, base classes)
   - Feature files (widgets, components)
   - Init files (registrations, setup)

7. **Add to __manifest__.py:**
   - Include assets.xml in data list
   - Format: `'views/assets.xml'`

## Usage Examples

### Basic Backend Assets

```bash
/web-assets library_book backend "static/src/js/widgets.js,static/src/css/widgets.css"
```

Output:
```xml
<!-- library_book/views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="assets_backend"
                  name="Library Book Backend Assets"
                  inherit_id="web.assets_backend">

            <!-- JavaScript files -->
            <xpath expr="." position="inside">
                <script type="text/javascript"
                        src="/library_book/static/src/js/widgets.js"/>
            </xpath>

            <!-- CSS files -->
            <xpath expr="." position="inside">
                <link rel="stylesheet"
                      type="text/css"
                      href="/library_book/static/src/css/widgets.css"/>
            </xpath>

        </template>
    </data>
</odoo>
```

```python
# library_book/__manifest__.py
'data': [
    'views/assets.xml',
    # ... other data files
]
```

### Frontend Website Assets

```bash
/web-assets website_custom frontend "static/src/js/main.js,static/src/js/slider.js,static/src/scss/style.scss,static/src/xml/templates.xml"
```

Output:
```xml
<!-- website_custom/views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <template id="assets_frontend"
                  name="Website Custom Frontend Assets"
                  inherit_id="web.assets_frontend">

            <!-- JavaScript files -->
            <xpath expr="." position="inside">
                <script type="text/javascript"
                        src="/website_custom/static/src/js/main.js"/>
                <script type="text/javascript"
                        src="/website_custom/static/src/js/slider.js"/>
            </xpath>

            <!-- CSS files -->
            <xpath expr="." position="inside">
                <link rel="stylesheet"
                      type="text/scss"
                      href="/website_custom/static/src/scss/style.scss"/>
            </xpath>

            <!-- QWeb templates -->
            <xpath expr="." position="inside">
                <script type="text/xml"
                        src="/website_custom/static/src/xml/templates.xml"/>
            </xpath>

        </template>
    </data>
</odoo>
```

### Complete Module Assets with Dependencies

```bash
/web-assets sale_custom backend "static/src/js/utils.js,static/src/js/widgets/color_picker.js,static/src/js/widgets/status_widget.js,static/src/js/views/form_view.js,static/src/scss/widgets.scss,static/src/scss/custom.scss,static/src/xml/widgets.xml" depends="web.assets_common"
```

Output:
```xml
<!-- sale_custom/views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Backend Assets -->
        <template id="assets_backend"
                  name="Sale Custom Backend Assets"
                  inherit_id="web.assets_backend"
                  priority="10">

            <!-- Utilities first -->
            <xpath expr="script[last()]" position="after">
                <script type="text/javascript"
                        src="/sale_custom/static/src/js/utils.js"/>
            </xpath>

            <!-- Widget files -->
            <xpath expr="script[last()]" position="after">
                <script type="text/javascript"
                        src="/sale_custom/static/src/js/widgets/color_picker.js"/>
                <script type="text/javascript"
                        src="/sale_custom/static/src/js/widgets/status_widget.js"/>
            </xpath>

            <!-- View files -->
            <xpath expr="script[last()]" position="after">
                <script type="text/javascript"
                        src="/sale_custom/static/src/js/views/form_view.js"/>
            </xpath>

            <!-- Stylesheets -->
            <xpath expr="link[last()]" position="after">
                <link rel="stylesheet"
                      type="text/scss"
                      href="/sale_custom/static/src/scss/widgets.scss"/>
                <link rel="stylesheet"
                      type="text/scss"
                      href="/sale_custom/static/src/scss/custom.scss"/>
            </xpath>

            <!-- QWeb templates -->
            <xpath expr="." position="inside">
                <script type="text/xml"
                        src="/sale_custom/static/src/xml/widgets.xml"/>
            </xpath>

        </template>
    </data>
</odoo>
```

### Multiple Asset Bundles

```bash
/web-assets project_custom backend,frontend "static/src/js/backend.js|static/src/js/frontend.js,static/src/scss/backend.scss|static/src/scss/frontend.scss"
```

Output:
```xml
<!-- project_custom/views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Backend Assets -->
        <template id="assets_backend"
                  name="Project Custom Backend Assets"
                  inherit_id="web.assets_backend"
                  priority="15">

            <xpath expr="." position="inside">
                <script type="text/javascript"
                        src="/project_custom/static/src/js/backend.js"/>
                <link rel="stylesheet"
                      type="text/scss"
                      href="/project_custom/static/src/scss/backend.scss"/>
            </xpath>

        </template>

        <!-- Frontend Assets -->
        <template id="assets_frontend"
                  name="Project Custom Frontend Assets"
                  inherit_id="web.assets_frontend"
                  priority="15">

            <xpath expr="." position="inside">
                <script type="text/javascript"
                        src="/project_custom/static/src/js/frontend.js"/>
                <link rel="stylesheet"
                      type="text/scss"
                      href="/project_custom/static/src/scss/frontend.scss"/>
            </xpath>

        </template>

    </data>
</odoo>
```

### Report Assets

```bash
/web-assets invoice_custom reports "static/src/js/report.js,static/src/scss/report.scss,static/src/xml/report.xml"
```

Output:
```xml
<!-- invoice_custom/views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Report Assets -->
        <template id="assets_report"
                  name="Invoice Custom Report Assets"
                  inherit_id="web.report_assets">

            <xpath expr="." position="inside">
                <script type="text/javascript"
                        src="/invoice_custom/static/src/js/report.js"/>
                <link rel="stylesheet"
                      type="text/scss"
                      href="/invoice_custom/static/src/scss/report.scss"/>
                <script type="text/xml"
                        src="/invoice_custom/static/src/xml/report.xml"/>
            </xpath>

        </template>

    </data>
</odoo>
```

### Custom Asset Bundle

```bash
/web-assets library_book assets "static/src/js/app.js,static/src/scss/app.scss" assets_id="module.main_assets"
```

Output:
```xml
<!-- library_book/views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Custom Asset Bundle -->
        <template id="main_assets"
                  name="Library Book Main Assets"
                  xml:space="preserve">

            <t t-call="web.assets_bootstrap">
                <t t-call="web.assets_frontend">
                    <t t-call="web.assets_common">
                        <!-- Module specific assets -->
                        <script type="text/javascript"
                                src="/library_book/static/src/js/app.js"/>
                        <link rel="stylesheet"
                              type="text/scss"
                              href="/library_book/static/src/scss/app.scss"/>
                    </t>
                </t>
            </t>

        </template>
    </data>
</odoo>
```

## Asset Bundle Types

### Backend Assets (web.assets_backend)
- Used for: Backend (admin) interface
- Loads: After common assets
- Includes: OWL framework, web client, views, widgets

### Frontend Assets (web.assets_frontend)
- Used for: Website public pages
- Loads: After common assets
- Includes: Website editor, frontend components

### Common Assets (web.assets_common)
- Used for: Shared between backend and frontend
- Loads: First
- Includes: Core libraries, jQuery, OWL

### Report Assets (web.report_assets)
- Used for: QWeb reports (PDF, HTML)
- Loads: Separate bundle
- Includes: Report-specific styles and scripts

## XPath Positioning

### Add at the end
```xml
<xpath expr="." position="inside">
    <!-- Content added at the end -->
</xpath>
```

### Add after specific element
```xml
<xpath expr="script[last()]" position="after">
    <!-- Content added after last script -->
</xpath>
```

### Add before specific element
```xml
<xpath expr="link[1]" position="before">
    <!-- Content added before first link -->
</xpath>
```

### Replace specific element
```xml
<xpath expr="script[@src='/path/to/file.js']" position="replace">
    <!-- New content replaces the element -->
</xpath>
```

### Remove specific element
```xml
<xpath expr="script[@src='/path/to/file.js']" position="replace"/>
```

## File Type Attributes

### JavaScript Files
```xml
<!-- Standard JavaScript -->
<script type="text/javascript"
        src="/module/static/src/js/file.js"/>

<!-- ES6 Module -->
<script type="module"
        src="/module/static/src/js/module.js"/>

<!-- With defer -->
<script type="text/javascript"
        src="/module/static/src/js/file.js"
        defer="defer"/>
```

### CSS/SCSS Files
```xml
<!-- CSS -->
<link rel="stylesheet"
      type="text/css"
      href="/module/static/src/css/file.css"/>

<!-- SCSS/SASS -->
<link rel="stylesheet"
      type="text/scss"
      href="/module/static/src/scss/file.scss"/>

<!-- With media query -->
<link rel="stylesheet"
      type="text/css"
      href="/module/static/src/css/print.css"
      media="print"/>
```

### XML Templates
```xml
<!-- QWeb templates -->
<script type="text/xml"
        src="/module/static/src/xml/templates.xml"/>
```

## Best Practices

1. **File Organization:**
   - Group files by type (JS, CSS, XML)
   - Use descriptive filenames
   - Organize in logical directories

2. **Loading Order:**
   - Dependencies first
   - Core files before feature files
   - Utilities before components
   - CSS before JS (when possible)

3. **Performance:**
   - Minify assets for production
   - Use SCSS for better organization
   - Lazy load non-critical assets
   - Consider bundle splitting

4. **Naming Conventions:**
   - Template IDs: `{module}.{purpose}_assets`
   - Descriptive names for clarity
   - Consistent prefixes

5. **Version Control:**
   - Use priority to control load order
   - Avoid conflicts with other modules
   - Test with different module combinations

## Asset Loading Order

Odoo 19 loads assets in this order:
1. Bootstrap assets (jQuery, underscore)
2. Common assets (OWL framework, core)
3. Backend/frontend assets (views, widgets)
4. Module-specific assets (your files)

Within each bundle, files load in:
- Priority order (lower numbers first)
- XPath position
- Document order

## Debugging Assets

### Enable Assets Debugging
```
?debug=assets
```

### Rebuild Assets
```bash
odoo-bin -c odoo.conf --stop-after-init
```

### Clear Cache
```bash
# In Settings > Technical > System Parameters
# web_base_url.sanitize_css = False
```

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── views/
│   └── assets.xml
└── static/
    └── src/
        ├── js/
        │   ├── utils/
        │   │   └── utils.js
        │   ├── widgets/
        │   │   ├── widget1.js
        │   │   └── widget2.js
        │   └── main.js
        ├── scss/
        │   ├── variables.scss
        │   ├── mixins.scss
        │   └── main.scss
        ├── css/
        │   └── custom.css
        └── xml/
            └── templates.xml
```

## Next Steps

After creating assets, use:
- `/web-widget` - Create custom widgets
- `/web-template` - Create QWeb templates
- `/controller-new` - Create HTTP controllers for frontend
- `/view-form` - Use widgets in views
