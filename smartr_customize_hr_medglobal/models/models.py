# -*- coding: utf-8 -*-

from datetime import datetime

from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import format_amount


class HrAnnouncementType(models.Model):
    _name = 'hr.announcement.category'

    name = fields.Char()
    type = fields.Selection([('internal_vacancy', 'Internal Vacancy')], default='internal_vacancy')


class HrAnnouncement(models.Model):
    _inherit = 'hr.announcement'

    category_id = fields.Many2one('hr.announcement.category', string='Category')
    job_id = fields.Many2one('hr.job', string='Job Position')
    job_code = fields.Char(string='Job Code')
    job_address = fields.Many2one("res.partner",
                                  "Job Address",
                                  domain="[('type', '=', 'other'), ('parent_id', '=', company_id)]")
    job_location = fields.Many2one("hr.work.location",
                                   "Job Location",
                                   domain="[('address_id', '=', job_address)]")
    department_id = fields.Many2one('hr.department',
                                    string='Job Department',
                                    related='job_id.department_id',
                                    readonly=True)
    contract_duration = fields.Integer('Contract Duration')
    salary_scale = fields.Monetary("Salary Scale")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    job_description = fields.Html('Job Description And Specification')
    is_internal_vacancy = fields.Boolean(compute="_compute_is_internal_vacancy")
    announcement_message = fields.Text(required=True)
    announcement_type = fields.Selection(selection='_get_new_announcement_type',
                                         compute='_compute_announcement_type', readonly=False, store=True)

    @api.model
    def _get_new_announcement_type(self):
        selection = [('department', 'By Department')]
        return selection

    def unlink(self):
        for rec in self:
            if not (self.env.is_admin() or self.env.user.has_group('ent_hr_reward_warning.group_manager')):
                raise UserError(_("You don't have the rights to delete records. Please contact an Administrator."))
            else:
                return super(HrAnnouncement, self).unlink()

    @api.onchange('category_id')
    def _compute_is_internal_vacancy(self):
        for rec in self:
            rec.is_internal_vacancy = rec.category_id.type == 'internal_vacancy'

    def send_message_to_channels(self, channels, message):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        rec_url = base_url + '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        for channel in channels:
            message_html = ("<div>"
                            "<p>{message}</p><br>"
                            "<a href='{rec_link}' class='btn btn-primary' target='_blank'>Check Announcement</a>"
                            "</div>").format(message=message, rec_link=rec_url)

            message_with_button = Markup(message_html)
            channel.sudo().message_post(body=message_with_button,
                                        author_id=self.env.user.partner_id.id,
                                        message_type="comment",
                                        subtype_xmlid="mail.mt_comment")

    def create_channel_for_department(self, department):
        self.env['discuss.channel'].create({
            "name": department.name,
            "group_public_id": 1,
            "channel_type": "channel",
            "active": True,
            "subscription_department_ids": department
        })

    def approve(self):
        channels = self.env['discuss.channel']
        if self.is_announcement:
            channels = self.sudo().env.ref('mail.channel_all_employees')

        elif self.announcement_type == 'department':
            for department in self.department_ids:
                if not self.env['discuss.channel'].search([('subscription_department_ids', 'in', department.id)]):
                    self.create_channel_for_department(department)

            channels = self.env['discuss.channel'].search(
                [('subscription_department_ids', 'in', self.department_ids.ids)])

        self.send_message_to_channels(channels, self.announcement_message)
        self.state = 'approved'


class ApprovedGradingScale(models.Model):
    _name = 'approved.grading.scale'

    name = fields.Char()


class ApprovalJobLine(models.Model):
    _inherit = "approval.job.line"

    anticipated_start_date = fields.Date("Anticipated start date", required=True,
                                         default=fields.Date.context_today)
    anticipated_end_date = fields.Date("Anticipated End date", required=True, default=fields.Date.context_today)
    employment_reason = fields.Selection([('new_vacancy', "New Vacancy"), ('replacement', "Replacement")],
                                         default='new_vacancy')
    incumbent_employee_id = fields.Many2one('hr.employee',
                                            'Incumbent', domain="[('job_id', '=', job_id)]")
    approved_scale = fields.Many2one(related='job_id.approved_scale')
    salary_grade_id = fields.Many2one("hr.salary.grade", string="Salary Grade")
    salary_range_min = fields.Monetary(related="salary_grade_id.salary_range_min", readonly=True, store=True)
    salary_range_max = fields.Monetary(related="salary_grade_id.salary_range_max", readonly=True, store=True)
    proposed_salary = fields.Monetary()
    source_of_employment = fields.Selection([('internal', "Internal Hiring"),
                                             ('external', "External Hiring"),
                                             ('rehire', "Rehire")], 'Employment Type', default='internal')
    percentage_of_travel = fields.Integer('Percentage of travel')
    work_location = fields.Selection([('remote', 'Remote'), ('on_site', 'Onsite')], default='remote')
    work_schedule = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time')],
                                     default='full_time')
    hours_per_week = fields.Integer('Hours Per Week')
    budget_line_id = fields.Many2one('budget.line')

    @api.constrains("proposed_salary", "salary_grade_id")
    def _check_proposed_salary(self):
        for job_line in self:
            salary_grade = job_line.salary_grade_id
            if job_line.proposed_salary < salary_grade.salary_range_min or job_line.proposed_salary > salary_grade.salary_range_max:
                raise ValidationError(
                    _("Job %s\nThe Proposed Salary should be between %s and %s") %
                    (job_line.job_id.name,
                     format_amount(self.env, salary_grade.salary_range_min, job_line.currency_id),
                     format_amount(self.env, salary_grade.salary_range_max, job_line.currency_id)))

    @api.constrains('quantity')
    def _constrains_quantity(self):
        for rec in self:
            if rec.approval_request_id.approval_type == 'recruitment':
                available_quantity = rec.job_id.planned_target
                if rec.quantity > available_quantity and not rec.is_unplanned and not rec.is_new:
                    raise ValidationError(_('Job: {} , Quantity: should be equal or less than {} (Remaining)'
                                            .format(rec.job_id.name, available_quantity)))

    @api.constrains('anticipated_end_date')
    def _constraint_anticipated_end_date(self):
        for rec in self:
            if rec.approval_request_id.approval_type == 'recruitment':
                if self.diff_month(rec.anticipated_end_date, rec.anticipated_start_date) < 3:
                    raise ValidationError(_('Job: {} , Anticipated End Date: Minimum difference between Anticipated '
                                            'Start Date and End Date should be 3 months'
                                            .format(rec.job_id.name)))

    @api.constrains('anticipated_start_date')
    def _constraint_anticipated_start_date(self):
        for rec in self:
            if rec.approval_request_id.approval_type == 'recruitment':
                if rec.anticipated_start_date < datetime.today().date():
                    raise ValidationError(_('Job: {} , Anticipated Start Date: Should be >= Today'
                                            .format(rec.job_id.name)))

    @staticmethod
    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
