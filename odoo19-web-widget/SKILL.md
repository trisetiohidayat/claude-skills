---
description: Create custom web widget extending basic field widgets for Odoo 19. Use when user wants to create a custom web widget.
---


# Odoo 19 Web Widget Creation

Create a custom web widget extending Odoo 19 basic field widgets with proper field registry setup, field properties configuration, and widget rendering logic.

## Instructions

1. **Determine the file location:**
   - Widget JavaScript should be in: `{module_name}/static/src/js/{widget_filename}.js`
   - Widget XML templates should be in: `{module_name}/static/src/xml/{widget_filename}.xml`
   - Widget CSS should be in: `{module_name}/static/src/css/{widget_filename}.css`

2. **Generate the widget class structure:**

```javascript
/** @odoo-module **/
import { fieldRegistry } from 'web.field_registry';
import { FieldXxx } from 'web.basic_fields';
import { registry } from '@web/core/registry';

const { Component, useState } = owl;

export class CustomWidget extends FieldXxx {
    // Widget properties
    static template = 'module_name.CustomWidgetTemplate';

    setup() {
        super.setup();
        // Custom setup code
    }

    // Custom methods
}
```

3. **Widget field types:**
   - `basic_field` - Basic field widgets (Char, Text, Integer, Float, Date, etc.)
   - `abstract_field` - Abstract field widgets with common functionality
   - `relational_field` - Relational field widgets (Many2one, One2many, Many2many)

4. **Common parent widgets to extend:**
   - `FieldChar` - For text/string fields
   - `FieldText` - For multi-line text fields
   - `FieldInteger` - For integer fields
   - `FieldFloat` - For float/decimal fields
   - `FieldDate` - For date fields
   - `FieldDateTime` - For datetime fields
   - `FieldBoolean` - For boolean/toggle fields
   - `FieldSelection` - For selection dropdown fields
   - `FieldMany2one` - For many2one relational fields
   - `FieldOne2many` - For one2many relational fields
   - `FieldMany2many` - For many2many relational fields
   - `FieldRadio` - For radio button fields
   - `FieldBinaryFile` - For file upload fields
   - `FieldBinaryImage` - For image fields

5. **Register the widget:**

```javascript
fieldRegistry.add('custom_widget', CustomWidget);
// OR for OWL framework
registry.category('fields').add('custom_widget', CustomWidget);
```

6. **Include XML template:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="module_name.CustomWidgetTemplate" owl="1">
        <!-- Widget template content -->
    </t>
</templates>
```

7. **Add to web.assets:**
   - Create or update `{module_name}/views/assets.xml`
   - Add JavaScript and XML files to appropriate bundles

## Usage Examples

### Basic Color Picker Widget

```bash
/web-widget library_book color_picker basic_field FieldChar
```

Output:
```javascript
// library_book/static/src/js/color_picker_widget.js
/** @odoo-module **/
import { fieldRegistry } from 'web.field_registry';
import { FieldChar } from 'web.basic_fields';
import { registry } from '@web/core/registry';

export class ColorPickerWidget extends FieldChar {
    /**
     * @override
     */
    setup() {
        super.setup();
        this.colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'];
    }

    /**
     * Handle color selection
     * @param {string} color - Selected color
     */
    onColorClick(color) {
        this._setValue(color);
    }

    /**
     * Check if color is selected
     * @param {string} color - Color to check
     * @returns {boolean}
     */
    isColorSelected(color) {
        return this.value === color;
    }
}

ColorPickerWidget.template = 'library_book.ColorPickerWidgetTemplate';
ColorPickerWidget.components = {};

fieldRegistry.add('color_picker', ColorPickerWidget);
```

```xml
<!-- library_book/static/src/xml/color_picker_widget.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="library_book.ColorPickerWidgetTemplate" owl="1">
        <div class="o_color_picker_widget">
            <t t-foreach="widget.colors" t-as="color" t-key="color">
                <div class="o_color_swatch"
                     t-att-class="widget.isColorSelected(color) ? 'o_color_selected' : ''"
                     t-att-style="'background-color: ' + color"
                     t-on-click="() => widget.onColorClick(color)"/>
            </t>
        </div>
    </t>
</templates>
```

```css
/* library_book/static/src/css/color_picker_widget.css */
.o_color_picker_widget {
    display: flex;
    gap: 8px;
    padding: 8px;
}

.o_color_swatch {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
}

.o_color_swatch:hover {
    transform: scale(1.1);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.o_color_swatch.o_color_selected {
    border-color: #000;
    box-shadow: 0 0 0 2px #fff, 0 0 0 4px #000;
}
```

### Advanced Status Widget

```bash
/web-widget sale_custom advance_status basic_field FieldSelection
```

Output:
```javascript
// sale_custom/static/src/js/advance_status_widget.js
/** @odoo-module **/
import { fieldRegistry } from 'web.field_registry';
import { FieldSelection } from 'web.basic_fields';

export class AdvanceStatusWidget extends FieldSelection {
    setup() {
        super.setup();
        this.statusConfig = {
            'draft': { label: 'Draft', color: '#6c757d', icon: 'fa-file' },
            'confirmed': { label: 'Confirmed', color: '#007bff', icon: 'fa-check' },
            'approved': { label: 'Approved', color: '#28a745', icon: 'fa-thumbs-up' },
            'rejected': { label: 'Rejected', color: '#dc3545', icon: 'fa-times' },
            'done': { label: 'Done', color: '#17a2b8', icon: 'fa-flag-checkered' },
        };
    }

    get currentStatus() {
        return this.statusConfig[this.value] || this.statusConfig['draft'];
    }

    canTransitionTo(status) {
        const transitions = {
            'draft': ['confirmed', 'rejected'],
            'confirmed': ['approved', 'rejected'],
            'approved': ['done'],
            'rejected': ['draft'],
            'done': [],
        };
        return transitions[this.value]?.includes(status) || false;
    }

    onStatusClick(status) {
        if (this.canTransitionTo(status)) {
            this._setValue(status);
            this.trigger('status_changed', { newStatus: status });
        }
    }
}

AdvanceStatusWidget.template = 'sale_custom.AdvanceStatusWidgetTemplate';

fieldRegistry.add('advance_status', AdvanceStatusWidget);
```

### Custom Many2One Avatar Widget

```bash
/web-widget hr_custom custom_avatar relational_field FieldMany2one
```

Output:
```javascript
// hr_custom/static/src/js/custom_avatar_widget.js
/** @odoo-module **/
import { fieldRegistry } from 'web.field_registry';
import { FieldMany2One } from 'web.relational_fields';

export class CustomAvatarWidget extends FieldMany2One {
    setup() {
        super.setup();
        this.avatarSize = this.nodeOptions.avatar_size || 'medium';
        this.showName = this.nodeOptions.show_name !== false;
        this.showEmail = this.nodeOptions.show_email || false;
    }

    get avatarSizeClass() {
        return `o_avatar_${this.avatarSize}`;
    }

    get recordData() {
        return this.value && {
            id: this.value.resId,
            name: this.value.data.display_name,
            email: this.value.data.email,
            image: this.value.data.image_128,
        };
    }

    onAvatarClick() {
        if (this.recordData && this.recordData.id) {
            this.trigger('clicked', {
                recordId: this.recordData.id,
                model: this.field.relation,
            });
        }
    }
}

CustomAvatarWidget.template = 'hr_custom.CustomAvatarWidgetTemplate';

fieldRegistry.add('custom_avatar', CustomAvatarWidget);
```

```xml
<!-- hr_custom/static/src/xml/custom_avatar_widget.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="hr_custom.CustomAvatarWidgetTemplate" owl="1">
        <div class="o_custom_avatar_widget" t-on-click="widget.onAvatarClick">
            <img t-if="widget.recordData and widget.recordData.image"
                 t-att-src="'data:image/png;base64,' + widget.recordData.image"
                 t-att-class="'o_avatar ' + widget.avatarSizeClass"
                 alt="Avatar"/>
            <div t-else="" class="o_avatar o_avatar_empty" t-att-class="widget.avatarSizeClass">
                <t t-esc="widget.recordData and widget.recordData.name ? widget.recordData.name[0] : ''"/>
            </div>
            <div class="o_avatar_info" t-if="widget.showName or widget.showEmail">
                <div class="o_avatar_name" t-if="widget.showName">
                    <t t-esc="widget.recordData and widget.recordData.name or ''"/>
                </div>
                <div class="o_avatar_email" t-if="widget.showEmail">
                    <t t-esc="widget.recordData and widget.recordData.email or ''"/>
                </div>
            </div>
        </div>
    </t>
</templates>
```

### Progress Bar Widget for Float Fields

```bash
/web-widget project_custom progress_bar basic_field FieldFloat
```

Output:
```javascript
// project_custom/static/src/js/progress_bar_widget.js
/** @odoo-module **/
import { fieldRegistry } from 'web.field_registry';
import { FieldFloat } from 'web.basic_fields';

export class ProgressBarWidget extends FieldFloat {
    setup() {
        super.setup();
        this.maxValue = this.nodeOptions.max || 100;
        this.showPercentage = this.nodeOptions.show_percentage !== false;
        this.colorScheme = this.nodeOptions.color_scheme || 'default';
    }

    get percentage() {
        if (!this.value) return 0;
        return Math.min((this.value / this.maxValue) * 100, 100);
    }

    get barColor() {
        const schemes = {
            'default': '#007bff',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'gradient': 'linear-gradient(90deg, #007bff 0%, #28a745 100%)',
        };
        return schemes[this.colorScheme] || schemes['default'];
    }

    get progressClass() {
        if (this.percentage >= 100) return 'o_progress_complete';
        if (this.percentage >= 75) return 'o_progress_high';
        if (this.percentage >= 50) return 'o_progress_medium';
        if (this.percentage >= 25) return 'o_progress_low';
        return 'o_progress_very_low';
    }
}

ProgressBarWidget.template = 'project_custom.ProgressBarWidgetTemplate';

fieldRegistry.add('progress_bar', ProgressBarWidget);
```

```xml
<!-- project_custom/static/src/xml/progress_bar_widget.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="project_custom.ProgressBarWidgetTemplate" owl="1">
        <div class="o_progress_bar_container">
            <div class="o_progress_bar">
                <div class="o_progress_fill"
                     t-att-class="widget.progressClass"
                     t-att-style="'width: ' + widget.percentage + '%; background: ' + widget.barColor">
                    <span t-if="widget.showPercentage" class="o_progress_label">
                        <t t-esc="Math.round(widget.percentage)"/>%
                    </span>
                </div>
            </div>
            <div class="o_progress_text" t-if="!widget.showPercentage">
                <t t-esc="widget.value or 0"/> / <t t-esc="widget.maxValue"/>
            </div>
        </div>
    </t>
</templates>
```

## Widget Features

### Field Properties
- `this.value` - Current field value
- `this.record` - Current record data
- `this.field` - Field definition
- `this.fieldType` - Field type (char, many2one, etc.)
- `this.nodeOptions` - Widget options from XML
- `this.readonly` - Field readonly state
- `this.required` - Field required state

### Widget Methods
- `setup()` - Initialize widget (OWL lifecycle)
- `_setValue(value)` - Set field value
- `isValid()` - Validate field value
- `focus()` - Focus on widget
- `commitChanges()` - Commit pending changes

### Widget Events
- `this.trigger('changed', { data })` - Trigger change event
- `this.trigger('focused')` - Trigger focus event
- `this.trigger('blurred')` - Trigger blur event
- `this.trigger('field_changed')` - Field value changed

## Best Practices

1. **Naming Conventions:**
   - Widget name: lowercase_with_underscores
   - Widget class: PascalCase (e.g., `ColorPickerWidget`)
   - Template: `{module}.{WidgetName}Template`

2. **Widget Options:**
   - Pass options via XML: `widget="custom_widget" options="{'max': 100}"`
   - Access via `this.nodeOptions`
   - Provide sensible defaults

3. **Performance:**
   - Use reactive properties with `this.value`
   - Avoid expensive operations in render
   - Cache computed values

4. **Accessibility:**
   - Add proper ARIA labels
   - Support keyboard navigation
   - Provide visual feedback

5. **Testing:**
   - Test with different field values
   - Test readonly/required states
   - Test in different views (form, list, kanban)

## Using Custom Widgets in Views

```xml
<record id="view_custom_form" model="ir.ui.view">
    <field name="name">custom.model.form</field>
    <field name="model">custom.model</field>
    <field name="arch" type="xml">
        <form>
            <field name="color" widget="color_picker"/>
            <field name="status" widget="advance_status"
                   options="{'show_history': True}"/>
            <field name="assignee_id" widget="custom_avatar"
                   options="{'avatar_size': 'large', 'show_email': True}"/>
            <field name="progress" widget="progress_bar"
                   options="{'max': 100, 'show_percentage': True, 'color_scheme': 'success'}"/>
        </form>
    </field>
</record>
```

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   └── ...
├── views/
│   └── assets.xml  # Include widget files
└── static/
    ├── src/
    │   ├── js/
    │   │   └── {widget_name}_widget.js
    │   ├── xml/
    │   │   └── {widget_name}_widget.xml
    │   └── css/
    │       └── {widget_name}_widget.css
    └── description/
        └── icon.png
```

## Next Steps

After creating the widget, use:
- `/web-assets` - Add widget JS/CSS/XML to asset bundles
- `/web-template` - Create widget templates if needed
- `/view-form` - Use widget in form views
- `/view-tree` - Use widget in list views (with `widget="widget_name"`)
