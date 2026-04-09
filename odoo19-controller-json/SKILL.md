---
description: Generate JSON request/response handlers with CORS support and API authentication for Odoo 19. Use when user wants to create a JSON API controller.
---


# Odoo 19 JSON API Controller

Generate JSON request/response handlers with CORS, authentication, and proper error handling following Odoo 19 conventions.

## Instructions

1. **Determine the API structure:**

```python
from odoo import http
from odoo.http import request
import json
```

2. **CORS Setup (if enabled):**

```python
def _set_cors_headers(self, response):
    """Set CORS headers for API responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response
```

3. **Authentication patterns:**

### No Authentication
```python
@http.route('/api/{version}/{resource}', type='json', auth='none', methods=['GET'], csrf=False)
def list_{resource}(self, **kwargs):
    # API logic
    pass
```

### API Key Authentication
```python
def _validate_api_key(self, api_key):
    """Validate API key"""
    api_token = request.env['api.token'].sudo().search([
        ('token', '=', api_key),
        ('active', '=', True)
    ], limit=1)
    return bool(api_token)

@http.route('/api/{version}/{resource}', type='json', auth='none', methods=['POST'], csrf=False)
def create_{resource}(self, api_key=None, **kwargs):
    if not self._validate_api_key(api_key):
        return {'error': 'Invalid API key', 'code': 401}
    # API logic
    pass
```

### JWT Authentication
```python
import jwt

def _validate_jwt(self, token):
    """Validate JWT token"""
    try:
        payload = jwt.decode(token, request.env['ir.config_parameter'].sudo().get_param('api.jwt_secret'), algorithms=['HS256'])
        return payload
    except:
        return None
```

4. **Standard JSON Response:**

```python
def _make_response(self, success=True, data=None, error=None, code=200):
    """Standard JSON response format"""
    response = {
        'success': success,
        'code': code,
    }
    if data is not None:
        response['data'] = data
    if error:
        response['error'] = error
    return response
```

5. **Error Handling:**

```python
try:
    # API logic
    result = self._process_data(kwargs)
    return self._make_response(success=True, data=result)
except ValidationError as e:
    return self._make_response(success=False, error=str(e), code=422)
except Exception as e:
    return self._make_response(success=False, error=str(e), code=500)
```

## Usage Examples

### Basic JSON API (No Auth)

```bash
/controller-json "" products auth="none" cors_enabled="true"
```

Output:
```python
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class ProductAPIController(http.Controller):

    def _set_cors_headers(self, response):
        """Set CORS headers"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    def _make_response(self, success=True, data=None, error=None, code=200):
        """Standard JSON response"""
        response_dict = {
            'success': success,
            'code': code,
        }
        if data is not None:
            response_dict['data'] = data
        if error:
            response_dict['error'] = error
        return response_dict

    @http.route('/api/products', type='http', auth='none', methods=['GET'], csrf=False)
    def list_products(self, limit=20, offset=0, **kwargs):
        """List products with pagination"""
        try:
            products = request.env['product.product'].sudo().search(
                [],
                limit=int(limit),
                offset=int(offset)
            )

            data = [{
                'id': p.id,
                'name': p.name,
                'default_code': p.default_code,
                'list_price': p.list_price,
                'qty_available': p.qty_available,
            } for p in products]

            response = request.make_json_response(
                self._make_response(success=True, data=data)
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)

    @http.route('/api/products/<int:product_id>', type='http', auth='none',
                methods=['GET'], csrf=False)
    def get_product(self, product_id, **kwargs):
        """Get single product"""
        try:
            product = request.env['product.product'].sudo().browse(product_id)
            if not product.exists():
                response = request.make_json_response(
                    self._make_response(success=False, error='Product not found', code=404),
                    status=404
                )
                return self._set_cors_headers(response)

            data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'default_code': product.default_code,
                'list_price': product.list_price,
                'cost_price': product.standard_price,
                'qty_available': product.qty_available,
                'category': product.categ_id.name,
            }

            response = request.make_json_response(
                self._make_response(success=True, data=data)
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)
```

### API Key Authentication with CRUD

```bash
/controller-json v1 partners auth="api_key" cors_enabled="true" rate_limit="100"
```

Output:
```python
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import hashlib

class PartnerAPIController(http.Controller):

    def _validate_api_key(self, api_key):
        """Validate API key and check rate limit"""
        if not api_key:
            return False, 'API key required'

        token = request.env['api.token'].sudo().search([
            ('token', '=', api_key),
            ('active', '=', True)
        ], limit=1)

        if not token:
            return False, 'Invalid API key'

        # Rate limiting
        now = datetime.utcnow()
        rate_limit = int(request.env['ir.config_parameter'].sudo().get_param('api.rate_limit', '100'))

        # Count requests in last minute
        recent_requests = request.env['api.request.log'].sudo().search_count([
            ('token_id', '=', token.id),
            ('create_date', '>=', now - timedelta(minutes=1))
        ])

        if recent_requests >= rate_limit:
            return False, 'Rate limit exceeded'

        # Log request
        request.env['api.request.log'].sudo().create({
            'token_id': token.id,
            'endpoint': request.httprequest.path,
            'method': request.httprequest.method,
        })

        return True, token

    def _make_response(self, success=True, data=None, error=None, code=200):
        """Standard JSON response"""
        response_dict = {
            'success': success,
            'code': code,
            'timestamp': datetime.utcnow().isoformat(),
        }
        if data is not None:
            response_dict['data'] = data
        if error:
            response_dict['error'] = error
        return response_dict

    def _set_cors_headers(self, response):
        """Set CORS headers"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response

    @http.route('/api/v1/partners', type='http', auth='none', methods=['GET'], csrf=False)
    def list_partners(self, api_key=None, limit=20, offset=0, domain=None, **kwargs):
        """List partners"""
        try:
            valid, result = self._validate_api_key(api_key)
            if not valid:
                response = request.make_json_response(
                    self._make_response(success=False, error=result, code=401),
                    status=401
                )
                return self._set_cors_headers(response)

            # Parse domain if provided
            search_domain = []
            if domain:
                try:
                    search_domain = eval(domain)
                except:
                    pass

            partners = request.env['res.partner'].sudo().search(
                search_domain,
                limit=int(limit),
                offset=int(offset)
            )

            data = [{
                'id': p.id,
                'name': p.name,
                'email': p.email,
                'phone': p.phone,
                'is_company': p.is_company,
                'street': p.street,
                'city': p.city,
                'country': p.country_id.name,
            } for p in partners]

            response = request.make_json_response(
                self._make_response(success=True, data=data)
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)

    @http.route('/api/v1/partners', type='http', auth='none', methods=['POST'], csrf=False)
    def create_partner(self, api_key=None, **kwargs):
        """Create partner"""
        try:
            valid, result = self._validate_api_key(api_key)
            if not valid:
                response = request.make_json_response(
                    self._make_response(success=False, error=result, code=401),
                    status=401
                )
                return self._set_cors_headers(response)

            # Parse JSON body
            try:
                data = json.loads(request.httprequest.data)
            except:
                data = kwargs

            # Validate required fields
            if 'name' not in data:
                response = request.make_json_response(
                    self._make_response(success=False, error='Name is required', code=422),
                    status=422
                )
                return self._set_cors_headers(response)

            # Create partner
            partner = request.env['res.partner'].sudo().create({
                'name': data['name'],
                'email': data.get('email'),
                'phone': data.get('phone'),
                'is_company': data.get('is_company', False),
                'street': data.get('street'),
                'city': data.get('city'),
            })

            response_data = {
                'id': partner.id,
                'name': partner.name,
            }

            response = request.make_json_response(
                self._make_response(success=True, data=response_data, code=201),
                status=201
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)
```

### Full CRUD API with Versioning

```bash
/controller-json v2 orders auth="jwt" cors_enabled="true" rate_limit="60"
```

Output:
```python
from odoo import http
from odoo.http import request
import json
import jwt
from datetime import datetime, timedelta

class OrderAPIController(http.Controller):

    def _validate_jwt(self, auth_header):
        """Validate JWT token"""
        if not auth_header or not auth_header.startswith('Bearer '):
            return False, 'Invalid authorization header'

        token = auth_header.split(' ')[1]
        secret = request.env['ir.config_parameter'].sudo().get_param('api.jwt_secret')

        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, 'Token expired'
        except jwt.InvalidTokenError:
            return False, 'Invalid token'

    def _make_response(self, success=True, data=None, error=None, code=200):
        """Standard JSON response"""
        return {
            'success': success,
            'code': code,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'error': error,
        }

    def _set_cors_headers(self, response):
        """Set CORS headers"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    @http.route('/api/v2/orders', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def options_orders(self, **kwargs):
        """Handle OPTIONS preflight request"""
        response = request.make_json_response({})
        return self._set_cors_headers(response)

    @http.route('/api/v2/orders', type='http', auth='none', methods=['GET'], csrf=False)
    def list_orders(self, **kwargs):
        """List orders"""
        try:
            # Validate JWT
            auth_header = request.httprequest.headers.get('Authorization')
            valid, result = self._validate_jwt(auth_header)
            if not valid:
                response = request.make_json_response(
                    self._make_response(success=False, error=result, code=401),
                    status=401
                )
                return self._set_cors_headers(response)

            # Get orders for authenticated user
            user_id = result.get('user_id')
            orders = request.env['sale.order'].sudo().search([
                ('user_id', '=', user_id)
            ])

            data = [{
                'id': o.id,
                'name': o.name,
                'date': o.date_order.isoformat(),
                'amount_total': o.amount_total,
                'state': o.state,
            } for o in orders]

            response = request.make_json_response(
                self._make_response(success=True, data=data)
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)

    @http.route('/api/v2/orders/<int:order_id>', type='http', auth='none',
                methods=['GET'], csrf=False)
    def get_order(self, order_id, **kwargs):
        """Get single order"""
        try:
            auth_header = request.httprequest.headers.get('Authorization')
            valid, result = self._validate_jwt(auth_header)
            if not valid:
                response = request.make_json_response(
                    self._make_response(success=False, error=result, code=401),
                    status=401
                )
                return self._set_cors_headers(response)

            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                response = request.make_json_response(
                    self._make_response(success=False, error='Order not found', code=404),
                    status=404
                )
                return self._set_cors_headers(response)

            data = {
                'id': order.id,
                'name': order.name,
                'date': order.date_order.isoformat(),
                'amount_total': order.amount_total,
                'state': order.state,
                'lines': [{
                    'product': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'subtotal': line.price_subtotal,
                } for line in order.order_line],
            }

            response = request.make_json_response(
                self._make_response(success=True, data=data)
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)

    @http.route('/api/v2/orders', type='http', auth='none', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        """Create order"""
        try:
            auth_header = request.httprequest.headers.get('Authorization')
            valid, result = self._validate_jwt(auth_header)
            if not valid:
                response = request.make_json_response(
                    self._make_response(success=False, error=result, code=401),
                    status=401
                )
                return self._set_cors_headers(response)

            data = json.loads(request.httprequest.data)

            # Create order
            order = request.env['sale.order'].sudo().create({
                'partner_id': data['partner_id'],
                'order_line': data.get('lines', []),
            })

            response = request.make_json_response(
                self._make_response(success=True, data={'id': order.id, 'name': order.name}, code=201),
                status=201
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)

    @http.route('/api/v2/orders/<int:order_id>', type='http', auth='none',
                methods=['DELETE'], csrf=False)
    def delete_order(self, order_id, **kwargs):
        """Delete order"""
        try:
            auth_header = request.httprequest.headers.get('Authorization')
            valid, result = self._validate_jwt(auth_header)
            if not valid:
                response = request.make_json_response(
                    self._make_response(success=False, error=result, code=401),
                    status=401
                )
                return self._set_cors_headers(response)

            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                response = request.make_json_response(
                    self._make_response(success=False, error='Order not found', code=404),
                    status=404
                )
                return self._set_cors_headers(response)

            order.unlink()

            response = request.make_json_response(
                self._make_response(success=True, data={'message': 'Order deleted'})
            )
            return self._set_cors_headers(response)

        except Exception as e:
            response = request.make_json_response(
                self._make_response(success=False, error=str(e), code=500),
                status=500
            )
            return self._set_cors_headers(response)
```

## API Response Formats

### Success Response
```json
{
    "success": true,
    "code": 200,
    "timestamp": "2026-02-15T10:30:00.000Z",
    "data": {
        "id": 1,
        "name": "Example"
    }
}
```

### Error Response
```json
{
    "success": false,
    "code": 400,
    "timestamp": "2026-02-15T10:30:00.000Z",
    "error": "Error message"
}
```

### Validation Error Response
```json
{
    "success": false,
    "code": 422,
    "timestamp": "2026-02-15T10:30:00.000Z",
    "error": "Validation failed",
    "errors": {
        "field_name": "Error message"
    }
}
```

### Paginated Response
```json
{
    "success": true,
    "code": 200,
    "timestamp": "2026-02-15T10:30:00.000Z",
    "data": [...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "total_pages": 5
    }
}
```

## Best Practices

1. **Security:**
   - Always use HTTPS in production
   - Implement proper authentication
   - Validate and sanitize all input
   - Use rate limiting
   - Log API requests for auditing

2. **CORS Configuration:**
   - Specify allowed origins instead of '*'
   - Limit allowed methods
   - Set appropriate cache duration
   - Handle preflight OPTIONS requests

3. **API Design:**
   - Use versioned URLs (/api/v1/, /api/v2/)
   - Use RESTful conventions (GET, POST, PUT, DELETE)
   - Return appropriate HTTP status codes
   - Provide consistent response format

4. **Error Handling:**
   - Return descriptive error messages
   - Use appropriate status codes
   - Log errors for debugging
   - Don't expose sensitive information

5. **Performance:**
   - Implement rate limiting
   - Use pagination for large datasets
   - Cache frequently accessed data
   - Optimize database queries

## HTTP Status Codes for APIs

- `200` - OK (success)
- `201` - Created (new resource)
- `204` - No Content (successful delete)
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication failed)
- `403` - Forbidden (authorization failed)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

## File Structure

```
{module_name}/
├── controllers/
│   ├── __init__.py
│   ├── main.py
│   └── api/
│       ├── __init__.py
│       ├── v1.py
│       └── v2.py
├── models/
│   ├── api_token.py
│   └── api_request_log.py
└── security/
    └── ir.model.access.csv
```

## Next Steps

After creating JSON API controllers:
- `/security-xml` - Add security for API token model
- `/model-new` - Create API token model
- `/automation-cron` - Add cleanup job for old API logs
- `/utils-logging` - Add proper logging for API requests
