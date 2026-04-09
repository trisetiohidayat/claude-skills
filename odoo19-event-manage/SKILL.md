---
name: odoo19-event-manage
description: Create Event Management model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat event management, event registration, atau extend event models.
---

# Odoo 19 Event Management Generator

Skill ini digunakan untuk membuat Event Management models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Creating event management system
- Event registration tracking
- Extending event models
- Event ticket management

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Event type**: Conference, Workshop, etc
3. **Fields yang dibutuhkan**: Custom fields

## Extending event.event

```python
from odoo import models, fields

class EventEvent(models.Model):
    _name = 'event.event'
    _inherit = 'event.event'

    # Custom fields
    event_code = fields.Char(string='Event Code')
```

## Complete Event Extension

```python
from odoo import models, fields, api, _

class EventEventExtended(models.Model):
    _name = 'event.event'
    _inherit = ['event.event', 'mail.thread', 'portal.mixin']
    _description = 'Event (Extended)'

    # Event Identification
    event_code = fields.Char(
        string='Event Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Event Details
    name = fields.Char(string='Event Name', required=True, tracking=True)
    event_type_id = fields.Many2one('event.type', string='Event Type')

    # Dates
    date_begin = fields.Datetime(string='Start Date', required=True)
    date_end = fields.Datetime(string='End Date', required=True)

    # Location
    address_id = fields.Many2one(
        'res.partner',
        string='Location',
    )
    venue = fields.Char(string='Venue')

    # Organizer
    organizer_id = fields.Many2one(
        'res.partner',
        string='Organizer',
    )

    # Registration
    registration_ids = fields.One2many(
        'event.registration',
        'event_id',
        string='Registrations',
    )
    seats_max = fields.Integer(string='Maximum Attendees')
    seats_available = fields.Integer(
        string='Available Seats',
        compute='_compute_seats',
    )
    seats_reserved = fields.Integer(string='Reserved Seats')
    seats_confirmed = fields.Integer(string='Confirmed Seats')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)

    # Website
    website_url = fields.Char(string='Website URL')
    website_published = fields.Boolean(string='Published')

    # Custom Fields
    event_category = fields.Selection([
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('webinar', 'Webinar'),
        ('other', 'Other'),
    ], string='Category')

    description = fields.Html(string='Description')

    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        for event in self:
            confirmed = len(event.registration_ids.filtered(
                lambda r: r.state in ('done', 'open')
            ))
            event.seats_available = event.seats_max - confirmed

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('event_code', _('New')) == _('New'):
                vals['event_code'] = self.env['ir.sequence'].next_by_code(
                    'event.event.code'
                ) or _('New')
        return super().create(vals_list)
```

## Event Registration

```python
class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = 'event.registration'
    _description = 'Event Registration'

    # Custom fields
    registration_code = fields.Char(
        string='Registration Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    event_id = fields.Many2one(required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')

    name = fields.Char(string='Attendee Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Confirmed'),
        ('done', 'Attended'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')
