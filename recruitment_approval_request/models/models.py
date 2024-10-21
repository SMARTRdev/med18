# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    approval_type = fields.Selection(selection_add=[('recruitment', 'Recruitment')])


class ApprovalJobLine(models.Model):
    _name = "approval.job.line"

    approval_request_id = fields.Many2one('approval.request', ondelete="cascade", readonly=True)
    job_id = fields.Many2one("hr.job", "Jobs",
                             domain="[('department_id', '=', department_id), ('department_id', '!=', False)]")
    quantity = fields.Integer("Quantity", default=1)
    department_id = fields.Many2one("hr.department", "Department", check_company=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company,
                                 readonly=True)
    manager_id = fields.Many2one("hr.employee", "Department Manager", related="department_id.manager_id",
                                 readonly=True)
    expected_joining_Date = fields.Datetime("Expected Joining Date")
    job_address = fields.Many2one("res.partner", "Job Address",
                                  domain="[('type', '=', 'other'), ('parent_id', '=', company_id)]")
    job_location = fields.Many2one("hr.work.location", "Job Location",
                                   domain="[('company_id', '=', company_id), ('address_id', '=', job_address)]")

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    salary_range_min = fields.Monetary("Salary Range From")
    salary_range_max = fields.Monetary("Salary Range To")
    job_skill_ids = fields.One2many('approval.job.skill', 'job_id', string="Skills")
    skill_ids = fields.Many2many('hr.skill', compute='_compute_skill_ids', store=True)
    show_add_button = fields.Boolean(compute="_compute_show_add_button")
    available_departments_ids = fields.Many2many('hr.department', compute='_compute_departments_ids')

    @api.depends('approval_request_id.department_id')
    def _compute_departments_ids(self):
        for rec in self:
            if rec.approval_request_id.department_id:
                rec.department_id = rec.approval_request_id.department_id.id
                rec.write({'available_departments_ids': [(4, rec.approval_request_id.department_id.id)]})
                rec.get_department_children(rec.approval_request_id.department_id, rec)
            else:
                rec.available_departments_ids = False

    def get_department_children(self, department, rec):
        children = department.child_ids
        if len(children) > 0:
            for child in children:
                rec.write({'available_departments_ids': [(4, child.id)]})
                self.get_department_children(child, rec)

    @api.depends('job_skill_ids.skill_id')
    def _compute_skill_ids(self):
        for rec in self:
            rec.skill_ids = rec.job_skill_ids.skill_id

    @api.depends('approval_request_id.request_status')
    def _compute_show_add_button(self):
        for rec in self:
            rec.show_add_button = True
            if rec.approval_request_id.request_status != 'new':
                rec.show_add_button = False

    def action_add_skill(self):
        return {
            "name": _("Add Skill"),
            "type": "ir.actions.act_window",
            "res_model": "approval.job.skill",
            "views": [[False, "form"]],
            "view_mode": "form",
            "domain": [["job_id", "=", self.id]],
            "context": dict(self._context, default_job_id=self.id),
            "target": "new"
        }

    def action_show_skills(self):
        return {
            "name": _("Job Skills"),
            "type": "ir.actions.act_window",
            "res_model": "approval.job.skill",
            "views": [[self.env.ref("recruitment_approval_request.approval_job_skill_tree_view").id, "tree"]],
            "view_mode": "list",
            "domain": [["job_id", "=", self.id]],
            "target": "new"
        }


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    job_line_ids = fields.One2many('approval.job.line', 'approval_request_id', check_company=True)
    request_owner_id = fields.Many2one('res.users', readonly=True)
    show_submit_button = fields.Boolean(compute="_compute_show_submit_button")

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        for request in self:
            super(ApprovalRequest, request)._compute_request_status()
            if request.request_status == 'approved' and request.approval_type == 'recruitment':
                for job_line in request.job_line_ids:
                    job_line.job_id.no_of_recruitment += job_line.quantity

    @api.depends('job_line_ids')
    def _compute_show_submit_button(self):
        for rec in self:
            rec.show_submit_button = True

    def action_confirm(self):
        res = super(ApprovalRequest, self).action_confirm()
        return res


class ApprovalJobSkill(models.Model):
    _name = "approval.job.skill"

    job_id = fields.Many2one('approval.job.line',
                             ondelete='cascade',
                             readonly=True)
    skill_id = fields.Many2one('hr.skill', compute='_compute_skill_id', store=True,
                               domain="[('skill_type_id', '=', skill_type_id)]", readonly=False, required=True,
                               ondelete='cascade')
    skill_level_id = fields.Many2one('hr.skill.level', compute='_compute_skill_level_id',
                                     domain="[('skill_type_id', '=', skill_type_id)]", store=True, readonly=False,
                                     required=True, ondelete='cascade')
    skill_type_id = fields.Many2one('hr.skill.type',
                                    default=lambda self: self.env['hr.skill.type'].search([], limit=1),
                                    required=True, ondelete='cascade')
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    @api.constrains('job_id', 'skill_id')
    def _check_skill(self):
        for record in self:
            if self.env['approval.job.skill'].search_count([
                ('job_id', '=', record.job_id.id),
                ('skill_id', '=', record.skill_id.id)
            ]) > 1:
                raise ValidationError(_("Two levels for the same skill is not allowed"))

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(
                    _("The skill %(name)s and skill type %(type)s doesn't match", name=record.skill_id.name,
                      type=record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s",
                                        level=record.skill_level_id.name, type=record.skill_type_id.name))

    @api.depends('skill_type_id')
    def _compute_skill_id(self):
        for record in self:
            if record.skill_type_id:
                record.skill_id = record.skill_type_id.skill_ids[0] if record.skill_type_id.skill_ids else False
            else:
                record.skill_id = False

    @api.depends('skill_id')
    def _compute_skill_level_id(self):
        for record in self:
            if not record.skill_id:
                record.skill_level_id = False
            else:
                skill_levels = record.skill_type_id.skill_level_ids
                record.skill_level_id = skill_levels.filtered('default_level') or skill_levels[
                    0] if skill_levels else False


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    first_interview_datetime = fields.Date(string='First Interview', default=fields.Date.context_today)
    second_interview_datetime = fields.Date(string='Second Interview', default=fields.Date.context_today)
    years_of_experience = fields.Integer(string="Years Of Experience", default=0, required=True)
    period_of_contract = fields.Integer(string="Period Of Contract (Months)", default=0)
    ranking = fields.Integer(string="Rank")

    def create_employee_from_applicant(self):
        """ Create an employee from applicant """
        self.ensure_one()
        self._check_interviewer_access()

        if not self.partner_id:
            if not self.partner_name:
                raise UserError(_('Please provide an applicant name.'))
            self.partner_id = self.env['res.partner'].create({
                'is_company': False,
                'name': self.partner_name,
                'email': self.email_from,
            })

        action = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        employee = self.env['hr.employee'].create(self._get_employee_create_vals())
        action['res_id'] = employee.id

        if not self.job_id:
            raise UserError(_('Please provide an applicant job.'))

        if self.job_id.no_of_recruitment > 0:
            # self.job_id.no_of_recruitment -= 1
            self.job_id.no_of_hired_employee +=1

        return action