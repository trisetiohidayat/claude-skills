---
description: Migrate __manifest__.py files from older Odoo versions to Odoo 19 format. Use when user wants to migrate a module manifest to Odoo 19.
---


# Odoo 19 Manifest Migration

Migrate `__manifest__.py` files from older Odoo versions to Odoo 19 format, updating dependencies, version requirements, data files, and configuration keys.

## Instructions

1. **Read the target __manifest__.py file:**
   - Identify current structure and keys
   - Check for deprecated keys and values
   - Note external dependencies and requirements

2. **Update version to '19.0':**
   - Set `'version': '19.0.0.1'` (or appropriate version number)
   - Use semantic versioning: major.minor.patch

3. **Update dependencies:**
   - Remove deprecated module dependencies
   - Add new required dependencies for Odoo 19
   - Update module names if they changed
   - Ensure proper dependency order

4. **Update data files:**
   - Check `data` key for XML files
   - Check `demo` key for demo XML files
   - Ensure file paths are correct
   - Update file extensions if needed

5. **Update assets:**
   - Check `assets` key structure
   - Update web asset bundles
   - Ensure CSS/JS files are properly referenced

6. **Update external dependencies:**
   - Check `external_dependencies` key
   - Update Python package requirements
   - Ensure versions are compatible with Odoo 19

7. **Remove deprecated keys:**
   - Remove `depends` (use `depends` or check if still valid)
   - Remove `installable` (no longer needed)
   - Remove `auto_install` if not needed
   - Remove `post_init_hook` if not needed

8. **Update configuration keys:**
   - Ensure `name` is present and descriptive
   - Ensure `summary` is present
   - Ensure `description` is present (can be long)
   - Ensure `author` is present
   - Ensure `category` is present
   - Ensure `website` is present (optional)
   - Ensure `license` is present (LGPL-3, OPL-1, etc.)

## Common Migration Patterns

### Pattern 1: Basic Version Update

**Before (Odoo 17):**
```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'My custom module',
    'author': 'My Company',
    'depends': ['base'],
}
```

**After (Odoo 19):**
```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'My custom module',
    'author': 'My Company',
    'depends': ['base'],
}
```

### Pattern 2: Update Dependencies

**Before (Odoo 15-17):**
```python
{
    'name': 'Sale Enhancement',
    'version': '17.0.1.0.0',
    'depends': [
        'sale',
        'sale_stock',
        'web',
        'web_kanban',
    ],
}
```

**After (Odoo 19):**
```python
{
    'name': 'Sale Enhancement',
    'version': '19.0.1.0.0',
    'depends': [
        'sale',
        'sale_stock',
        'web',
    ],
}
```

### Pattern 3: Update Data Files

**Before (Odoo 14-16):**
```python
{
    'data': [
        'security/my_module_security.xml',
        'security/ir.model.access.csv',
        'views/my_module_views.xml',
        'views/my_module_templates.xml',
        'report/my_module_reports.xml',
        'wizard/my_module_wizard_views.xml',
    ],
    'demo': [
        'demo/my_module_demo.xml',
    ],
}
```

**After (Odoo 19):**
```python
{
    'data': [
        'security/my_module_security.xml',
        'security/ir.model.access.csv',
        'views/my_module_views.xml',
        'views/my_module_templates.xml',
        'report/my_module_reports.xml',
        'wizard/my_module_wizard_views.xml',
    ],
    'demo': [
        'demo/my_module_demo.xml',
    ],
}
```

### Pattern 4: Update Assets

**Before (Odoo 15-17):**
```python
{
    'assets': {
        'web.assets_frontend': [
            'my_module/static/src/css/my_module.css',
            'my_module/static/src/js/my_module.js',
        ],
        'web.assets_backend': [
            'my_module/static/src/js/backend.js',
        ],
    },
}
```

**After (Odoo 19):**
```python
{
    'assets': {
        'web.assets_frontend': [
            'my_module/static/src/css/my_module.css',
            'my_module/static/src/js/my_module.js',
        ],
        'web.assets_backend': [
            'my_module/static/src/js/backend.js',
        ],
    },
}
```

### Pattern 5: Add External Dependencies

**Before (Odoo 14-16):**
```python
{
    'external_dependencies': {
        'python': ['requests', 'openpyxl'],
        'bin': [],
    },
}
```

**After (Odoo 19):**
```python
{
    'external_dependencies': {
        'python': ['requests', 'openpyxl'],
        'bin': [],
    },
}
```

## Usage Examples

### Example 1: Simple Module Migration

```bash
/migrate-manifest __manifest__.py
```

**Input File (__manifest__.py):**
```python
{
    'name': 'Library Management',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Library book management system',
    'author': 'My Company',
    'website': 'https://www.mycompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/library_author_views.xml',
    ],
    'demo': [
        'demo/library_demo.xml',
    ],
    'installable': True,
}
```

**Output File (__manifest__.py):**
```python
{
    'name': 'Library Management',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Library book management system',
    'author': 'My Company',
    'description': """
        Library Management Module
        ==========================
        This module provides a complete library book management system.
        Features:
        * Book catalog management
        * Author tracking
        * Book borrowing system
    """,
    'website': 'https://www.mycompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/library_author_views.xml',
    ],
    'demo': [
        'demo/library_demo.xml',
    ],
    'images': ['static/description/banner.png'],
}
```

### Example 2: Module with Web Assets

```bash
/migrate-manifest custom_website/__manifest__.py
```

**Input File (custom_website/__manifest__.py):**
```python
{
    'name': 'Custom Website',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': 'Custom website enhancements',
    'author': 'My Company',
    'depends': [
        'website',
        'website_sale',
    ],
    'data': [
        'views/templates.xml',
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_website/static/src/css/custom.css',
            'custom_website/static/src/js/custom.js',
        ],
    },
    'qweb': [
        'static/src/xml/custom.xml',
    ],
}
```

**Output File (custom_website/__manifest__.py):**
```python
{
    'name': 'Custom Website',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Custom website enhancements',
    'author': 'My Company',
    'description': """
        Custom Website Module
        =====================
        This module provides custom enhancements for the website.
    """,
    'depends': [
        'website',
        'website_sale',
    ],
    'data': [
        'views/templates.xml',
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_website/static/src/css/custom.css',
            'custom_website/static/src/js/custom.js',
        ],
    },
    'images': ['static/description/banner.png'],
}
```

### Example 3: Module with External Dependencies

```bash
/migrate-manifest sync_connector/__manifest__.py
```

**Input File (sync_connector/__manifest__.py):**
```python
{
    'name': 'Sync Connector',
    'version': '15.0.1.0.0',
    'category': 'Connector',
    'summary': 'External system synchronization',
    'author': 'My Company',
    'depends': [
        'base',
        'connector',
    ],
    'external_dependencies': {
        'python': ['requests>=2.25.0', 'zeep>=4.0.0'],
        'bin': ['curl'],
    },
    'data': [
        'views/connector_views.xml',
        'security/connector_security.xml',
    ],
}
```

**Output File (sync_connector/__manifest__.py):**
```python
{
    'name': 'Sync Connector',
    'version': '19.0.1.0.0',
    'category': 'Connector',
    'summary': 'External system synchronization',
    'author': 'My Company',
    'description': """
        Sync Connector Module
        =====================
        This module provides synchronization with external systems.
        Supports:
        * REST API integration
        * SOAP integration
        * Scheduled synchronization jobs
    """,
    'depends': [
        'base',
        'connector',
    ],
    'external_dependencies': {
        'python': ['requests>=2.32.0', 'zeep>=4.2.1'],
        'bin': ['curl'],
    },
    'data': [
        'views/connector_views.xml',
        'security/connector_security.xml',
    ],
    'images': ['static/description/banner.png'],
}
```

### Example 4: Complete Module Migration

```bash
/migrate-manifest sale_promotion/__manifest__.py
```

**Input File (sale_promotion/__manifest__.py):**
```python
{
    'name': 'Sale Promotion',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Promotion and discount management',
    'author': 'My Company',
    'website': 'https://www.mycompany.com',
    'license': 'OPL-1',
    'depends': [
        'sale',
        'sale_management',
        'product',
        'web',
        'web_kanban',
    ],
    'data': [
        'security/sale_promotion_security.xml',
        'security/ir.model.access.csv',
        'views/sale_promotion_views.xml',
        'views/sale_promotion_templates.xml',
        'report/sale_promotion_reports.xml',
        'wizard/promotion_wizard_views.xml',
        'data/sale_promotion_data.xml',
    ],
    'demo': [
        'demo/sale_promotion_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_promotion/static/src/css/promotion.css',
            'sale_promotion/static/src/js/promotion.js',
        ],
        'web.assets_frontend': [
            'sale_promotion/static/src/css/frontend.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}
```

**Output File (sale_promotion/__manifest__.py):**
```python
{
    'name': 'Sale Promotion',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Promotion and discount management',
    'author': 'My Company',
    'description': """
        Sale Promotion Module
        =====================
        This module provides comprehensive promotion and discount management for sales.
        Features:
        * Flexible promotion rules
        * Discount codes and coupons
        * Time-based promotions
        * Customer-specific promotions
        * Analytics and reporting
    """,
    'website': 'https://www.mycompany.com',
    'license': 'OPL-1',
    'depends': [
        'sale',
        'sale_management',
        'product',
        'web',
    ],
    'data': [
        'security/sale_promotion_security.xml',
        'security/ir.model.access.csv',
        'views/sale_promotion_views.xml',
        'views/sale_promotion_templates.xml',
        'report/sale_promotion_reports.xml',
        'wizard/promotion_wizard_views.xml',
        'data/sale_promotion_data.xml',
    ],
    'demo': [
        'demo/sale_promotion_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_promotion/static/src/css/promotion.css',
            'sale_promotion/static/src/js/promotion.js',
        ],
        'web.assets_frontend': [
            'sale_promotion/static/src/css/frontend.css',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
}
```

## Key Changes Summary

### Removed Keys
- `installable` - No longer needed, always True
- `auto_install` - Keep if needed, otherwise remove

### Updated Keys
- `version` - Update to '19.0.x.x.x' format
- `depends` - Update module dependencies
- `external_dependencies` - Update Python package versions

### Recommended Keys
- `description` - Add detailed description (multi-line)
- `images` - Add banner and icon images

## Common Odoo 19 Dependencies

### Core Dependencies
```python
'depends': [
    'base',              # Always required
    'web',               # For web interface
]
```

### Sales Dependencies
```python
'depends': [
    'sale',              # Sales module
    'sale_management',   # Sales management
    'sale_stock',        # Sales and stock
    'sale_payment',      # Sale payment
]
```

### Accounting Dependencies
```python
'depends': [
    'account',           # Accounting
    'account_invoicing', # Invoicing
    'account_payment',   # Payment
]
```

### Website Dependencies
```python
'depends': [
    'website',           # Website builder
    'website_sale',      # E-commerce
    'website_form',      # Website forms
]
```

### Inventory Dependencies
```python
'depends': [
    'stock',             # Inventory management
    'stock_account',     # Stock accounting
    'mrp',               # Manufacturing
]
```

## External Dependencies Versions

### Common Python Packages (Odoo 19)
```python
'external_dependencies': {
    'python': [
        'requests>=2.32.0',      # HTTP library
        'zeep>=4.2.1',           # SOAP client
        'openpyxl>=3.1.0',       # Excel files
        'Pillow>=10.0.0',        # Image processing
        'reportlab>=4.0.0',      # PDF generation
        'python-dateutil>=2.8.2',# Date parsing
        'pytz>=2023.3',          # Timezones
        'babel>=2.14.0',         # Internationalization
    ],
}
```

## Migration Checklist

- [ ] Update version to '19.0.x.x.x'
- [ ] Update dependencies for Odoo 19
- [ ] Remove deprecated keys (installable, etc.)
- [ ] Add detailed description
- [ ] Update external dependencies versions
- [ ] Verify data file paths
- [ ] Update asset bundle references
- [ ] Add module images (banner, icon)
- [ ] Verify license is correct
- [ ] Test module installation
- [ ] Test module functionality
- [ ] Check for deprecated modules

## Important Notes

1. **Version Format:** Use '19.0.x.y.z' where:
   - x = major version
   - y = minor version
   - z = patch version

2. **Dependencies Order:** List dependencies in order:
   - Core modules first (base, web)
   - Related modules next
   - Custom modules last

3. **Data Files Order:** List data files in load order:
   - Security files first
   - Views next
   - Data files
   - Demo files last

4. **External Dependencies:** Be conservative with version requirements:
   - Specify minimum versions only
   - Test with Odoo 19's Python environment
   - Document any special requirements

5. **Description Format:** Use triple quotes for multi-line descriptions:
   - Keep it concise but informative
   - Highlight key features
   - Use proper formatting

6. **Images:** Include both icon and banner:
   - icon.png: 128x128 pixels
   - banner.png: 1920x400 pixels
   - Place in static/description/

## Testing After Migration

1. **Installation Test:**
   ```bash
   ./odoo-bin -i my_module -d test_db --stop-after-init
   ```

2. **Update Test:**
   ```bash
   ./odoo-bin -u my_module -d test_db --stop-after-init
   ```

3. **Dependency Check:**
   - Verify all dependencies install correctly
   - Check for missing modules
   - Resolve dependency conflicts

4. **Functionality Test:**
   - Test all module features
   - Check views render correctly
   - Verify security rules work
   - Test reports and wizards

## Related Skills

- `/module-new` - Create new module structure
- `/module-addon` - Create addon module
- `/migrate-model` - Migrate model files
- `/migrate-view` - Migrate view files
- `/data-xml` - Create data XML files
- `/security-group` - Create security groups
