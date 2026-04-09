---
name: odoo-integration-analysis
description: |
  Analisis integrasi Odoo dengan sistem eksternal - REST API, XML-RPC, webhooks, EDI, payment gateways,
  shipping providers, CRM integration. Gunakan ketika:
  - User bertanya tentang integrasi dengan sistem lain
  - Ingin build API untuk Odoo
  - Need to connect dengan third-party services
  - Ingin understand external API patterns
---

# Odoo Integration Analysis Skill

## Overview

Skill ini membantu menganalisis dan membangun integrasi Odoo dengan sistem eksternal. Integrasi merupakan aspek kritis dalam implementasi Odoo enterprise, memungkinkan pertukaran data dengan berbagai layanan pihak ketiga seperti payment gateways, shipping providers, CRM, ERP lain, e-commerce platforms, dan masih banyak lagi. Kemampuan untuk menganalisis dan mengimplementasikan integrasi dengan benar adalah kompetensi penting bagi setiap developer Odoo.

Integrasi Odoo dapat dilakukan melalui berbagai mekanisme, masing-masing dengan kelebihan dan kekurangan tertentu. Pemahaman mendalam tentang berbagai pendekatan ini memungkinkan developer memilih solusi yang paling sesuai dengan kebutuhan spesifik proyek. Beberapa faktor yang perlu dipertimbangkan dalam memilih mekanisme integrasi meliputi: jenis data yang akan dipertukarkan, frekuensi pertukaran data, kebutuhan real-time vs batch processing, keamanan, dan kompleksitas implementasi.

Dalam konteks Odoo 19, tersedia berbagai fitur dan peningkatan yang mendukung integrasi. Odoo 19 memperkenalkan beberapa perubahan API dan peningkatan keamanan yang perlu dipahami untuk membangun integrasi yang robust dan aman. Skill ini akan memandu Anda melalui proses analisis integrasi secara sistematis, mulai dari pemilihan protokol hingga implementasi dan dokumentasi.

## Step 1: Analyze API Options

### 1.1 REST API dengan http.Controller

REST API merupakan pilihan paling populer untuk integrasi modern dengan Odoo. Menggunakan http.Controller, developer dapat mendefinisikan endpoint-endpoint yang dapat diakses oleh sistem eksternal. Pendekatan ini sangat cocok untuk aplikasi web modern, mobile apps, dan sistem yang menggunakan format JSON untuk pertukaran data.

Untuk membangun REST API di Odoo, pertama-tama perlu dipahami struktur dasar http.Controller. Controller di Odoo mewarisi dari kelas `odoo.http.Controller` dan mendefinisikan method-method yang akan menangani request HTTP. Setiap method dalam controller dapat di-dekorasi dengan `@http.route` untuk mendefinisikan URL endpoint, metode HTTP yang diizinkan (GET, POST, PUT, DELETE), dan berbagai parameter konfigurasi lainnya.

Contoh sederhana REST API controller di Odoo 19:

```python
from odoo import http
from odoo.http import request

class VendorAPI(http.Controller):

    @http.route('/api/vendors', type='json', auth='public', methods=['GET'])
    def get_vendors(self, limit=100, offset=0):
        """Get list of vendors"""
        vendors = request.env['res.partner'].search_read(
            [('supplier_rank', '>', 0)],
            fields=['id', 'name', 'email', 'phone'],
            limit=limit,
            offset=offset
        )
        return {'vendors': vendors, 'count': len(vendors)}

    @http.route('/api/vendors/<int:vendor_id>', type='json', auth='public', methods=['GET'])
    def get_vendor(self, vendor_id):
        """Get single vendor details"""
        vendor = request.env['res.partner'].browse(vendor_id)
        if not vendor.exists():
            return {'error': 'Vendor not found'}, 404
        return {
            'id': vendor.id,
            'name': vendor.name,
            'email': vendor.email,
            'phone': vendor.phone,
            'street': vendor.street,
            'city': vendor.city,
            'country_id': vendor.country_id.code if vendor.country_id else None,
        }

    @http.route('/api/vendors', type='json', auth='api_key', methods=['POST'])
    def create_vendor(self, name, email, phone=None, street=None, city=None, country_code=None):
        """Create new vendor"""
        # Validate required fields
        if not name or not email:
            return {'error': 'Name and email are required'}, 400

        # Check for duplicate email
        existing = request.env['res.partner'].search([('email', '=', email)])
        if existing:
            return {'error': 'Vendor with this email already exists'}, 409

        # Get country if provided
        country_id = None
        if country_code:
            country = request.env['res.country'].search([('code', '=', country_code)])
            country_id = country.id if country else None

        # Create vendor
        vendor = request.env['res.partner'].create({
            'name': name,
            'email': email,
            'phone': phone,
            'street': street,
            'city': city,
            'country_id': country_id,
            'supplier_rank': 1,
        })

        return {'id': vendor.id, 'name': vendor.name}, 201

    @http.route('/api/vendors/<int:vendor_id>', type='json', auth='api_key', methods=['PUT'])
    def update_vendor(self, vendor_id, **kwargs):
        """Update vendor"""
        vendor = request.env['res.partner'].browse(vendor_id)
        if not vendor.exists():
            return {'error': 'Vendor not found'}, 404

        # Filter allowed fields
        allowed_fields = ['name', 'email', 'phone', 'street', 'city', 'country_id']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        vendor.write(update_data)
        return {'id': vendor.id, 'name': vendor.name}
```

Beberapa poin penting yang perlu diperhatikan dalam implementasi REST API:

1. **Authentication**: Odoo menyediakan beberapa mode autentikasi untuk HTTP routes. Mode `auth` dapat diatur ke `none` (tanpa autentikasi), `public` (pengguna publik), `user` (pengguna yang login), atau `api_key` (menggunakan API key khusus).

2. **Response Type**: Parameter `type` menentukan format response. Nilai `json` otomatis menserialisasi return value menjadi JSON, sementara `http` mengembalikan response sesuai format yang di-set di controller.

3. **Error Handling**: Selalu handle exception dan return format yang konsisten. Disarankan menggunakan tuple `(response, status_code)` untuk menunjukkan error.

### 1.2 XML-RPC Integration

XML-RPC merupakan protokol yang lebih lama namun masih广泛 digunakan, terutama untuk integrasi dengan sistem legacy. Odoo menyediakan library XML-RPC untuk berbagai bahasa pemrograman, menjadikannya pilihan yang baik untuk integrasi dengan sistem yang sudah ada.

Keunggulan XML-RPC adalah kompatibilitas luas - dapat digunakan dari hampir semua bahasa pemrograman modern. Namun, XML-RPC memiliki beberapa keterbatasan dibandingkan REST: format XML lebih besar dari JSON, performa sedikit lebih lambat, dan tidak sekuat REST dalam hal representasi data yang kompleks.

Implementasi XML-RPC di sisi client (contoh menggunakan Python):

```python
import xmlrpc.client

# Koneksi ke Odoo
url = 'http://localhost:8069'
db = 'roedl'
username = 'admin'
password = 'admin'

# Common endpoint
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

# Object endpoint untuk operasi ORM
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Contoh: Search
vendor_ids = models.execute_kw(
    db, uid, password,
    'res.partner',
    'search',
    [[['supplier_rank', '>', 0]]],
    {'limit': 100}
)

# Contoh: Read
vendors = models.execute_kw(
    db, uid, password,
    'res.partner',
    'read',
    [vendor_ids],
    {'fields': ['name', 'email', 'phone']}
)

# Contoh: Create
new_vendor_id = models.execute_kw(
    db, uid, password,
    'res.partner',
    'create',
    [{
        'name': 'New Vendor',
        'email': 'vendor@example.com',
        'supplier_rank': 1,
    }]
)

# Contoh: Write
models.execute_kw(
    db, uid, password,
    'res.partner',
    'write',
    [[new_vendor_id], {'phone': '+1234567890'}]
)

# Contoh: Delete
models.execute_kw(
    db, uid, password,
    'res.partner',
    'unlink',
    [[new_vendor_id]]
)
```

XML-RPC juga dapat digunakan untuk memanggil method kustom:

```python
# Call custom method
result = models.execute_kw(
    db, uid, password,
    'res.partner',
    'method_name',
    [arg1, arg2],  # Arguments
    {}  # Keyword arguments
)
```

### 1.3 JSON-RPC

JSON-RPC adalah alternatif modern untuk XML-RPC yang menggunakan format JSON. Ini menggabungkan kemudahan format JSON dengan kesederhanaan protokol RPC. Odoo mendukung JSON-RPC baik untuk web maupun mobile apps.

Implementasi JSON-RPC dari sisi client:

```python
import json
import requests

url = 'http://localhost:8069/jsonrpc'

# Login
payload = {
    'jsonrpc': '2.0',
    'method': 'call',
    'params': {
        'service': 'common',
        'method': 'authenticate',
        'args': ['roedl', 'admin', 'admin', {}]
    },
    'id': 1
}

response = requests.post(url, json=payload)
result = response.json()
uid = result.get('result')

# Execute ORM operations
def call_kw(model, method, args, kwargs=None):
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': 'object',
            'method': 'execute_kw',
            'args': [
                'roedl', uid, 'admin',
                model,
                method,
                args,
                kwargs or {}
            ]
        },
        'id': 2
    }
    response = requests.post(url, json=payload)
    return response.json().get('result')

# Search
vendor_ids = call_kw('res.partner', 'search', [[['supplier_rank', '>', 0]]])

# Read
vendors = call_kw('res.partner', 'read', [vendor_ids[:10], ['name', 'email']])
```

### 1.4 Webhooks

Webhooks merupakan mekanisme di mana Odoo dapat dikirimkan notifikasi ke sistem eksternal saat event tertentu terjadi. Berbeda dengan polling (di mana client berulang kali memeriksa data), webhooks mendorong data ke client saat ada perubahan.

Implementasi webhook di Odoo dapat menggunakan external API atau server actions. Berikut contoh sederhana menggunakan server action dan webhook:

```python
# webhook_handler.py - Module untuk menangani outgoing webhooks
from odoo import models, api
import requests
import logging

_logger = logging.getLogger(__name__)

class WebhookMixin(models.AbstractModel):
    """Mixin untuk menambahkan functionality webhook ke model manapun"""

    _name = 'webhook.mixin'
    _description = 'Webhook Mixin'

    def _send_webhook(self, webhook_url, event_type, payload):
        """Send webhook notification"""
        if not webhook_url:
            return

        try:
            response = requests.post(
                webhook_url,
                json={
                    'event': event_type,
                    'model': self._name,
                    'record_id': self.id,
                    'data': payload,
                },
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            _logger.info(f'Webhook sent successfully: {event_type}')
        except requests.RequestException as e:
            _logger.error(f'Failed to send webhook: {e}')

    def _get_webhook_payload(self):
        """Override this method untuk customize payload"""
        return {
            'id': self.id,
            'name': self.name,
        }
```

## Step 2: Analyze Authentication

### 2.1 API Keys

API keys adalah mekanisme autentikasi yang aman dan mudah digunakan untuk integrasi. Odoo 16+ mendukung API keys secara native, yang memungkinkan user membuat key khusus untuk akses API tanpa perlu membagikan password.

Implementasi autentikasi API key di controller:

```python
from odoo.http import request
from odoo.exceptions import AccessError

class SecureAPIController(http.Controller):

    @http.route('/api/secure/data', type='json', auth='api_key')
    def get_secure_data(self):
        """Endpoint yang dilindungi dengan API key"""
        # request.env.user akan berisi user yang terkait dengan API key
        current_user = request.env.user
        return {
            'user': current_user.name,
            'company': current_user.company_id.name,
            'data': 'Sensitive data here'
        }

    @http.route('/api/secure/partner/create', type='json', auth='api_key')
    def create_partner_with_api_key(self, name, email, **kwargs):
        """Buat partner dengan API key authentication"""
        # Dapatkan user dari API key
        user = request.env.user

        # Check specific permission
        if not user.has_group('base.group_partner_manager'):
            return {'error': 'Insufficient permissions'}, 403

        partner = request.env['res.partner'].create({
            'name': name,
            'email': email,
            **kwargs
        })

        return {'id': partner.id}
```

Membuat API key melalui Odoo UI:
1. Buka Settings > Users & Companies > Users
2. Pilih user yang ingin dibuatkan API key
3. Klik tab "API Keys"
4. Klik "New API Key"
5. Masukkan nama deskriptif dan simpan

### 2.2 OAuth2

OAuth2 adalah protokol autentikasi yang lebih kompleks namun sangat fleksibel, cocok untuk integrasi dengan platform besar seperti Google, Microsoft, atau layanan lain yang mendukung OAuth2.

Odoo dapat dikonfigurasi sebagai OAuth2 provider atau consumer. Untuk menggunakan OAuth2 sebagai autentikasi API:

```python
# Konfigurasi OAuth2 di Odoo
# Pertama, install module auth_oauth

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    oauth_provider_enabled = fields.Boolean(
        string='Enable OAuth2 Provider',
        config_parameter='auth_oauth.enabled'
    )
    oauth_provider_client_id = fields.Char(
        string='OAuth2 Client ID',
        config_parameter='auth_oauth.client_id'
    )
    oauth_provider_client_secret = fields.Char(
        string='OAuth2 Client Secret',
        config_parameter='auth_oauth.client_secret'
    )
```

### 2.3 Token-Based Authentication

Untuk sistem yang lebih sederhana, token-based authentication dapat diimplementasikan dengan membuat model token:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import secrets
import hashlib
from datetime import datetime, timedelta

class APIAccessToken(models.Model):
    """Model untuk menyimpan access tokens"""
    _name = 'api.access.token'
    _description = 'API Access Token'

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', required=True)
    token = fields.Char(required=True, index=True)
    token_hash = fields.Char(required=True, index=True)
    expires_at = fields.Datetime()
    active = fields.Boolean(default=True)

    @api.model
    def generate_token(self, user_id, name, expiry_days=365):
        """Generate new API token"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        expires_at = datetime.now() + timedelta(days=expiry_days)

        record = self.create({
            'name': name,
            'user_id': user_id,
            'token': token,  # Store plain token untuk display sekali saja
            'token_hash': token_hash,
            'expires_at': fields.Datetime.to_string(expires_at),
        })

        return token, record

    @api.model
    def validate_token(self, token):
        """Validate token dan return user jika valid"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        token_record = self.search([
            ('token_hash', '=', token_hash),
            ('active', '=', True),
        ])

        if not token_record:
            return False

        if token_record.expires_at and fields.Datetime.from_string(token_record.expires_at) < datetime.now():
            return False

        return token_record.user_id
```

### 2.4 Basic Authentication

Basic Auth dapat digunakan untuk endpoint tertentu, meskipun kurang aman dibanding metode lain:

```python
from odoo.http import request
import base64

class BasicAuthController(http.Controller):

    @http.route('/api/basic/test', type='json', auth='none')
    def test_basic_auth(self):
        """Contoh penggunaan basic auth"""
        # Get Authorization header
        auth_header = request.httprequest.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Basic '):
            return {'error': 'Authentication required'}, 401

        # Decode credentials
        try:
            encoded = auth_header[6:]  # Remove 'Basic '
            decoded = base64.b64decode(encoded).decode('utf-8')
            username, password = decoded.split(':', 1)
        except Exception:
            return {'error': 'Invalid authentication format'}, 401

        # Validate credentials
        user = request.env['res.users'].sudo().search([('login', '=', username)])
        if not user:
            return {'error': 'Invalid credentials'}, 401

        # Check password (gunakan method validate_password dari user)
        if not user._validate_password(password):
            return {'error': 'Invalid credentials'}, 401

        return {'user': username, 'message': 'Authentication successful'}
```

## Step 3: Analyze Integration Patterns

### 3.1 Push vs Pull Patterns

Dalam desain integrasi, terdapat dua pola utama: push (proaktif) dan pull (reaktif). Pilihan antara keduanya bergantung pada kebutuhan spesifik sistem.

**Push Pattern**:
- Odoo mengirim data ke sistem eksternal saat event terjadi
- Cocok untuk: notifikasi real-time, webhook, trigger-based updates
- Keunggulan: respons cepat, mengurangi beban di sistem target
- Tantangan: perlu manage retry logic, handle unreachable systems

```python
# Contoh Push Pattern dengan scheduled action
class SaleOrderPush(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super().action_confirm()
        # Push order ke external system
        self._push_to_erp()
        return result

    def _push_to_erp(self):
        """Push order data ke external ERP"""
        for order in self:
            try:
                # Prepare payload
                payload = {
                    'order_number': order.name,
                    'customer': {
                        'name': order.partner_id.name,
                        'email': order.partner_id.email,
                        'code': order.partner_id.ref,
                    },
                    'lines': [{
                        'product': line.product_id.default_code,
                        'quantity': line.product_uom_qty,
                        'price': line.price_unit,
                    } for line in order.order_line],
                    'total': order.amount_total,
                }

                # Send to external system
                response = requests.post(
                    f'{self.env.company.external_erp_url}/api/orders',
                    json=payload,
                    headers={
                        'Authorization': f'Bearer {self.env.company.external_erp_token}',
                        'Content-Type': 'application/json',
                    },
                    timeout=30
                )
                response.raise_for_status()

                # Store external reference
                order.write({'external_id': response.json().get('id')})

            except requests.RequestException as e:
                # Log error dan schedule retry
                order.message_post(
                    body=f'Failed to push order: {str(e)}',
                    message_type='notification'
                )
```

**Pull Pattern**:
- Sistem eksternal secara periodik mengambil data dari Odoo
- Cocok untuk: batch processing, data warehouse, reporting
- Keunggulan: lebih sederhana, tidak perlu manage push infrastructure
- Tantangan: data tidak real-time, perlu scheduling yang tepat

```python
# Contoh Pull Pattern dengan scheduled action
class ExternalDataPull(models.Model):
    _name = 'external.data.pull'
    _description = 'External Data Pull Configuration'

    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', required=True)
    external_url = fields.Char(required=True)
    external_api_key = fields.Char()
    last_sync = fields.Datetime()
    sync_interval = fields.Integer(default=60)  # minutes

    def run_sync(self):
        """Pull data dari external system"""
        for config in self:
            try:
                # Fetch data dari external system
                response = requests.get(
                    f'{config.external_url}/api/data',
                    headers={
                        'Authorization': f'Bearer {config.external_api_key}',
                    },
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()

                # Process data
                model = self.env[config.model_id.model]
                for item in data.get('items', []):
                    # Find existing record atau create new
                    existing = model.search([('external_id', '=', item['id'])])
                    if existing:
                        existing.write(item)
                    else:
                        model.create(item)

                # Update last sync
                config.write({'last_sync': fields.Datetime.now()})

            except Exception as e:
                _logger.error(f'Sync failed: {e}')
```

### 3.2 Real-time vs Batch Processing

Pemilihan antara real-time dan batch processing sangat bergantung pada use case:

| Aspek | Real-time | Batch |
|-------|-----------|-------|
| Response time | Immediate | Delayed |
| Data volume | Low-medium | High |
| Complexity | Higher | Lower |
| Resource usage | Continuous | Periodic |
| Use case | Transactions, notifications | Reporting, analytics |

**Real-time Integration**:
```python
class PaymentGatewayController(http.Controller):

    @http.route('/payment/webhook', type='json', auth='none', csrf=False)
    def payment_webhook(self):
        """Handle real-time payment notifications"""
        data = request.jsonrequest

        # Verify webhook signature
        if not self._verify_signature(data):
            return {'error': 'Invalid signature'}, 400

        # Process payment notification
        transaction_ref = data.get('reference')
        payment_status = data.get('status')

        transaction = request.env['payment.transaction'].search([
            ('reference', '=', transaction_ref)
        ])

        if transaction:
            if payment_status == 'completed':
                transaction._set_done()
                # Trigger additional real-time actions
                transaction._post_process()
            elif payment_status == 'failed':
                transaction._set_error(data.get('error_message'))

        return {'status': 'ok'}
```

**Batch Processing**:
```python
class BatchSyncScheduler(models.Model):
    _name = 'batch.sync.scheduler'
    _description = 'Batch Sync Scheduler'

    name = fields.Char()
    model_id = fields.Many2one('ir.model')
    external_system = fields.Char()
    batch_size = fields.Integer(default=100)

    def run_batch_sync(self):
        """Run batch synchronization"""
        model = self.env[self.model_id.model]

        # Get records yang perlu disinkronkan
        domain = self._get_sync_domain()
        record_ids = model.search(domain, order='id', limit=self.batch_size)

        for record in record_ids:
            try:
                self._sync_record(record)
                record.write({'last_sync': fields.Datetime.now()})
            except Exception as e:
                _logger.error(f'Failed to sync record {record.id}: {e}')

        # Schedule next batch jika masih ada data
        if len(record_ids) == self.batch_size:
            self.env['ir.cron'].create({
                'name': f'Batch Sync - {self.name}',
                'model_id': self.id,
                'state': 'code',
                'code': 'model.run_batch_sync()',
                'interval_number': 5,
                'interval_type': 'minutes',
            })
```

### 3.3 Webhook Handlers

Webhook handler yang robust memerlukan penanganan error yang baik, retry logic, dan security:

```python
import hashlib
import hmac
import json
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class WebhookHandler(http.Controller):

    def _verify_webhook_signature(self, payload, signature, secret):
        """Verify webhook signature untuk keamanan"""
        if not signature:
            return False

        # Compute expected signature
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @http.route('/webhook/generic', type='json', auth='none', methods=['POST'])
    def handle_generic_webhook(self):
        """Generic webhook handler untuk berbagai events"""
        # Get raw payload
        payload = request.httprequest.get_data().decode('utf-8')
        signature = request.httprequest.headers.get('X-Webhook-Signature')

        # Verify webhook
        webhook_config = self._get_webhook_config(request.jsonrequest.get('event'))
        if not webhook_config:
            return {'error': 'Unknown event type'}, 400

        if not self._verify_webhook_signature(
            payload,
            signature,
            webhook_config.secret
        ):
            return {'error': 'Invalid signature'}, 401

        # Process webhook
        try:
            result = self._process_webhook(
                webhook_config,
                request.jsonrequest
            )
            return result
        except Exception as e:
            _logger.exception('Webhook processing failed')
            # Return 200 agar provider tidak retry terus
            return {'status': 'error', 'message': str(e)}

    def _process_webhook(self, config, data):
        """Process webhook berdasarkan type"""
        model = self.env[config.target_model]

        if config.action == 'create':
            return model.create(data.get('payload', {}))

        elif config.action == 'update':
            record = model.browse(data.get('record_id'))
            if not record.exists():
                return {'error': 'Record not found'}, 404
            record.write(data.get('payload', {}))
            return record

        elif config.action == 'custom':
            # Execute custom logic
            method = getattr(model, config.custom_method, None)
            if method:
                return method(data.get('payload', {}))

        return {'status': 'ok'}
```

## Step 4: Analyze External Services

### 4.1 Payment Gateways

Integrasi payment gateway adalah salah satu integrasi paling umum dalam Odoo. Odoo menyediakan module payment yang sudah terintegrasi dengan berbagai provider.

Struktur dasar integrasi payment gateway:

```python
# payment_provider.py - Contoh custom payment provider
from odoo import models, fields, api
from odoo.addons.payment import const

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('custom_gateway', 'Custom Gateway')],
        ondelete={'custom_gateway': 'set default'}
    )

    # Custom configuration fields
    custom_gateway_merchant_id = fields.Char(
        string='Merchant ID',
        required_if_code='custom_gateway',
        groups='base.group_user'
    )
    custom_gateway_api_key = fields.Char(
        string='API Key',
        required_if_code='custom_gateway',
        groups='base.group_user'
    )
    custom_gateway_environment = fields.Selection(
        [('test', 'Test'), ('production', 'Production')],
        default='test'
    )

    def _get_custom_gateway_urls(self, environment):
        """Get API URLs untuk environment"""
        if environment == 'production':
            return {
                'form_url': 'https://api.gateway.com/pay',
                'verify_url': 'https://api.gateway.com/verify',
            }
        return {
            'form_url': 'https://sandbox.gateway.com/pay',
            'verify_url': 'https://sandbox.gateway.com/verify',
        }

    def _custom_gateway_form_generate_values(self, values):
        """Generate form values untuk payment redirect"""
        base_url = self.get_base_url()

        custom_values = {
            'merchant_id': self.custom_gateway_merchant_id,
            'amount': values['amount'],
            'currency': values['currency'].name,
            'reference': values['reference'],
            'return_url': f"{base_url}/payment/custom_gateway/return",
            'cancel_url': f"{base_url}/payment/custom_gateway/cancel",
            'notify_url': f"{base_url}/payment/custom_gateway/notify",
        }

        return custom_values

    def custom_gateway_get_form_action_url(self):
        """Get payment form URL"""
        return self._get_custom_gateway_urls(
            self.custom_gateway_environment
        )['form_url']
```

### 4.2 Shipping Providers

Integrasi dengan shipping providers memungkinkan otomatis perhitungan ongkos kirim, pelacakan pengiriman, dan generation of shipping labels.

```python
# shipping_integration.py - Contoh integrasi shipping provider
from odoo import models, api, fields
import requests
import logging

_logger = logging.getLogger(__name__)

class ShippingProvider(models.Model):
    _name = 'shipping.provider'
    _description = 'Shipping Provider Integration'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    api_url = fields.Char(required=True)
    api_key = fields.Char()
    api_secret = fields.Char()
    active = fields.Boolean(default=True)

    def _get_shipping_rates(self, picking):
        """Get shipping rates dari provider"""
        self.ensure_one()

        # Prepare request
        payload = {
            'from': {
                'name': picking.picking_type_id.warehouse_id.partner_id.name,
                'street': picking.picking_type_id.warehouse_id.partner_id.street,
                'city': picking.picking_type_id.warehouse_id.partner_id.city,
                'country': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
                'zip': picking.picking_type_id.warehouse_id.partner_id.zip,
            },
            'to': {
                'name': picking.partner_id.name,
                'street': picking.partner_id.street,
                'city': picking.partner_id.city,
                'country': picking.partner_id.country_id.code,
                'zip': picking.partner_id.zip,
            },
            'packages': self._calculate_packages(picking),
        }

        try:
            response = requests.post(
                f'{self.api_url}/rates',
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                timeout=30
            )
            response.raise_for_status()
            return self._parse_rates(response.json())
        except requests.RequestException as e:
            _logger.error(f'Failed to get shipping rates: {e}')
            return []

    def _calculate_packages(self, picking):
        """Calculate packages berdasarkan moves"""
        packages = []
        for move in picking.move_ids:
            for quant in move.move_line_ids:
                packages.append({
                    'weight': quant.qty_done * quant.product_id.weight,
                    'dimensions': {
                        'length': quant.product_id.package_length or 10,
                        'width': quant.product_id.package_width or 10,
                        'height': quant.product_id.package_height or 10,
                    }
                })
        return packages

    def _parse_rates(self, response):
        """Parse API response menjadi rate objects"""
        rates = []
        for service in response.get('services', []):
            rates.append({
                'name': service['name'],
                'delivery_time': service['transit_days'],
                'price': service['price'],
                'currency': response.get('currency'),
                'service_code': service['code'],
            })
        return rates

    def create_shipment(self, picking, service_code):
        """Create shipment dengan provider"""
        self.ensure_one()

        payload = self._prepare_shipment(picking, service_code)

        try:
            response = requests.post(
                f'{self.api_url}/shipments',
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                timeout=60
            )
            response.raise_for_status()
            return self._parse_shipment_response(response.json())
        except requests.RequestException as e:
            _logger.error(f'Failed to create shipment: {e}')
            return False

    def get_tracking_info(self, tracking_number):
        """Get tracking information"""
        self.ensure_one()

        try:
            response = requests.get(
                f'{self.api_url}/track/{tracking_number}',
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f'Failed to get tracking: {e}')
            return {}
```

### 4.3 CRM Integration

Integrasi dengan CRM eksternal memungkinkan sinkronisasi data customer dan opportunity:

```python
# crm_integration.py - Contoh integrasi CRM
from odoo import models, api, fields
import requests
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class CRMIntegration(models.Model):
    _name = 'crm.integration'
    _description = 'CRM External Integration'

    name = fields.Char(required=True)
    provider = fields.Selection([
        ('salesforce', 'Salesforce'),
        ('hubspot', 'HubSpot'),
        ('zoho', 'Zoho'),
        ('custom', 'Custom REST API'),
    ])
    api_endpoint = fields.Char()
    api_key = fields.Char()
    sync_contacts = fields.Boolean(default=True)
    sync_opportunities = fields.Boolean(default=True)
    last_sync = fields.Datetime()

    def sync_contacts_from_crm(self):
        """Sinkronisasi contacts dari external CRM"""
        for integration in self:
            if not integration.sync_contacts:
                continue

            try:
                contacts = integration._fetch_contacts()

                for ext_contact in contacts:
                    # Find atau create contact
                    partner = self.env['res.partner'].search([
                        ('external_crm_id', '=', ext_contact['id'])
                    ])

                    if partner:
                        partner.write({
                            'name': ext_contact.get('name'),
                            'email': ext_contact.get('email'),
                            'phone': ext_contact.get('phone'),
                            'street': ext_contact.get('address'),
                            'last_sync_date': fields.Datetime.now(),
                        })
                    else:
                        self.env['res.partner'].create({
                            'name': ext_contact.get('name'),
                            'email': ext_contact.get('email'),
                            'phone': ext_contact.get('phone'),
                            'street': ext_contact.get('address'),
                            'external_crm_id': ext_contact['id'],
                            'external_crm_system': integration.provider,
                        })

                integration.write({'last_sync': fields.Datetime.now()})

            except Exception as e:
                _logger.error(f'Contact sync failed: {e}')

    def _fetch_contacts(self):
        """Fetch contacts dari external CRM"""
        self.ensure_one()

        if self.provider == 'hubspot':
            return self._fetch_hubspot_contacts()
        elif self.provider == 'salesforce':
            return self._fetch_salesforce_contacts()
        else:
            return self._fetch_custom_contacts()

    def _fetch_hubspot_contacts(self):
        """Fetch contacts dari HubSpot"""
        response = requests.get(
            f'{self.api_endpoint}/crm/v3/objects/contacts',
            headers={
                'Authorization': f'Bearer {self.api_key}',
            },
            params={'limit': 100}
        )
        response.raise_for_status()

        return [
            {
                'id': c['id'],
                'name': c['properties'].get('firstname', '') + ' ' + c['properties'].get('lastname', ''),
                'email': c['properties'].get('email'),
                'phone': c['properties'].get('phone'),
                'address': c['properties'].get('address'),
            }
            for c in response.json().get('results', [])
        ]

    def push_opportunity_to_crm(self, opportunity):
        """Push opportunity ke external CRM"""
        self.ensure_one()

        payload = {
            'name': opportunity.name,
            'amount': opportunity.expected_revenue,
            'stage': opportunity.stage_id.name,
            'probability': opportunity.probability,
            'close_date': opportunity.date_deadline.isoformat() if opportunity.date_deadline else None,
            'partner': {
                'name': opportunity.partner_id.name,
                'email': opportunity.partner_id.email,
            } if opportunity.partner_id else None,
        }

        if self.provider == 'hubspot':
            return self._push_hubspot_deal(opportunity, payload)

    def _push_hubspot_deal(self, opportunity, payload):
        """Push deal ke HubSpot"""
        response = requests.post(
            f'{self.api_endpoint}/crm/v3/objects/deals',
            json={
                'properties': payload
            },
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
        )
        response.raise_for_status()

        # Store external ID
        result = response.json()
        opportunity.write({'external_crm_id': result.get('id')})

        return result
```

### 4.4 E-commerce Platforms

Integrasi dengan e-commerce platforms seperti Shopify, WooCommerce, atau Magento memerlukan sinkronisasi produk, orders, dan inventory:

```python
# ecommerce_integration.py - Contoh integrasi e-commerce
from odoo import models, api, fields
import requests
import logging
import base64

_logger = logging.getLogger(__name__)

class EcommerceIntegration(models.Model):
    _name = 'ecommerce.integration'
    _description = 'E-commerce Platform Integration'

    name = fields.Char(required=True)
    platform = fields.Selection([
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('custom', 'Custom Platform'),
    ])
    api_url = fields.Char(string='Store URL')
    api_key = fields.Char(string='API Key')
    api_secret = fields.Char(string='API Secret')
    webhook_secret = fields.Char()

    def import_orders_from_ecommerce(self):
        """Import orders dari e-commerce platform"""
        for integration in self:
            try:
                orders = integration._fetch_orders()

                for ext_order in orders:
                    # Check if order already exists
                    existing = self.env['sale.order'].search([
                        ('external_order_id', '=', ext_order['id'])
                    ])

                    if existing:
                        # Update existing order
                        integration._update_order(existing, ext_order)
                    else:
                        # Create new order
                        integration._create_order(ext_order)

            except Exception as e:
                _logger.error(f'Order import failed: {e}')

    def _fetch_orders(self):
        """Fetch orders dari platform"""
        self.ensure_one()

        if self.platform == 'shopify':
            return self._fetch_shopify_orders()
        elif self.platform == 'woocommerce':
            return self._fetch_woocommerce_orders()

        return []

    def _fetch_shopify_orders(self):
        """Fetch orders dari Shopify"""
        # Generate basic auth header
        auth = base64.b64encode(
            f'{self.api_key}:{self.api_secret}'.encode()
        ).decode()

        response = requests.get(
            f'{self.api_url}/admin/api/2024-01/orders.json',
            headers={
                'Authorization': f'Basic {auth}',
            },
            params={'status': 'any', 'limit': 250}
        )
        response.raise_for_status()

        return response.json().get('orders', [])

    def _create_order(self, ext_order):
        """Create Odoo sale order dari external order"""
        self.ensure_one()

        # Find atau create customer
        partner = self._find_or_create_partner(ext_order.get('customer', {}))

        # Prepare order data
        order_data = {
            'partner_id': partner.id,
            'external_order_id': ext_order['id'],
            'external_order_number': ext_order.get('order_number'),
            'date_order': ext_order.get('created_at'),
            'note': ext_order.get('note'),
        }

        # Add warehouse
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        if warehouse:
            order_data['warehouse_id'] = warehouse.id

        # Create order
        order = self.env['sale.order'].create(order_data)

        # Add order lines
        for line in ext_order.get('line_items', []):
            product = self._find_product(line)

            if product:
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'name': line.get('name'),
                    'product_uom_qty': line.get('quantity'),
                    'price_unit': line.get('price'),
                    'tax_id': [(6, 0, self._get_taxes(line.get('tax_lines', [])))],
                })

        # Confirm order automatically jika needed
        if ext_order.get('financial_status') == 'paid':
            order.action_confirm()

        return order

    def _find_product(self, line_item):
        """Find atau create product dari line item"""
        # Try by SKU
        if line_item.get('sku'):
            product = self.env['product.product'].search([
                ('default_code', '=', line_item['sku'])
            ], limit=1)
            if product:
                return product

        # Try by name
        product = self.env['product.product'].search([
            ('name', '=', line_item.get('name'))
        ], limit=1)

        if product:
            return product

        # Create new product
        return self.env['product.product'].create({
            'name': line_item.get('name'),
            'default_code': line_item.get('sku'),
            'list_price': float(line_item.get('price', 0)),
            'type': 'product',
        })

    def sync_inventory_to_ecommerce(self):
        """Sync inventory levels ke e-commerce platform"""
        for integration in self:
            products = self.env['product.product'].search([
                ('type', '=', 'product'),
                ('external_product_id', '!=', False),
            ])

            for product in products:
                try:
                    integration._update_inventory(product)
                except Exception as e:
                    _logger.error(f'Failed to sync inventory for {product.name}: {e}')

    def _update_inventory(self, product):
        """Update inventory di e-commerce platform"""
        self.ensure_one()

        qty_available = product.qty_available

        if self.platform == 'shopify':
            endpoint = f"{self.api_url}/admin/api/2024-01/products/{product.external_product_id}.json"

            auth = base64.b64encode(
                f'{self.api_key}:{self.api_secret}'.encode()
            ).decode()

            response = requests.put(
                endpoint,
                json={
                    'product': {
                        'id': product.external_product_id,
                        'variants': [{
                            'id': product.external_variant_id,
                            'inventory_quantity': int(qty_available),
                        }]
                    }
                },
                headers={
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/json',
                }
            )
            response.raise_for_status()
```

## Step 5: Document Integration

### 5.1 API Documentation Template

Dokumentasi yang baik sangat penting untuk keberhasilan integrasi. Berikut template dokumentasi API:

```markdown
# API Documentation

## Overview
[Describe the purpose of this API]

## Base URL
```
Production: https://api.production.com
Sandbox: https://api.sandbox.com
```

## Authentication

### API Key
Include your API key in the request header:
```
Authorization: Bearer YOUR_API_KEY
```

### Rate Limits
- 100 requests per minute
- 10,000 requests per day

## Endpoints

### GET /api/vendors
Get list of vendors

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| limit | int | No | Max results (default: 100) |
| offset | int | No | Pagination offset |
| search | string | No | Search term |

**Response:**
```json
{
  "vendors": [
    {
      "id": 1,
      "name": "Vendor Name",
      "email": "vendor@example.com",
      "phone": "+1234567890"
    }
  ],
  "count": 1
}
```

### POST /api/vendors
Create new vendor

**Request Body:**
```json
{
  "name": "Vendor Name",
  "email": "vendor@example.com",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Vendor Name",
  "status": "created"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |
```

### 5.2 Integration Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Odoo System                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ REST API     │  │ XML-RPC      │  │ Webhooks    │          │
│  │ Controller   │  │ Handler      │  │ Outgoing    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│  ┌──────┴──────────────────┴──────────────────┴───────┐      │
│  │              Integration Layer                        │      │
│  │  - Authentication Manager                            │      │
│  │  - Data Transformer                                  │      │
│  │  - Error Handler                                      │      │
│  │  - Retry Logic                                        │      │
│  └──────────────────────┬───────────────────────────────┘      │
└─────────────────────────┼───────────────────────────────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────▼────┐         ┌─────▼─────┐        ┌────▼─────┐
│ Payment │         │ Shipping  │        │  CRM     │
│ Gateway │         │ Provider  │        │ System   │
└─────────┘         └───────────┘        └──────────┘
```

## Output Format

## Integration Analysis

### API Design

[Summary of recommended API approach based on requirements]

### Authentication

[Summary of recommended authentication method]

### Data Flow

[Description of data flow patterns - push/pull, real-time/batch]

### Error Handling

[Description of error handling strategy]

### Recommendations

[Specific recommendations for the integration scenario]
