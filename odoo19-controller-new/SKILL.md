---
description: Generate a new Odoo 19 http.Controller class with proper route decorators. Use when user wants to create a new HTTP controller.
---


# Odoo 19 HTTP Controller Creation

Generate a new Odoo 19 http.Controller class with proper route decorators following Odoo 19 conventions.

## Instructions

1. **Determine the file location:**
   - Controllers should be in: `{module_name}/controllers/{controller_filename}.py`
   - Use descriptive filenames (e.g., `main.py`, `api.py`, `portal.py`)

2. **Generate the controller class structure:**

```python
from odoo import http
from odoo.http import request

class {ControllerClassName}(http.Controller):
    {route_decorators}
    def {method_name}(self, **kwargs):
        # Controller logic here
        pass
```

3. **Route decorator patterns:**

```python
# Basic route
@http.route(['{route_prefix}/endpoint'], type='http', auth='{auth_type}', methods=['GET'])

# Multiple routes
@http.route(['{route_prefix}/endpoint1', '{route_prefix}/endpoint2'],
            type='http', auth='{auth_type}', methods=['GET'])

# With CSRF
@http.route('{route_prefix}/endpoint', type='http', auth='user',
            methods=['POST'], csrf=True)

# Without CSRF (for public APIs)
@http.route('{route_prefix}/endpoint', type='http', auth='none',
            methods=['POST'], csrf=False)
```

4. **Authentication types:**
   - `public` - Accessible without authentication (but can access user data if logged in)
   - `user` - Requires authenticated user
   - `none` - No authentication check, no session

5. **Add to __init__.py:**
   - Update `controllers/__init__.py` to import the new controller
   - Format: `from . import {controller_filename}`

6. **Include these standard imports:**

```python
from odoo import http
from odoo.http import request
```

## Usage Examples

### Basic Public Controller

```bash
/controller-new website_myshop MainController /myshop auth="public"
```

Output:
```python
# website_myshop/controllers/main.py

from odoo import http
from odoo.http import request

class MainController(http.Controller):

    @http.route(['/myshop', '/myshop/index'], type='http', auth='public', website=True)
    def index(self, **kwargs):
        return request.render('website_myshop.index', {
            'products': request.env['product.product'].search([]),
        })

    @http.route('/myshop/product/<model("product.product"):product>',
                type='http', auth='public', website=True)
    def product_detail(self, product, **kwargs):
        return request.render('website_myshop.product_detail', {
            'product': product,
        })
```

### Authenticated User Controller

```bash
/controller-new hr_portal PortalController /portal auth="user"
```

Output:
```python
# hr_portal/controllers/portal.py

from odoo import http
from odoo.http import request

class PortalController(http.Controller):

    @http.route('/portal/my-info', type='http', auth='user', website=True)
    def my_info(self, **kwargs):
        employee = request.env['hr.employee'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        return request.render('hr_portal.portal_my_info', {
            'employee': employee,
        })

    @http.route('/portal/leaves', type='http', auth='user', website=True)
    def leaves(self, **kwargs):
        leaves = request.env['hr.leave'].search([
            ('employee_id.user_id', '=', request.env.user.id)
        ])
        return request.render('hr_portal.portal_leaves', {
            'leaves': leaves,
        })
```

### API Controller with CSRF and CORS

```bash
/controller-new api_connector APIController /api/v1 auth="none" features="csrf,cors"
```

Output:
```python
# api_connector/controllers/api.py

from odoo import http
from odoo.http import request

class APIController(http.Controller):

    @http.route('/api/v1/status', type='http', auth='none', methods=['GET'], csrf=False)
    def status(self, **kwargs):
        return request.make_json_response({
            'status': 'ok',
            'version': '1.0',
        })

    @http.route('/api/v1/partners', type='http', auth='none',
                methods=['GET'], csrf=False)
    def get_partners(self, limit=20, **kwargs):
        partners = request.env['res.partner'].sudo().search([], limit=int(limit))
        data = [{'id': p.id, 'name': p.name, 'email': p.email} for p in partners]
        return request.make_json_response(data)

    @http.route('/api/v1/partner', type='http', auth='none',
                methods=['POST'], csrf=False)
    def create_partner(self, **kwargs):
        try:
            partner = request.env['res.partner'].sudo().create({
                'name': kwargs.get('name'),
                'email': kwargs.get('email'),
            })
            return request.make_json_response({
                'success': True,
                'id': partner.id,
            })
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e),
            }, status=400)
```

### Website Controller with Sitemap

```bash
/controller-new website_blog BlogController /blog auth="public" features="sitemap"
```

Output:
```python
# website_blog/controllers/main.py

from odoo import http
from odoo.http import request

class BlogController(http.Controller):

    @http.route(['/blog', '/blog/page/<int:page>'],
                type='http', auth='public', website=True, sitemap=True)
    def blog_list(self, page=1, **kwargs):
        posts = request.env['blog.post'].search([
            ('published', '=', True)
        ], limit=10, offset=(page - 1) * 10)
        return request.render('website_blog.blog_list', {
            'posts': posts,
            'page': page,
        })

    @http.route('/blog/post/<model("blog.post"):post>',
                type='http', auth='public', website=True, sitemap=True)
    def blog_post(self, post, **kwargs):
        return request.render('website_blog.blog_post', {
            'post': post,
        })

    @http.route('/blog/category/<model("blog.category"):category>',
                type='http', auth='public', website=True, sitemap=True)
    def blog_category(self, category, **kwargs):
        posts = request.env['blog.post'].search([
            ('category_id', '=', category.id),
            ('published', '=', True),
        ])
        return request.render('website_blog.blog_category', {
            'category': category,
            'posts': posts,
        })
```

## Route Decorator Options

### Type Parameter
- `type='http'` - Standard HTTP request/response
- `type='json'` - JSON request/response (automatically parses JSON body)

### Auth Parameter
- `auth='public'` - Public access, session available
- `auth='user'` - Requires login
- `auth='none'` - No session, no authentication

### Methods Parameter
- `methods=['GET']` - GET requests only
- `methods=['POST']` - POST requests only
- `methods=['GET', 'POST']` - Multiple methods

### CSRF Parameter
- `csrf=True` - CSRF protection enabled (default for POST)
- `csrf=False` - Disable CSRF (for public APIs)

### Additional Parameters
- `website=True` - Enable website features (templates, qweb)
- `sitemap=True` - Include in website sitemap
- `multilang=True` - Support multiple languages

## Best Practices

1. **URL Structure:**
   - Use lowercase with hyphens: `/my-shop/products`
   - Use RESTful patterns: `/api/v1/resource/<id>`
   - Group routes logically: `/admin/settings`, `/admin/users`

2. **Security:**
   - Always use appropriate `auth` level
   - Enable CSRF for form submissions
   - Use `sudo()` for public APIs with proper validation
   - Validate all input data

3. **Response Types:**
   - Use `request.render()` for HTML templates
   - Use `request.make_json_response()` for JSON APIs
   - Use `request.redirect()` for redirects

4. **Controller Organization:**
   - Group related routes in one controller
   - Separate frontend (website) from backend (admin)
   - Keep API controllers separate from web controllers

5. **Naming Conventions:**
   - Controller class: PascalCase (e.g., `MainController`)
   - Methods: lowercase_with_underscores (e.g., `get_products`)
   - Routes: lowercase-with-hyphens (e.g., `/my-shop/products`)

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py  # Import controllers here
│   ├── main.py       # Main website routes
│   ├── portal.py     # Customer/supplier portal
│   └── api.py        # API endpoints
├── views/
│   └── templates.xml  # QWeb templates
└── static/
    ├── src/
    │   ├── js/
    │   └── xml/
    └── description/
        └── icon.png
```

## Next Steps

After creating the controller, use:
- `/controller-http` - Add GET/POST handlers with HTML/JSON responses
- `/controller-json` - Add JSON request/response handlers with CORS
- `/web-template` - Create QWeb templates for HTML responses
