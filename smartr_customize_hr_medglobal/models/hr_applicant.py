from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    interviewer_job_ids = fields.Many2many('hr.job')
    job_address = fields.Many2one("res.partner",
                                  "Job Address",
                                  domain="[('type', '=', 'other'), ('parent_id', '=', company_id)]")
    job_location = fields.Many2one("hr.work.location",
                                   "Job Location",
                                   domain="[('address_id', '=', job_address)]")

    response_ids = fields.One2many('survey.user_input', 'applicant_id',
                                   compute='get_response_ids',
                                   string="Responses")
    email_from = fields.Char(required=True)
    core_competencies = fields.Text()
    technical_competencies = fields.Text()
    interviewer_other_notes = fields.Text()
    interviewer_recommendation = fields.Selection([
        ('not_recommended', 'Not Recommended'),
        ('recommended_with_res', 'Recommended With Reservations'),
        ('recommended', 'Recommended'),
        ('not_decided', 'Not Decided Yet'),
    ], default='not_decided')

    ref_check_ids = fields.One2many('survey.user_input', 'applicant_id',
                                    compute='get_ref_check_ids',
                                    string="Reference Checks")
    pre_screen_survey_id = fields.Many2one('survey.user_input',
                                           'Pre-screen questionnaire',
                                           domain="[('email', '=', email_from), ('survey_type', '=', 'pre_screen')]",
                                           compute='get_pre_screen_survey_id',
                                           readonly=True)
    interview_scorecard_ids = fields.One2many('survey.user_input',
                                              'applicant_id',
                                              compute='get_ref_check_ids',
                                              string="Interview Score Cards")
    scorecard_survey_id = fields.Many2one('survey.survey',
                                          'Interview Scorecard template',
                                          compute="get_interview_scorecard_template",
                                          domain="[('job_id', '=', job_id),('survey_type', '=', 'interview_scorecard')]")

    def create(self, vals_list):
        for val in vals_list:
            if 'email_from' == val:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", vals_list['email_from']):
                    raise ValidationError("Invalid email format: %s" % vals_list['email_from'])
        res = super(HrApplicant, self).create(vals_list)
        return res

    def get_response_ids(self):
        for rec in self:
            user_inputs = self.env['survey.user_input'].search([('email', '=', rec.email_from),
                                                                ('survey_type', '=', 'interview'),
                                                                ('email', '!=', False)])
            rec.response_ids = user_inputs

    def get_ref_check_ids(self):
        for rec in self:
            ref_checks = self.env['survey.user_input'].search([('email', '=', rec.email_from),
                                                               ('survey_type', '=', 'ref_check'),
                                                               ('email', '!=', False)])

            interview_scorecard = self.env['survey.user_input'].search([('email', '=', rec.email_from),
                                                                        ('survey_type', '=', 'interview_scorecard'),
                                                                        ('email', '!=', False)])
            rec.ref_check_ids = ref_checks
            rec.interview_scorecard_ids = interview_scorecard

    def get_pre_screen_survey_id(self):
        for rec in self:
            user_inputs = self.env['survey.user_input'].search([('email', '=', rec.email_from),
                                                                ('survey_type', '=', 'pre_screen'),
                                                                ('email', '!=', False)])
            rec.pre_screen_survey_id = user_inputs

    def get_interview_scorecard_template(self):
        for rec in self:
            template = self.env['survey.survey'].search([('job_id', '=', rec.job_id.id),
                                                         ('survey_type', '=', 'interview_scorecard')])
            rec.scorecard_survey_id = template

    def action_send_invitation(self, survey, invite_name):
        self.ensure_one()
        # if an applicant does not already has associated partner_id create it
        if not self.partner_id:
            if not self.partner_name:
                raise UserError(_('Please provide an applicant name.'))
            self.partner_id = self.env['res.partner'].sudo().create({
                'is_company': False,
                'name': self.partner_name,
                'email': self.email_from,
                'phone': self.partner_phone,
                'mobile': self.partner_mobile
            })

        survey.check_validity()

        template = self.env.ref('hr_recruitment_survey.mail_template_applicant_interview_invite',
                                raise_if_not_found=False)
        local_context = dict(
            default_applicant_id=self.id,
            default_partner_ids=self.partner_id.ids,
            default_survey_id=survey.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_email_layout_xmlid='mail.mail_notification_light',
            default_email=self.email_from
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _(invite_name),
            'view_mode': 'form',
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }

    def action_send_ref_check(self):
        survey = self.env['survey.survey'].search([('survey_type', '=', 'ref_check')])
        return self.action_send_invitation(survey, 'Send a Reference check')

    def action_send_pre_screen(self):
        survey = self.env['survey.survey'].search([('survey_type', '=', 'pre_screen')])
        return self.action_send_invitation(survey, 'Send a Pre-screen questionnaire')

    def action_scorecard(self):
        survey = self.env['survey.survey'].search([('survey_type', '=', 'interview_scorecard'),
                                                   ('job_id', '=', self.job_id.id)])
        return self.action_send_invitation(survey, 'Send an Interview scorecard')
