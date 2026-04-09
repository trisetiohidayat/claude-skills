---
name: odoo-api
description: Create external API endpoint/controller in Odoo. Odoo 17/18/19 compatible. Use when user asks to "create API", "add endpoint", "create controller", "add HTTP route", or "external integration"
---

# Odoo External API (Controller) Guide

You are helping the user create an external API endpoint in Odoo.

## Steps

1. **Parse input**:
   - Endpoint name (e.g., "custom.api")
   - HTTP path (e.g., "/api/custom/endpoint")
   - HTTP method: GET, POST, PUT, DELETE
   - Model: What Odoo model to interface with
   - Operation: What the endpoint should do
   - Authentication: public, api_key, user_token, oauth
   - Odoo version (default: from project CLAUDE.md)

2. **Determine module location**:
   - Find the custom module to add controller to
   - Create controllers/ directory if not exists

3. **Create controller**:

   ```python
   # -*- coding: utf-8 -*-
   from odoo import http
   from odoo.http import request

   import json
   import logging
   import secrets

   _logger = logging.getLogger(__name__)


   class CustomAPI(http.Controller):
       """Custom API Controller for external integrations"""

       # ============================================================
       # Health Check Endpoint
       # ============================================================

       @http.route('/api/health', type='json', auth='public', methods=['GET'], csrf=False)
       def health_check(self, **kwargs):
           """Health check endpoint for monitoring"""
           return {
               'status': 'healthy',
               'service': 'odoo-api',
               'version': '1.0',
           }

       # ============================================================
       # GET Endpoints - Read Data
       # ============================================================

       @http.route([
           '/api/v1/records',
           '/api/v1/records/<int:record_id>',
       ], type='json', auth='api_key', methods=['GET'], csrf=False)
       def get_records(self, record_id=None, limit=100, offset=0, **kwargs):
           """
           Get records from the model.

           Query params:
               limit: Maximum records to return (default: 100, max: 1000)
               offset: Starting position (default: 0)
               domain: JSON-encoded domain filter

           Headers:
               X-API-KEY: Your API key

           Returns:
               List of records or single record
           """
           # Validate API key
           if not self._validate_api_key():
               return {'error': 'Invalid API key', 'code': 401}

           try:
               Model = request.env['custom.model'].sudo()

               # Parse domain if provided
               domain = []
               if kwargs.get('domain'):
                   domain = json.loads(kwargs['domain'])

               # Build query
               if record_id:
                   records = Model.search([
                       ('id', '=', record_id)
                   ] + domain, limit=1)
               else:
                   records = Model.search(
                       domain,
                       limit=min(int(limit), 1000),
                       offset=int(offset)
                   )

               # Serialize records
               data = [self._serialize_record(r) for r in records]

               return {
                   'status': 'success',
                   'count': len(data),
                   'data': data,
               }

           except Exception as e:
               _logger.error(f"API Error: {str(e)}")
               return {'error': str(e), 'code': 500}

       # ============================================================
       # POST Endpoint - Create Data
       # ============================================================

       @http.route('/api/v1/records', type='json', auth='api_key',
                   methods=['POST'], csrf=False)
       def create_record(self, **kwargs):
           """
           Create a new record.

           Body (JSON):
               {
                   "name": "Record Name",
                   "partner_id": 123,
                   "value": 1000
               }

           Returns:
               Created record with ID
           """
           try:
               data = request.jsonrequest or {}

               # Validate required fields
               required_fields = ['name']
               for field in required_fields:
                   if field not in data:
                       return {
                           'error': f'Missing required field: {field}',
                           'code': 400
                       }

               # Prepare record data
               record_data = {
                   k: v for k, v in data.items()
                   if k in ['name', 'partner_id', 'value', 'date']
               }

               # Create record
               Model = request.env['custom.model'].sudo()
               record = Model.create(record_data)

               return {
                   'status': 'created',
                   'id': record.id,
                   'data': self._serialize_record(record),
               }, 201

           except Exception as e:
               _logger.error(f"Create Error: {str(e)}")
               return {'error': str(e), 'code': 500}

       # ============================================================
       # PUT Endpoint - Update Data
       # ============================================================

       @http.route('/api/v1/records/<int:record_id>', type='json',
                   auth='api_key', methods=['PUT'], csrf=False)
       def update_record(self, record_id, **kwargs):
           """
           Update an existing record.

           Body (JSON):
               {
                   "name": "Updated Name",
                   "value": 2000
               }

           Returns:
               Updated record
           """
           try:
               Model = request.env['custom.model'].sudo()
               record = Model.search([('id', '=', record_id)], limit=1)

               if not record:
                   return {'error': 'Record not found', 'code': 404}

               data = request.jsonrequest or {}
               record.write(data)

               return {
                   'status': 'updated',
                   'data': self._serialize_record(record),
               }

           except Exception as e:
               _logger.error(f"Update Error: {str(e)}")
               return {'error': str(e), 'code': 500}

       # ============================================================
       # DELETE Endpoint - Delete Data
       # ============================================================

       @http.route('/api/v1/records/<int:record_id>', type='json',
                   auth='api_key', methods=['DELETE'], csrf=False)
       def delete_record(self, record_id, **kwargs):
           """
           Delete a record.

           Returns:
               Success message
           """
           try:
               Model = request.env['custom.model'].sudo()
               record = Model.search([('id', '=', record_id)], limit=1)

               if not record:
                   return {'error': 'Record not found', 'code': 404}

               record.unlink()

               return {
                   'status': 'deleted',
                   'id': record_id,
               }

           except Exception as e:
               _logger.error(f"Delete Error: {str(e)}")
               return {'error': str(e), 'code': 500}

       # ============================================================
       # Helper Methods
       # ============================================================

       def _validate_api_key(self):
           """Validate API key from header"""
           api_key = request.httprequest.headers.get('X-API-KEY')

           if not api_key:
               return False

           # Check against stored keys
           key_model = request.env['api.key'].sudo()
           key = key_model.search([
               ('key', '=', api_key),
               ('active', '=', True),
           ], limit=1)

           return bool(key)

       def _serialize_record(self, record):
           """Convert record to dictionary"""
           return {
               'id': record.id,
               'name': record.name,
               'partner_id': record.partner_id.id if record.partner_id else None,
               'partner_name': record.partner_id.name if record.partner_id else None,
               'value': record.value,
               'state': record.state,
               'create_date': record.create_date.isoformat() if record.create_date else None,
               'write_date': record.write_date.isoformat() if record.write_date else None,
           }

       def _log_request(self):
           """Log incoming request for auditing"""
           _logger.info(
               f"API Request: {request.httprequest.method} "
               f"{request.httprequest.path} "
               f"from {request.httprequest.remote_addr}"
           )
   ```

4. **Create API Key Model** (for key management):

   ```python
   # models/api_key.py
   from odoo import models, fields, api

   class APIKey(models.Model):
       _name = 'api.key'
       _description = 'API Key'

       name = fields.Char(string='Name', required=True)
       key = fields.Char(string='API Key', required=True, copy=False)
       user_id = fields.Many2one('res.users', string='User',
                               default=lambda self: self.env.user)
       active = fields.Boolean(string='Active', default=True)
       access_count = fields.Integer(string='Access Count', default=0)
       last_access = fields.Datetime(string='Last Access')

       @api.model
       def generate_key(self):
           """Generate a new API key"""
           return secrets.token_urlsafe(32)
   ```

5. **Update __manifest__.py**:

   ```python
   "data": [
       "security/ir.model.access.csv",
       "controllers/controllers.xml",
   ],
   ```

6. **Create controllers/__init__.py**:

   ```python
   from . import main
   ```

7. **Update module __init__.py**:

   ```python
   from . import controllers
   from . import models
   ```

## Authentication Methods

| Method | Use Case | Implementation |
|--------|----------|---------------|
| `auth='public'` | Public APIs | No auth needed |
| `auth='user'` | User session | Requires valid Odoo session |
| `auth='api_key'` | API keys | Custom key validation |
| `auth='none'` | Internal only | No auth check |

## Best Practices

```python
# Always use csrf=False for external APIs
@http.route('/api/endpoint', type='json', auth='api_key', csrf=False)

# Always handle exceptions
try:
    # API logic
except Exception as e:
    return {'error': str(e), 'code': 500}

# Log all requests for auditing
_logger.info(f"API: {method} {path} from {ip}")

# Validate input
if not data.get('required_field'):
    return {'error': 'Missing field'}, 400

# Use sudo() only when necessary and secure
Model = request.env['model'].sudo()  # For external APIs

# Return proper HTTP status codes
return {'data': result}, 201  # Created
return {'error': 'Not found'}, 404
return {'error': 'Server error'}, 500
```

## Important Notes

- Always use `csrf=False` for external APIs
- Validate all input data before processing
- Return proper HTTP status codes: 200, 201, 400, 401, 404, 500
- Use `request.make_json_response()` for JSON responses
- Handle exceptions gracefully
- Log API calls for auditing
- Add rate limiting for public APIs
- Document API endpoints
- Test all endpoints thoroughly
