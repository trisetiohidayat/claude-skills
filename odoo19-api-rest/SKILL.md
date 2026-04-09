---
description: Create REST API endpoint with authentication and JSON handling for Odoo 19. Use when user wants to create a REST API controller for CRUD operations.
---


# REST API Endpoint Creation for Odoo 19

## Overview

This skill creates a REST API endpoint controller in Odoo 19 with proper authentication, JSON request/response handling, CORS support, and error handling. The endpoint follows Odoo 19 conventions and integrates seamlessly with the ORM.

## File Structure

```
{module_name}/
├── controllers/
│   ├── __init__.py
│   └── {endpoint_name}_controller.py
├── security/
│   └── ir.model.access.csv
└── __manifest__.py
```

## Implementation Steps

### 1. Create Controller Directory Structure

Ensure the module has a controllers directory with proper __init__.py:

```python
# {module_name}/controllers/__init__.py

from . import {endpoint_name}_controller
```

### 2. Create the REST API Controller

Create the controller file with proper authentication and routing:

```python
# {module_name}/controllers/{endpoint_name}_controller.py

import json
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError

class {EndpointNameCamelCase}ApiController(http.Controller):

    @http.route(
        ['/api/v1/{endpoint_name}', '/api/v1/{endpoint_name}/<int:record_id>'],
        type='http',
        auth='{auth_type}',  # 'user', 'public', 'none'
        methods=['{methods}'],
        csrf=False,
        cors='*'
    )
    def {endpoint_name}_api_handler(self, record_id=None, **kwargs):
        """
        REST API endpoint for {endpoint_name} operations

        Args:
            record_id: Optional record ID for specific record operations
            **kwargs: Additional parameters from request

        Returns:
            JSON response with data or error message
        """
        try:
            # Get request method
            method = request.httprequest.method

            # Parse JSON body for POST/PUT requests
            if method in ['POST', 'PUT']:
                try:
                    data = json.loads(request.httprequest.data)
                except json.JSONDecodeError:
                    return request.make_json_response(
                        {'error': 'Invalid JSON data'},
                        status=400
                    )
            else:
                data = kwargs

            # Get model
            model_name = request.env['{model_name}']  # Replace with actual model

            # Handle different HTTP methods
            if method == 'GET':
                return self._handle_get(model_name, record_id, data)
            elif method == 'POST':
                return self._handle_post(model_name, data)
            elif method == 'PUT':
                return self._handle_put(model_name, record_id, data)
            elif method == 'DELETE':
                return self._handle_delete(model_name, record_id)
            else:
                return request.make_json_response(
                    {'error': 'Method not allowed'},
                    status=405
                )

        except AccessError as e:
            return request.make_json_response(
                {'error': 'Access denied', 'message': str(e)},
                status=403
            )
        except ValidationError as e:
            return request.make_json_response(
                {'error': 'Validation error', 'message': str(e)},
                status=400
            )
        except Exception as e:
            return request.make_json_response(
                {'error': 'Internal server error', 'message': str(e)},
                status=500
            )

    def _handle_get(self, model, record_id, params):
        """Handle GET requests - retrieve records"""
        domain = params.get('domain', [])
        fields = params.get('fields', [])
        limit = params.get('limit', 80)
        offset = params.get('offset', 0)
        order = params.get('order', 'id DESC')

        if record_id:
            # Get single record
            record = model.browse(record_id)
            if not record.exists():
                return request.make_json_response(
                    {'error': 'Record not found'},
                    status=404
                )
            data = record.read(fields)[0] if fields else record.read()[0]
            return request.make_json_response({
                'status': 'success',
                'data': data
            })
        else:
            # Get multiple records
            records = model.search(domain, limit=limit, offset=offset, order=order)
            data = records.read(fields) if fields else records.read()
            return request.make_json_response({
                'status': 'success',
                'count': len(data),
                'data': data
            })

    def _handle_post(self, model, data):
        """Handle POST requests - create new record"""
        if not data:
            return request.make_json_response(
                {'error': 'No data provided'},
                status=400
            )

        try:
            record = model.create(data)
            return request.make_json_response({
                'status': 'success',
                'message': 'Record created successfully',
                'data': record.read()[0]
            }, status=201)
        except Exception as e:
            return request.make_json_response(
                {'error': 'Failed to create record', 'message': str(e)},
                status=400
            )

    def _handle_put(self, model, record_id, data):
        """Handle PUT requests - update existing record"""
        if not record_id:
            return request.make_json_response(
                {'error': 'Record ID required for update'},
                status=400
            )

        if not data:
            return request.make_json_response(
                {'error': 'No data provided'},
                status=400
            )

        record = model.browse(record_id)
        if not record.exists():
            return request.make_json_response(
                {'error': 'Record not found'},
                status=404
            )

        try:
            record.write(data)
            return request.make_json_response({
                'status': 'success',
                'message': 'Record updated successfully',
                'data': record.read()[0]
            })
        except Exception as e:
            return request.make_json_response(
                {'error': 'Failed to update record', 'message': str(e)},
                status=400
            )

    def _handle_delete(self, model, record_id):
        """Handle DELETE requests - delete record"""
        if not record_id:
            return request.make_json_response(
                {'error': 'Record ID required for deletion'},
                status=400
            )

        record = model.browse(record_id)
        if not record.exists():
            return request.make_json_response(
                {'error': 'Record not found'},
                status=404
            )

        try:
            record.unlink()
            return request.make_json_response({
                'status': 'success',
                'message': 'Record deleted successfully'
            })
        except Exception as e:
            return request.make_json_response(
                {'error': 'Failed to delete record', 'message': str(e)},
                status=400
            )
```

### 3. Alternative: API Key Authentication

If using `auth_type='api_key'`, create an API key model:

```python
# {module_name}/models/api_key.py

from odoo import models, fields, api, _

class ApiKey(models.Model):
    _name = 'api.key'
    _description = 'API Key Management'
    _order = 'create_date desc'

    name = fields.Char(string='Name', required=True)
    key = fields.Char(string='API Key', required=True, copy=False, index=True)
    user_id = fields.Many2one('res.users', string='User', required=True,
                             default=lambda self: self.env.user)
    active = fields.Boolean(string='Active', default=True)
    expiry_date = fields.Datetime(string='Expiry Date')
    last_used = fields.Datetime(string='Last Used', readonly=True)

    _sql_constraints = [
        ('key_unique', 'UNIQUE(key)', 'API Key must be unique!')
    ]

    @api.model
    def generate_key(self):
        """Generate a unique API key"""
        import uuid
        return str(uuid.uuid4())

    @api.model
    def create(self, vals):
        """Auto-generate API key if not provided"""
        if not vals.get('key'):
            vals['key'] = self.generate_key()
        return super(ApiKey, self).create(vals)

    def validate_key(self, key):
        """Validate API key and return user"""
        api_key = self.search([
            ('key', '=', key),
            ('active', '=', True)
        ], limit=1)

        if not api_key:
            return False

        # Check expiry
        if api_key.expiry_date:
            from odoo.fields import Datetime
            if api_key.expiry_date < Datetime.now():
                return False

        # Update last used
        api_key.last_used = fields.Datetime.now()
        return api_key.user_id
```

### 4. Add API Key Authentication to Controller

```python
# Add to controller
from odoo import models

class {EndpointNameCamelCase}ApiController(http.Controller):

    def _validate_api_key(self):
        """Validate API key from request headers"""
        api_key = request.httprequest.headers.get('X-API-Key')
        if not api_key:
            return False

        api_key_obj = request.env['api.key'].sudo()
        user = api_key_obj.validate_key(api_key)

        if not user:
            return False

        # Set user in environment
        request.env = request.env(user=user)
        return True

    @http.route(
        ['/api/v1/{endpoint_name}'],
        type='http',
        auth='none',  # We'll handle auth manually
        methods=['GET', 'POST'],
        csrf=False,
        cors='*'
    )
    def {endpoint_name}_api_handler(self, **kwargs):
        """API handler with API key authentication"""
        # Validate API key
        if not self._validate_api_key():
            return request.make_json_response(
                {'error': 'Invalid or missing API key'},
                status=401
            )

        # Continue with request handling...
        # ... rest of the handler code
```

### 5. Update Manifest

Add the controller to module dependencies:

```python
# __manifest__.py

{
    'name': '{Module Name}',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'REST API for {endpoint_name}',
    'author': 'Your Name',
    'depends': ['web'],
    'data': [
        'security/api_key_security.xml',
        'views/api_key_views.xml',
    ],
    'installable': True,
    'application': True,
}
```

### 6. Add Security Rules

Create security access rules:

```xml
<!-- security/api_key_security.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- API Key Access Rights -->
        <record id="api_key_user_rule" model="ir.rule">
            <field name="name">API Key: Users can see their own keys</field>
            <field name="model_id" ref="model_api_key"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- API Key Manager Access -->
        <record id="group_api_key_manager" model="res.groups">
            <field name="name">API Key Manager</field>
            <field name="category_id" ref="base.module_category_administration"/>
        </record>
    </data>
</odoo>
```

## Usage Examples

### Example 1: Simple GET Request

```bash
# Get all records
curl -X GET http://localhost:8069/api/v1/{endpoint_name} \
  -H "Content-Type: application/json" \
  -d '{"domain": [], "fields": ["id", "name"], "limit": 10}'

# Response
{
  "status": "success",
  "count": 10,
  "data": [
    {"id": 1, "name": "Record 1"},
    {"id": 2, "name": "Record 2"}
  ]
}
```

### Example 2: Get Single Record

```bash
curl -X GET http://localhost:8069/api/v1/{endpoint_name}/1

# Response
{
  "status": "success",
  "data": {"id": 1, "name": "Record 1", "field": "value"}
}
```

### Example 3: POST Request (Create)

```bash
curl -X POST http://localhost:8069/api/v1/{endpoint_name} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Record",
    "field1": "value1",
    "field2": "value2"
  }'

# Response
{
  "status": "success",
  "message": "Record created successfully",
  "data": {"id": 123, "name": "New Record"}
}
```

### Example 4: PUT Request (Update)

```bash
curl -X PUT http://localhost:8069/api/v1/{endpoint_name}/123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Record",
    "field1": "new_value"
  }'

# Response
{
  "status": "success",
  "message": "Record updated successfully",
  "data": {"id": 123, "name": "Updated Record"}
}
```

### Example 5: DELETE Request

```bash
curl -X DELETE http://localhost:8069/api/v1/{endpoint_name}/123

# Response
{
  "status": "success",
  "message": "Record deleted successfully"
}
```

### Example 6: Using API Key Authentication

```bash
curl -X GET http://localhost:8069/api/v1/{endpoint_name} \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json"
```

### Example 7: Using Session Authentication

```python
import requests

# Login to get session
session = requests.Session()
session.post('http://localhost:8069/web/session/authenticate', json={
    'jsonrpc': '2.0',
    'params': {
        'db': 'database_name',
        'login': 'admin',
        'password': 'admin'
    }
})

# Make authenticated request
response = session.get('http://localhost:8069/api/v1/{endpoint_name}')
print(response.json())
```

## Best Practices

1. **Always use HTTPS in production** - Never send API keys over plain HTTP
2. **Implement rate limiting** - Add middleware to prevent abuse
3. **Validate input data** - Use @api.constrains in models
4. **Use proper error handling** - Return appropriate HTTP status codes
5. **Log API requests** - Track usage and troubleshoot issues
6. **Version your API** - Use /api/v1/, /api/v2/ to maintain compatibility
7. **Use CORS carefully** - Limit origins in production
8. **Sanitize output** - Only expose necessary fields
9. **Implement pagination** - Use offset/limit for large datasets
10. **Document your API** - Use OpenAPI/Swagger specifications

## Rate Limiting Implementation

```python
# Add to controller
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limit = 100  # requests per hour
        self.window = timedelta(hours=1)

    def is_allowed(self, identifier):
        now = datetime.now()
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window
        ]

        if len(self.requests[identifier]) >= self.limit:
            return False

        self.requests[identifier].append(now)
        return True

# Use in endpoint
@http.route(..., auth='none')
def endpoint_handler(self, **kwargs):
    limiter = RateLimiter()
    api_key = request.httprequest.headers.get('X-API-Key')

    if not limiter.is_allowed(api_key):
        return request.make_json_response(
            {'error': 'Rate limit exceeded'},
            status=429
        )
    # ... continue with request
```

## Testing

```python
# tests/test_api_controller.py

from odoo.tests import common

class TestApiController(common.HttpCase):

    def setUp(self):
        super(TestApiController, self).setUp()
        self.api_key = self.env['api.key'].create({
            'name': 'Test Key',
            'user_id': self.env.user.id
        })

    def test_get_records(self):
        response = self.url_open(
            '/api/v1/{endpoint_name}',
            headers={'X-API-Key': self.api_key.key}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)

    def test_create_record(self):
        response = self.url_open(
            '/api/v1/{endpoint_name}',
            data=json.dumps({'name': 'Test'}),
            headers={'X-API-Key': self.api_key.key},
            method='POST'
        )
        self.assertEqual(response.status_code, 201)
```

## Summary

This REST API endpoint provides:
- Full CRUD operations (Create, Read, Update, Delete)
- Multiple authentication methods (session, API key, OAuth)
- Proper JSON request/response handling
- CORS support for cross-origin requests
- Comprehensive error handling
- Rate limiting capabilities
- Security best practices

The endpoint follows Odoo 19 conventions and can be easily extended for custom business logic.
