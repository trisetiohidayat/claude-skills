---
name: odoo19-survey-create
description: Create Survey/Quiz model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat survey, quiz, questionnaire, atau extend survey models.
---

# Odoo 19 Survey Generator

Skill ini digunakan untuk membuat Survey/Quiz models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Creating survey/quiz system
- Questionnaire management
- Extending survey models
- Feedback collection

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Survey type**: Quiz, Survey, Feedback
3. **Fields yang dibutuhkan**: Custom fields

## Extending survey.survey

```python
from odoo import models, fields

class SurveySurvey(models.Model):
    _name = 'survey.survey'
    _inherit = 'survey.survey'

    # Custom fields
    survey_code = fields.Char(string='Survey Code')
```

## Complete Survey Extension

```python
from odoo import models, fields, api, _

class SurveySurveyExtended(models.Model):
    _name = 'survey.survey'
    _inherit = ['survey.survey', 'mail.thread', 'portal.mixin']
    _description = 'Survey (Extended)'

    # Survey Identification
    survey_code = fields.Char(
        string='Survey Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Survey Details
    title = fields.Char(string='Survey Title', required=True, tracking=True)
    description = fields.Html(string='Description')

    # Questions
    question_ids = fields.One2many(
        'survey.question',
        'survey_id',
        string='Questions',
    )

    # Settings
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    # Access
    access_mode = fields.Selection([
        ('public', 'Public'),
        ('auth', 'Authenticated'),
        ('token', 'Token'),
    ], string='Access Mode', default='public')

    # Scoring
    scoring_mode = fields.Selection([
        ('no_scoring', 'No Scoring'),
        ('scoring_with_answers', 'Scoring with answers at the end'),
        ('scoring_without_answers', 'Scoring without answers at the end'),
    ], string='Scoring Mode', default='no_scoring')

    # Results
    response_ids = fields.One2many(
        'survey.user_input',
        'survey_id',
        string='Responses',
    )
    response_count = fields.Integer(
        string='Response Count',
        compute='_compute_response_count',
    )

    # Dates
    create_date = fields.Datetime(string='Create Date')
    start_datetime = fields.Datetime(string='Start Date')
    end_datetime = fields.Datetime(string='End Date')

    # Custom Fields
    survey_category = fields.Selection([
        ('customer_feedback', 'Customer Feedback'),
        ('employee_survey', 'Employee Survey'),
        ('market_research', 'Market Research'),
        ('quiz', 'Quiz'),
        ('assessment', 'Assessment'),
        ('other', 'Other'),
    ], string='Category')

    @api.depends('response_ids')
    def _compute_response_count(self):
        for survey in self:
            survey.response_count = len(survey.response_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('survey_code', _('New')) == _('New'):
                vals['survey_code'] = self.env['ir.sequence'].next_by_code(
                    'survey.survey.code'
                ) or _('New')
        return super().create(vals_list)
```

## Survey Question

```python
class SurveyQuestion(models.Model):
    _name = 'survey.question'
    _inherit = 'survey.question'
    _description = 'Survey Question'

    # Custom fields
    question_code = fields.Char(string='Question Code')
    is_mandatory = fields.Boolean(string='Mandatory', default=True)

    # Question Type
    question_type = fields.Selection([
        ('textbox', 'Text'),
        ('char_box', 'Short Text'),
        ('numerical_box', 'Numerical'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('simple_choice', 'Multiple Choice (One Answer)'),
        ('multiple_choice', 'Multiple Choice (Multiple Answers)'),
        ('matrix', 'Matrix'),
    ], string='Question Type', required=True)

    # Answers for choice questions
    suggested_answer_ids = fields.One2many(
        'survey.question.answer',
        'question_id',
        string='Answers',
    )
```

## Survey User Input (Response)

```python
class SurveyUserInput(models.Model):
    _name = 'survey.user_input'
    _inherit = 'survey.user_input'
    _description = 'Survey User Input'

    # Custom fields
    response_code = fields.Char(string='Response Code')
    survey_id = fields.Many2one(required=True)

    partner_id = fields.Many2one('res.partner', string='Partner')
    email = fields.Char(string='Email')

    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string='Status', default='new')

    # Answers
    user_input_line_ids = fields.One2many(
        'survey.user_input.line',
        'user_input_id',
        string='Answers',
    )

    # Score
    scoring_total = fields.Float(string='Total Score')
    scoring_percentage = fields.Float(string='Score Percentage')
