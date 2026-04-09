---
description: Generate HTTP endpoint handlers with GET/POST methods, HTML template rendering, and JSON response handling for Odoo 19. Use when user wants to create an HTTP controller endpoint.
---


# Odoo 19 HTTP Endpoint Handler

Generate HTTP endpoint handlers for GET/POST requests with proper response handling following Odoo 19 conventions.

## Instructions

1. **Determine the endpoint pattern:**

### GET Endpoints (HTML Response)
```python
@http.route('{route_path}', type='http', auth='{auth}', website=True)
def {method_name}(self, **kwargs):
    # Fetch data
    records = request.env['model.name'].search([])
    # Render template
    return request.render('{template}', {
        'records': records,
    })
```

### GET Endpoints (JSON Response)
```python
@http.route('{route_path}', type='http', auth='{auth}', methods=['GET'])
def {method_name}(self, **kwargs):
    data = {'key': 'value'}
    return request.make_json_response(data)
```

### POST Endpoints (Form Handling)
```python
@http.route('{route_path}', type='http', auth='{auth}', methods=['POST'], csrf=True)
def {method_name}(self, **kwargs):
    # Process form data
    record = request.env['model.name'].create(kwargs)
    # Redirect or render response
    return request.redirect('/success')
```

### POST Endpoints (JSON API)
```python
@http.route('{route_path}', type='http', auth='{auth}', methods=['POST'], csrf=False)
def {method_name}(self, **kwargs):
    try:
        # Process data
        result = self._process_data(kwargs)
        return request.make_json_response({'success': True, 'data': result})
    except Exception as e:
        return request.make_json_response({'success': False, 'error': str(e)}, status=400)
```

2. **Common response methods:**

```python
# HTML template
request.render('module.template_id', context_dict)

# JSON response
request.make_json_response(data_dict, status=200)

# Redirect
request.redirect('/target/url')

# File download
request.make_response(
    data,
    headers=[
        ('Content-Type', 'application/octet-stream'),
        ('Content-Disposition', 'attachment; filename=file.csv')
    ]
)
```

3. **Access request data:**

```python
# GET parameters
kwargs.get('param_name')

# POST form data
kwargs.get('field_name')

# JSON body (for type='json')
request.jsonrequest

# Current user
request.env.user

# Current company
request.env.company

# Session
request.session
```

## Usage Examples

### Simple GET with HTML Template

```bash
/controller-http get html /products auth="public" template="website_shop.products"
```

Output:
```python
@http.route('/products', type='http', auth='public', website=True)
def products(self, category=None, limit=20, **kwargs):
    domain = []
    if category:
        domain.append(('category_id', '=', int(category)))

    products = request.env['product.product'].search(
        domain,
        limit=int(limit)
    )

    categories = request.env['product.category'].search([])

    return request.render('website_shop.products', {
        'products': products,
        'categories': categories,
        'current_category': category,
    })
```

### GET with JSON Response

```bash
/controller-http get json /api/products/auth="none"
```

Output:
```python
@http.route('/api/products', type='http', auth='none', methods=['GET'], csrf=False)
def api_products(self, limit=20, category=None, **kwargs):
    domain = [('website_published', '=', True)]
    if category:
        domain.append(('category_id', '=', int(category)))

    products = request.env['product.product'].sudo().search(
        domain,
        limit=int(limit)
    )

    data = [{
        'id': p.id,
        'name': p.name,
        'price': p.list_price,
        'image_url': f'/web/image/product.product/{p.id}/image_1920',
    } for p in products]

    return request.make_json_response({
        'success': True,
        'count': len(data),
        'products': data,
    })
```

### POST Form Handler

```bash
/controller-http post html /contact/submit template="website_contact.success"
```

Output:
```python
@http.route('/contact/submit', type='http', auth='public', methods=['POST'], csrf=True)
def contact_submit(self, **kwargs):
    # Validate form data
    if not kwargs.get('email'):
        return request.render('website_contact.contact_form', {
            'error': 'Email is required',
            'defaults': kwargs,
        })

    # Create contact record
    request.env['mail.mail'].create({
        'subject': f"Contact Form: {kwargs.get('name', 'Anonymous')}",
        'email_from': kwargs.get('email'),
        'body_html': f"""
            <p><strong>Name:</strong> {kwargs.get('name')}</p>
            <p><strong>Email:</strong> {kwargs.get('email')}</p>
            <p><strong>Message:</strong></p>
            <p>{kwargs.get('message')}</p>
        """,
    }).send()

    return request.render('website_contact.success', {
        'name': kwargs.get('name'),
    })
```

### POST with JSON Response

```bash
/controller-http post json /api/quote auth="user"
```

Output:
```python
@http.route('/api/quote', type='http', auth='user', methods=['POST'], csrf=True)
def create_quote(self, **kwargs):
    try:
        # Validate required fields
        required = ['partner_id', 'lines']
        missing = [f for f in required if not kwargs.get(f)]
        if missing:
            return request.make_json_response({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}',
            }, status=400)

        # Create quote
        quote = request.env['sale.order'].create({
            'partner_id': int(kwargs['partner_id']),
            'order_line': kwargs['lines'],
        })

        return request.make_json_response({
            'success': True,
            'quote_id': quote.id,
            'quote_number': quote.name,
        })

    except Exception as e:
        return request.make_json_response({
            'success': False,
            'error': str(e),
        }, status=500)
```

### Detail Page with Model Routing

```bash
/controller-http get html /product/<model("product.product"):product> template="website_product.detail"
```

Output:
```python
@http.route('/product/<model("product.product"):product>',
            type='http', auth='public', website=True)
def product_detail(self, product, **kwargs):
    # Product is automatically fetched by model routing
    related_products = request.env['product.product'].search([
        ('category_id', '=', product.category_id.id),
        ('id', '!=', product.id),
    ], limit=4)

    return request.render('website_product.detail', {
        'product': product,
        'related_products': related_products,
    })
```

### Paginated List

```bash
/controller-http get html /blog auth="public" template="website_blog.list"
```

Output:
```python
@http.route(['/blog', '/blog/page/<int:page>'],
            type='http', auth='public', website=True)
def blog_list(self, page=1, category=None, **kwargs):
    domain = [('published', '=', True)]
    if category:
        domain.append(('category_id', '=', int(category)))

    # Count total
    total = request.env['blog.post'].search_count(domain)

    # Pagination
    posts_per_page = 10
    posts = request.env['blog.post'].search(
        domain,
        limit=posts_per_page,
        offset=(page - 1) * posts_per_page,
        order='date_published desc'
    )

    # Calculate pagination
    total_pages = (total + posts_per_page - 1) // posts_per_page

    return request.render('website_blog.list', {
        'posts': posts,
        'page': page,
        'total_pages': total_pages,
        'category': category,
    })
```

### Search Endpoint

```bash
/controller-http get json /search auth="public"
```

Output:
```python
@http.route('/search', type='http', auth='public', methods=['GET'], website=True)
def search(self, q=None, model='product.product', **kwargs):
    if not q:
        return request.render('website_search.search', {
            'results': [],
            'query': '',
        })

    # Search across multiple models
    products = request.env['product.product'].search([
        '|', '|',
        ('name', 'ilike', q),
        ('description', 'ilike', q),
        ('default_code', 'ilike', q),
    ], limit=10)

    blogs = request.env['blog.post'].search([
        ('name', 'ilike', q),
        ('published', '=', True),
    ], limit=5)

    return request.render('website_search.search', {
        'results': {
            'products': products,
            'blogs': blogs,
        },
        'query': q,
    })
```

### File Download

```bash
/controller-http get file /download/report auth="user"
```

Output:
```python
@http.route('/download/report', type='http', auth='user', methods=['GET'])
def download_report(self, report_type='pdf', **kwargs):
    # Generate report
    report = request.env.ref('module.report_action')
    data, format = report._render_qweb_pdf([kwargs.get('id')])

    # Determine content type
    content_types = {
        'pdf': 'application/pdf',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
    }

    filename = f"report_{kwargs.get('id')}.{format}"

    return request.make_response(
        data,
        headers=[
            ('Content-Type', content_types.get(format, 'application/octet-stream')),
            ('Content-Disposition', f'attachment; filename="{filename}"'),
            ('Content-Length', len(data)),
        ]
    )
```

### Redirect Handler

```bash
/controller-http post redirect /cart/add auth="public"
```

Output:
```python
@http.route('/cart/add', type='http', auth='public', methods=['POST'], csrf=True)
def add_to_cart(self, product_id, quantity=1, **kwargs):
    # Add to cart (session-based)
    cart = request.session.get('cart', [])
    cart.append({
        'product_id': int(product_id),
        'quantity': int(quantity),
    })
    request.session['cart'] = cart

    # Redirect to cart page
    return request.redirect('/cart?added=1')
```

## Response Patterns

### Success Response
```python
return request.make_json_response({
    'success': True,
    'data': {...},
})
```

### Error Response
```python
return request.make_json_response({
    'success': False,
    'error': 'Error message',
    'error_code': 'VALIDATION_ERROR',
}, status=400)
```

### Validation Error Response
```python
errors = {'field_name': 'Error message'}
return request.make_json_response({
    'success': False,
    'errors': errors,
}, status=422)
```

### Pagination Response
```python
return request.make_json_response({
    'success': True,
    'data': items,
    'pagination': {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
    }
})
```

## Best Practices

1. **Input Validation:**
   - Always validate user input
   - Convert to appropriate types (int, float)
   - Handle missing parameters gracefully

2. **Error Handling:**
   - Use try-except for operations
   - Return meaningful error messages
   - Use appropriate HTTP status codes

3. **Performance:**
   - Limit query results
   - Use `sudo()` carefully in public endpoints
   - Cache expensive operations

4. **Security:**
   - Use appropriate auth levels
   - Enable CSRF for form submissions
   - Validate file uploads
   - Sanitize user input

5. **Response Format:**
   - Keep JSON responses consistent
   - Use proper HTTP status codes
   - Include timestamps if relevant

## HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

## Next Steps

After creating HTTP handlers:
- `/controller-json` - Add advanced JSON handling with CORS
- `/web-template` - Create QWeb templates for HTML responses
- `/security-xml` - Add access rights if needed
