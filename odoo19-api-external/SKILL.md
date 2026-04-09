---
description: Create external API integration model with OAuth/API key handling for Odoo 19. Use when user wants to integrate with third-party APIs like Stripe, Mailchimp, or Shopify.
---


# External API Integration Model for Odoo 19

## Overview

This skill creates a complete external API integration model in Odoo 19 with support for multiple authentication methods (OAuth2, API Key, Bearer Token, Basic Auth), webhook handling, and robust error management. The integration provides a clean abstraction layer for communicating with third-party APIs.

## File Structure

```
{module_name}/
├── models/
│   ├── __init__.py
│   └── {api_name}_integration.py
├── controllers/
│   ├── __init__.py
│   └── {api_name}_webhook.py
├── security/
│   └── ir.model.access.csv
├── views/
│   └── {api_name}_integration_views.xml
└── __manifest__.py
```

## Implementation Steps

### 1. Create Base Integration Model

```python
# {module_name}/models/{api_name}_integration.py

import requests
import json
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class {ApiNameCamelCase}Integration(models.Model):
    _name = '{api_name}.integration'
    _description = '{ApiName} API Integration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Basic Fields
    name = fields.Char(string='Name', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Authentication Fields
    auth_method = fields.Selection([
        ('api_key', 'API Key'),
        ('oauth2', 'OAuth 2.0'),
        ('bearer_token', 'Bearer Token'),
        ('basic_auth', 'Basic Authentication'),
    ], string='Authentication Method', required=True, default='api_key')

    # API Key Authentication
    api_key = fields.Char(string='API Key', groups='base.group_system')
    api_secret = fields.Char(string='API Secret', groups='base.group_system')

    # Bearer Token
    bearer_token = fields.Char(string='Bearer Token', groups='base.group_system')

    # Basic Auth
    basic_username = fields.Char(string='Username', groups='base.group_system')
    basic_password = fields.Char(string='Password', groups='base.group_system')

    # OAuth2 Fields
    oauth_client_id = fields.Char(string='OAuth Client ID', groups='base.group_system')
    oauth_client_secret = fields.Char(string='OAuth Client Secret', groups='base.group_system')
    oauth_redirect_uri = fields.Char(string='Redirect URI', groups='base.group_system')
    oauth_access_token = fields.Text(string='Access Token', groups='base.group_system')
    oauth_refresh_token = fields.Text(string='Refresh Token', groups='base.group_system')
    oauth_token_expires = fields.Datetime(string='Token Expires At', groups='base.group_system')
    oauth_scope = fields.Char(string='OAuth Scope', groups='base.group_system')

    # API Configuration
    base_url = fields.Char(string='Base URL', required=True, default='https://api.{api_name}.com')
    api_version = fields.Char(string='API Version', default='v1')
    timeout = fields.Integer(string='Timeout (seconds)', default=30)

    # Webhook Configuration
    webhook_enabled = fields.Boolean(string='Enable Webhooks', default=False)
    webhook_secret = fields.Char(string='Webhook Secret', groups='base.group_system',
                                help='Secret to verify webhook signatures')
    webhook_url = fields.Char(
        string='Webhook URL',
        compute='_compute_webhook_url',
        store=False
    )

    # Logging
    log_requests = fields.Boolean(string='Log Requests', default=True,
                                 help='Log all API requests and responses')
    last_sync_date = fields.Datetime(string='Last Synchronization', readonly=True)
    last_sync_status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('pending', 'Pending'),
    ], string='Last Sync Status', readonly=True)

    # Statistics
    total_requests = fields.Integer(string='Total Requests', readonly=True)
    successful_requests = fields.Integer(string='Successful Requests', readonly=True)
    failed_requests = fields.Integer(string='Failed Requests', readonly=True)

    _sql_constraints = [
        ('name_company_unique', 'UNIQUE(name, company_id)',
         'Integration name must be unique per company!')
    ]

    @api.depends('webhook_enabled')
    def _compute_webhook_url(self):
        """Compute the webhook URL for this integration"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.webhook_enabled:
                record.webhook_url = f'{base_url}/webhook/{api_name}/{record.id}'
            else:
                record.webhook_url = False

    # ==================== AUTHENTICATION METHODS ====================

    def _get_auth_headers(self):
        """Get authentication headers based on auth method"""
        self.ensure_one()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        if self.auth_method == 'api_key':
            headers.update(self._get_api_key_headers())
        elif self.auth_method == 'bearer_token':
            headers['Authorization'] = f'Bearer {self.bearer_token}'
        elif self.auth_method == 'oauth2':
            headers['Authorization'] = f'Bearer {self._get_valid_access_token()}'
        elif self.auth_method == 'basic_auth':
            # Basic auth is handled in requests.auth parameter
            pass

        return headers

    def _get_api_key_headers(self):
        """Get API key authentication headers"""
        self.ensure_one()
        # Common patterns for API key headers
        return {
            'X-API-Key': self.api_key,
            # Alternative patterns (uncomment as needed):
            # 'Authorization': f'Bearer {self.api_key}',
            # 'x-{api_name}-api-key': self.api_key,
        }

    def _get_basic_auth(self):
        """Get basic authentication tuple"""
        self.ensure_one()
        return (self.basic_username, self.basic_password) if self.auth_method == 'basic_auth' else None

    # ==================== OAUTH2 METHODS ====================

    def _get_valid_access_token(self):
        """Get valid access token, refresh if expired"""
        self.ensure_one()

        if self.auth_method != 'oauth2':
            return False

        # Check if token is still valid
        if self.oauth_access_token:
            if not self.oauth_token_expires:
                return self.oauth_access_token

            # Refresh token if expired or will expire in next 5 minutes
            if self.oauth_token_expires > datetime.now() + timedelta(minutes=5):
                return self.oauth_access_token
            else:
                self._refresh_oauth_token()

        return self.oauth_access_token

    def _refresh_oauth_token(self):
        """Refresh OAuth2 access token"""
        self.ensure_one()

        if not self.oauth_refresh_token:
            raise UserError(_('No refresh token available. Please re-authorize.'))

        token_url = f'{self.base_url}/oauth/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.oauth_refresh_token,
            'client_id': self.oauth_client_id,
            'client_secret': self.oauth_client_secret,
        }

        try:
            response = requests.post(token_url, data=data, timeout=self.timeout)
            response.raise_for_status()

            token_data = response.json()
            self.write({
                'oauth_access_token': token_data.get('access_token'),
                'oauth_refresh_token': token_data.get('refresh_token', self.oauth_refresh_token),
                'oauth_token_expires': datetime.now() + timedelta(
                    seconds=token_data.get('expires_in', 3600)
                ),
            })

            _logger.info(f'{api_name} OAuth token refreshed successfully')

        except requests.RequestException as e:
            _logger.error(f'Failed to refresh OAuth token: {str(e)}')
            raise UserError(_('Failed to refresh OAuth token: %s') % str(e))

    def action_get_oauth_authorization_url(self):
        """Generate OAuth authorization URL for user to authorize"""
        self.ensure_one()

        if self.auth_method != 'oauth2':
            raise UserError(_('This integration does not use OAuth2'))

        auth_url = f'{self.base_url}/oauth/authorize'
        params = {
            'response_type': 'code',
            'client_id': self.oauth_client_id,
            'redirect_uri': self.oauth_redirect_uri,
            'scope': self.oauth_scope or 'read write',
            'state': self.id,  # Pass integration ID for callback
        }

        import urllib.parse
        url = f'{auth_url}?{urllib.parse.urlencode(params)}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_handle_oauth_callback(self, code, state):
        """Handle OAuth callback and exchange code for tokens"""
        self.ensure_one()

        token_url = f'{self.base_url}/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.oauth_client_id,
            'client_secret': self.oauth_client_secret,
            'redirect_uri': self.oauth_redirect_uri,
        }

        try:
            response = requests.post(token_url, data=data, timeout=self.timeout)
            response.raise_for_status()

            token_data = response.json()
            self.write({
                'oauth_access_token': token_data.get('access_token'),
                'oauth_refresh_token': token_data.get('refresh_token'),
                'oauth_token_expires': datetime.now() + timedelta(
                    seconds=token_data.get('expires_in', 3600)
                ),
            })

            _logger.info(f'{api_name} OAuth authorization successful')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Successfully authorized!'),
                    'type': 'success',
                }
            }

        except requests.RequestException as e:
            _logger.error(f'OAuth callback failed: {str(e)}')
            raise UserError(_('OAuth authorization failed: %s') % str(e))

    # ==================== API REQUEST METHODS ====================

    def _make_request(self, endpoint, method='GET', data=None, params=None, headers=None):
        """
        Make API request to external service

        Args:
            endpoint: API endpoint path (e.g., '/products', '/orders/123')
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            data: Request body data (dict for JSON)
            params: URL query parameters
            headers: Additional headers (merged with auth headers)

        Returns:
            Response data (dict)

        Raises:
            UserError: If request fails
        """
        self.ensure_one()

        # Build full URL
        url = f'{self.base_url}/{self.api_version}{endpoint}'

        # Prepare headers
        request_headers = self._get_auth_headers()
        if headers:
            request_headers.update(headers)

        # Prepare auth
        auth = self._get_basic_auth()

        # Log request
        if self.log_requests:
            self._log_request(method, endpoint, data)

        try:
            # Make request
            if method in ['GET', 'DELETE']:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    headers=request_headers,
                    auth=auth,
                    timeout=self.timeout
                )
            else:  # POST, PUT, PATCH
                response = requests.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    auth=auth,
                    timeout=self.timeout
                )

            # Handle response
            response.raise_for_status()
            result = response.json() if response.content else {}

            # Update statistics
            self._update_stats(success=True)

            # Log response
            if self.log_requests:
                self._log_response(response.status_code, result)

            return result

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.content else {}
            error_msg = error_data.get('message', str(e))
            _logger.error(f'API request failed: {error_msg}')
            self._update_stats(success=False)
            raise UserError(_('API request failed: %s') % error_msg)

        except requests.exceptions.RequestException as e:
            _logger.error(f'API request error: {str(e)}')
            self._update_stats(success=False)
            raise UserError(_('API connection error: %s') % str(e))

        except json.JSONDecodeError as e:
            _logger.error(f'Invalid JSON response: {str(e)}')
            self._update_stats(success=False)
            raise UserError(_('Invalid response from API server'))

    def _update_stats(self, success=True):
        """Update request statistics"""
        self.ensure_one()
        self.write({
            'total_requests': self.total_requests + 1,
            'successful_requests': self.successful_requests + (1 if success else 0),
            'failed_requests': self.failed_requests + (0 if success else 1),
            'last_sync_date': fields.Datetime.now(),
            'last_sync_status': 'success' if success else 'error',
        })

    def _log_request(self, method, endpoint, data):
        """Log API request"""
        self.env['api.request.log'].sudo().create({
            'integration_id': self.id,
            'request_method': method,
            'request_endpoint': endpoint,
            'request_data': json.dumps(data) if data else False,
            'request_date': fields.Datetime.now(),
        })

    def _log_response(self, status_code, data):
        """Log API response"""
        log = self.env['api.request.log'].sudo().search(
            [('integration_id', '=', self.id)],
            order='request_date desc',
            limit=1
        )
        if log:
            log.write({
                'response_status': status_code,
                'response_data': json.dumps(data) if data else False,
            })

    # ==================== CONVENIENCE METHODS ====================

    def test_connection(self):
        """Test API connection"""
        self.ensure_one()

        try:
            # Try a simple request (adjust endpoint as needed)
            result = self._make_request('/test', method='GET')

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Connection successful!'),
                    'type': 'success',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Connection failed: %s') % str(e),
                    'type': 'danger',
                }
            }

    def action_sync_now(self):
        """Trigger manual synchronization"""
        self.ensure_one()

        try:
            self._sync_data()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Synchronization completed successfully'),
                    'type': 'success',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Synchronization failed: %s') % str(e),
                    'type': 'danger',
                }
            }

    def _sync_data(self):
        """
        Synchronize data from external API
        Override this method to implement custom sync logic
        """
        self.ensure_one()
        # Example: Fetch and process data
        # data = self._make_request('/products', method='GET')
        # self._process_sync_data(data)
        _logger.info(f'{api_name} sync completed')

    def _process_sync_data(self, data):
        """
        Process synchronized data
        Override this method to implement custom data processing
        """
        pass


class ApiRequestLog(models.Model):
    _name = 'api.request.log'
    _description = 'API Request Log'
    _order = 'request_date desc'

    integration_id = fields.Many2one('{api_name}.integration', string='Integration', required=True)
    request_method = fields.Char(string='Method', readonly=True)
    request_endpoint = fields.Char(string='Endpoint', readonly=True)
    request_data = fields.Text(string='Request Data', readonly=True)
    request_date = fields.Datetime(string='Request Date', readonly=True)
    response_status = fields.Integer(string='Response Status', readonly=True)
    response_data = fields.Text(string='Response Data', readonly=True)
```

### 2. Create Webhook Controller (if has_webhook is True)

```python
# {module_name}/controllers/{api_name}_webhook.py

import hmac
import hashlib
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class {ApiNameCamelCase}WebhookController(http.Controller):

    @http.route(
        ['/webhook/{api_name}/<int:integration_id>'],
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
        save_session=False
    )
    def handle_webhook(self, integration_id, **kwargs):
        """
        Handle webhook notifications from {ApiName}

        The webhook receives POST requests with JSON payload
        """
        # Get integration record
        integration = request.env['{api_name}.integration'].sudo().browse(integration_id)

        if not integration.exists():
            _logger.error(f'Webhook received for non-existent integration {integration_id}')
            return {'status': 'error', 'message': 'Integration not found'}

        if not integration.webhook_enabled:
            _logger.warning(f'Webhook received for disabled integration {integration_id}')
            return {'status': 'error', 'message': 'Webhook not enabled'}

        try:
            # Verify webhook signature if secret is configured
            if integration.webhook_secret:
                if not self._verify_webhook_signature(integration):
                    return {'status': 'error', 'message': 'Invalid signature'}

            # Get webhook payload
            payload = request.get_json_data()
            _logger.info(f'Webhook received for {api_name}: {payload}')

            # Process webhook event
            integration._process_webhook_event(payload)

            return {'status': 'success', 'message': 'Webhook processed'}

        except Exception as e:
            _logger.error(f'Error processing webhook: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    def _verify_webhook_signature(self, integration):
        """Verify webhook signature using HMAC"""
        # Get signature from headers
        signature = request.httprequest.headers.get('X-{ApiName}-Signature')
        if not signature:
            signature = request.httprequest.headers.get('X-Hub-Signature-256')

        if not signature:
            return False

        # Calculate expected signature
        payload = request.httprequest.data
        expected_signature = hmac.new(
            integration.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures (timing-safe comparison)
        return hmac.compare_digest(signature, f'sha256={expected_signature}')
```

### 3. Add Webhook Processing Method to Model

```python
# Add to {ApiNameCamelCase}Integration class

def _process_webhook_event(self, payload):
    """
    Process webhook event from external API

    Args:
        payload: Webhook payload data (dict)

    Example payload structure:
    {
        'event': 'order.created',
        'data': {...},
        'timestamp': '2024-01-01T00:00:00Z'
    }
    """
    self.ensure_one()

    event_type = payload.get('event')
    event_data = payload.get('data', {})

    _logger.info(f'Processing webhook event: {event_type}')

    # Route to appropriate handler based on event type
    if event_type == 'order.created':
        self._handle_order_created(event_data)
    elif event_type == 'order.updated':
        self._handle_order_updated(event_data)
    elif event_type == 'product.created':
        self._handle_product_created(event_data)
    # Add more event handlers as needed
    else:
        _logger.warning(f'Unhandled webhook event: {event_type}')

def _handle_order_created(self, data):
    """Handle order.created webhook event"""
    # Example: Create or update order in Odoo
    order_id = data.get('id')
    order = self.env['sale.order'].search([('external_id', '=', order_id)], limit=1)

    if not order:
        self.env['sale.order'].create({
            'external_id': order_id,
            'name': data.get('name'),
            # ... map other fields
        })
        _logger.info(f'Created order {order_id} from webhook')

def _handle_order_updated(self, data):
    """Handle order.updated webhook event"""
    # Similar to _handle_order_created but updates existing record
    pass
```

### 4. Create Views

```xml
<!-- views/{api_name}_integration_views.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Integration Form View -->
    <record id="view_{api_name}_integration_form" model="ir.ui.view">
        <field name="name">{api_name}.integration.form</field>
        <field name="model">{api_name}.integration</field>
        <field name="arch" type="xml">
            <form string="{ApiName} Integration">
                <header>
                    <button name="test_connection" string="Test Connection" type="object" class="btn-primary"/>
                    <button name="action_sync_now" string="Sync Now" type="object" class="btn-secondary"/>
                    <button name="action_get_oauth_authorization_url" string="Authorize OAuth" type="object"
                            attrs="{'invisible': [('auth_method', '!=', 'oauth2')]}" class="btn-link"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Integration Name"/>
                        </h1>
                    </div>

                    <group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="active"/>
                            <field name="sequence"/>
                        </group>
                        <group>
                            <field name="auth_method" widget="radio"/>
                        </group>
                    </group>

                    <notebook>
                        <!-- API Configuration -->
                        <page string="Configuration">
                            <group>
                                <field name="base_url" widget="url"/>
                                <field name="api_version"/>
                                <field name="timeout"/>
                            </group>
                        </page>

                        <!-- Authentication -->
                        <page string="Authentication">
                            <group string="API Key Authentication" attrs="{'invisible': [('auth_method', '!=', 'api_key')]}">
                                <field name="api_key" password="True"/>
                                <field name="api_secret" password="True"/>
                            </group>

                            <group string="Bearer Token" attrs="{'invisible': [('auth_method', '!=', 'bearer_token')]}">
                                <field name="bearer_token" password="True"/>
                            </group>

                            <group string="Basic Authentication" attrs="{'invisible': [('auth_method', '!=', 'basic_auth')]}">
                                <field name="basic_username"/>
                                <field name="basic_password" password="True"/>
                            </group>

                            <group string="OAuth 2.0" attrs="{'invisible': [('auth_method', '!=', 'oauth2')]}">
                                <field name="oauth_client_id"/>
                                <field name="oauth_client_secret" password="True"/>
                                <field name="oauth_redirect_uri"/>
                                <field name="oauth_scope"/>
                                <group>
                                    <field name="oauth_access_token" password="True" readonly="True"/>
                                    <field name="oauth_refresh_token" password="True" readonly="True"/>
                                    <field name="oauth_token_expires" readonly="True"/>
                                </group>
                            </group>
                        </page>

                        <!-- Webhooks -->
                        <page string="Webhooks">
                            <group>
                                <field name="webhook_enabled"/>
                                <field name="webhook_url" widget="url" readonly="True" attrs="{'invisible': [('webhook_enabled', '=', False)]}"/>
                                <field name="webhook_secret" password="True" attrs="{'invisible': [('webhook_enabled', '=', False)]}"/>
                            </group>
                        </page>

                        <!-- Statistics -->
                        <page string="Statistics">
                            <group>
                                <group>
                                    <field name="total_requests" readonly="True"/>
                                    <field name="successful_requests" readonly="True"/>
                                    <field name="failed_requests" readonly="True"/>
                                </group>
                                <group>
                                    <field name="last_sync_date" readonly="True"/>
                                    <field name="last_sync_status" readonly="True"/>
                                </group>
                            </group>
                        </page>

                        <!-- Logs -->
                        <page string="Request Logs">
                            <field name="request_log_ids" readonly="True">
                                <tree>
                                    <field name="request_date"/>
                                    <field name="request_method"/>
                                    <field name="request_endpoint"/>
                                    <field name="response_status"/>
                                </tree>
                            </field>
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

    <!-- Integration Tree View -->
    <record id="view_{api_name}_integration_tree" model="ir.ui.view">
        <field name="name">{api_name}.integration.tree</field>
        <field name="model">{api_name}.integration</field>
        <field name="arch" type="xml">
            <tree string="{ApiName} Integrations">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
                <field name="auth_method"/>
                <field name="active"/>
                <field name="last_sync_date"/>
                <field name="last_sync_status" decoration-success="last_sync_status == 'success'" decoration-danger="last_sync_status == 'error'"/>
            </tree>
        </field>
    </record>

    <!-- Action Window -->
    <record id="action_{api_name}_integration" model="ir.actions.act_window">
        <field name="name">{ApiName} Integrations</field>
        <field name="res_model">{api_name}.integration</field>
        <field name="view_mode">tree,form</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first {ApiName} integration
            </p>
        </field>
    </record>

    <!-- Menu Item -->
    <menuitem id="menu_{api_name}_integration"
              name="{ApiName} Integrations"
              parent="base.menu_custom"
              action="action_{api_name}_integration"
              sequence="10"/>
</odoo>
```

### 5. Update Manifest

```python
# __manifest__.py

{
    'name': '{ApiName} Integration',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Integration with {ApiName} API',
    'author': 'Your Name',
    'depends': ['mail', 'web'],
    'data': [
        'security/{api_name}_integration_security.xml',
        'views/{api_name}_integration_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '{module_name}/static/src/css/{api_name}_integration.css',
        ],
    },
    'installable': True,
    'application': False,
}
```

### 6. Create Security File

```xml
<!-- security/{api_name}_integration_security.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <!-- Access Rights -->
        <record id="group_{api_name}_user" model="res.groups">
            <field name="name">{ApiName} User</field>
            <field name="category_id" ref="base.module_category_extra"/>
        </record>

        <record id="group_{api_name}_manager" model="res.groups">
            <field name="name">{ApiName} Manager</field>
            <field name="category_id" ref="base.module_category_extra"/>
            <field name="implied_ids" eval="[(4, ref('group_{api_name}_user'))]"/>
        </record>
    </data>

    <data noupdate="1">
        <!-- ACL -->
        <record id="{api_name}_integration_user_rule" model="ir.rule">
            <field name="name">{ApiName}: User can see integrations in their company</field>
            <field name="model_id" ref="model_{api_name}_integration"/>
            <field name="domain_force">[('company_id', 'in', company_ids)]</field>
            <field name="groups" eval="[(4, ref('group_{api_name}_user'))]"/>
        </record>
    </data>
</odoo>
```

## Usage Examples

### Example 1: Create Integration with API Key

```python
# Python code or Odoo shell
integration = env['{api_name}.integration'].create({
    'name': 'My {ApiName} Integration',
    'auth_method': 'api_key',
    'api_key': 'your-api-key',
    'api_secret': 'your-api-secret',
    'base_url': 'https://api.{api_name}.com',
    'webhook_enabled': True,
})

# Test connection
integration.test_connection()
```

### Example 2: Make API Request

```python
# GET request
products = integration._make_request('/products', method='GET', params={
    'limit': 50,
    'page': 1
})

# POST request
new_order = integration._make_request('/orders', method='POST', data={
    'customer_id': '12345',
    'items': [
        {'product_id': 'prod_001', 'quantity': 2},
        {'product_id': 'prod_002', 'quantity': 1}
    ]
})
```

### Example 3: OAuth2 Authorization Flow

```python
# Create integration with OAuth2
integration = env['{api_name}.integration'].create({
    'name': 'OAuth Integration',
    'auth_method': 'oauth2',
    'oauth_client_id': 'your-client-id',
    'oauth_client_secret': 'your-client-secret',
    'oauth_redirect_uri': 'https://your-odoo.com/oauth/callback',
    'oauth_scope': 'read write',
})

# This will open OAuth authorization page
integration.action_get_oauth_authorization_url()

# After user approves, handle callback
integration.action_handle_oauth_callback(code='authorization_code', state=integration.id)
```

### Example 4: Sync Data Automatically

```python
# Add automated sync via cron
# Add to __manifest__.py data:
# 'data': ['cron/{api_name}_cron.xml']

<!-- cron/{api_name}_cron.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="ir_cron_{api_name}_sync" model="ir.cron">
            <field name="name">{ApiName} Sync</field>
            <field name="model_id" ref="model_{api_name}_integration"/>
            <field name="state">code</field>
            <field name="code">model._sync_data()</field>
            <field name="interval_number">15</field>
            <field name="interval_type">minutes</field>
            <field name="active">True</field>
        </record>
    </data>
</odoo>
```

### Example 5: Handle Webhook Event

```bash
# Webhook will be called at:
# https://your-odoo.com/webhook/{api_name}/{integration_id}

# Example webhook payload:
curl -X POST https://your-odoo.com/webhook/{api_name}/1 \
  -H "Content-Type: application/json" \
  -H "X-{ApiName}-Signature: sha256=signature" \
  -d '{
    "event": "order.created",
    "data": {
      "id": "order_123",
      "status": "pending"
    },
    "timestamp": "2024-01-01T00:00:00Z"
  }'
```

## Best Practices

1. **Security**
   - Never log sensitive data (API keys, tokens)
   - Use groups='base.group_system' for sensitive fields
   - Encrypt secrets at rest if needed
   - Always verify webhook signatures

2. **Error Handling**
   - Implement retry logic for transient failures
   - Log all API calls for debugging
   - Use proper HTTP status codes
   - Provide user-friendly error messages

3. **Performance**
   - Use timeouts to prevent hanging requests
   - Implement rate limiting to avoid API throttling
   - Cache data when appropriate
   - Use batch operations for bulk updates

4. **OAuth2 Management**
   - Refresh tokens before they expire
   - Handle token refresh failures gracefully
   - Store tokens securely
   - Implement re-authorization flow

5. **Webhooks**
   - Always verify signatures
   - Process webhooks asynchronously if possible
   - Handle duplicate webhook deliveries
   - Return 200 OK immediately, process later

6. **Testing**
   - Test with sandbox/test API endpoints
   - Mock API responses in unit tests
   - Test error scenarios
   - Verify webhook handling

## Testing

```python
# tests/test_{api_name}_integration.py

from odoo.tests import common
from unittest.mock import patch, MagicMock

class Test{ApiNameCamelCase}Integration(common.TransactionCase):

    def setUp(self):
        super(Test{ApiNameCamelCase}Integration, self).setUp()
        self.integration = self.env['{api_name}.integration'].create({
            'name': 'Test Integration',
            'auth_method': 'api_key',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com',
        })

    @patch('requests.request')
    def test_make_request_get(self, mock_request):
        """Test GET request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        result = self.integration._make_request('/test', method='GET')

        self.assertEqual(result, {'data': 'test'})
        mock_request.assert_called_once()

    def test_oauth_token_refresh(self):
        """Test OAuth token refresh"""
        self.integration.auth_method = 'oauth2'
        self.integration.oauth_refresh_token = 'refresh_token'
        self.integration.oauth_token_expires = datetime.now() - timedelta(hours=1)

        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'access_token': 'new_token',
                'refresh_token': 'new_refresh',
                'expires_in': 3600
            }
            mock_post.return_value = mock_response

            token = self.integration._get_valid_access_token()
            self.assertEqual(token, 'new_token')
```

## Summary

This external API integration model provides:
- Multiple authentication methods (API Key, OAuth2, Bearer Token, Basic Auth)
- Automatic OAuth token refresh
- Webhook handling with signature verification
- Request/response logging
- Statistics tracking
- Error handling and retry capabilities
- Company isolation
- Full mail.thread integration

The integration follows Odoo 19 best practices and can be easily extended for any external API service.
