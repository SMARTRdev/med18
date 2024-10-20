# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import format_amount


class HRSalaryGradeLevel(models.Model):
    _name = 'hr.salary.grade.level'
    _description = "HR Salary Grade Level"

    name = fields.Char(required=True, translate=True, index=True)


class HRLevelResponsibility(models.Model):
    _name = "hr.level.responsibility"
    _description = "Level of Responsibility"

    name = fields.Char(required=True, translate=True, index=True)


class HRJobFamily(models.Model):
    _name = "hr.job.family"
    _description = "Job Position Family"

    name = fields.Char(required=True, translate=True, index=True)


class HRSalaryGrade(models.Model):
    _name = 'hr.salary.grade'

    name = fields.Char(required=True, translate=True, index=True)
    level_responsibility_id = fields.Many2one("hr.level.responsibility", string="Level of Responsibility",
                                              required=True)
    job_family_id = fields.Many2one("hr.job.family", string="Job Family", required=True)
    salary_grade_level_id = fields.Many2one("hr.salary.grade.level", string="Grade Level", required=True)
    skills_knowledge = fields.Html(string="Skills and Knowledge")
    experience = fields.Html(string="Experience")
    education = fields.Html(string="Education")
    language_proficiency = fields.Html(string="Language Proficiency")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company,
                                 required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    salary_range_min = fields.Monetary("Salary Range From")
    salary_range_max = fields.Monetary("Salary Range To")


class SalaryAllowance(models.Model):
    _name = 'hr.salary.allowance'

    name = fields.Char()


class FormerEmployee(models.Model):
    _name = 'hr.former.employee'

    name = fields.Char(related='employee_id.name', string="Name")
    employee_id = fields.Many2one('hr.employee', string="Replaced Personnel", required=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string="Replaced Personnel Position")
    last_working_day = fields.Date(required=True)


class HrJob(models.Model):
    _inherit = "hr.job"

    level_responsibility_id = fields.Many2one("hr.level.responsibility", string="Level of Responsibility")
    job_family_id = fields.Many2one("hr.job.family", string="Job Family")
    salary_grade_id = fields.Many2one("hr.salary.grade", string="Salary Grade", check_company=True,
                                      domain="[('level_responsibility_id','=',level_responsibility_id),('job_family_id','=',job_family_id)]")

    @api.onchange("level_responsibility_id", "job_family_id")
    def onchange_method(self):
        if self.salary_grade_id and (self.salary_grade_id.level_responsibility_id != self.level_responsibility_id
                                     or self.salary_grade_id.job_family_id != self.job_family_id):
            self.salary_grade_id = False


class HRContract(models.Model):
    _inherit = "hr.contract"

    salary_grade_id = fields.Many2one(related="job_id.salary_grade_id", string="Salary Grade", readonly=True,
                                      store=True)
    salary_range_min = fields.Monetary(related="salary_grade_id.salary_range_min", readonly=True, store=True)
    salary_range_max = fields.Monetary(related="salary_grade_id.salary_range_max", readonly=True, store=True)
    gross_salary = fields.Monetary(string="Gross Salary")

    @api.constrains("gross_salary", "salary_grade_id")
    def _check_gross_salary(self):
        for contract in self:
            salary_grade = contract.salary_grade_id
            if contract.gross_salary < salary_grade.salary_range_min or contract.gross_salary > salary_grade.salary_range_max:
                raise ValidationError(
                    _("The Gross Salary should be between %s and %s") % (
                        format_amount(self.env, salary_grade.salary_range_min, contract.currency_id),
                        format_amount(self.env, salary_grade.salary_range_max, contract.currency_id)))


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    salary_grade = fields.Many2one('hr.salary.grade')
    contract_type = fields.Selection([('internal', 'Int. Contractor'), ('external', 'Ext. Contractor')],
                                     default='internal')
    has_allowance = fields.Boolean()
    allowance_ids = fields.Many2many('hr.salary.allowance')
    working_hours = fields.Integer(required=True)
    nationality = fields.Many2one('res.country', required=True)
    is_position_in_rec_plan = fields.Boolean()
    is_replacement = fields.Boolean()
    former_employee_id = fields.Many2one('hr.former.employee')
    is_referral = fields.Boolean()
    referred_by = fields.Char(sting="Referred By")
    has_relatives = fields.Boolean(required=True)
    relatives_ids = fields.Many2many('hr.employee')
    replaced_personal_id = fields.Many2one('hr.employee', string="Replaced Personal")
    first_interviewer_id = fields.Many2one('hr.employee', string="First Interviewer")
    second_interviewer_id = fields.Many2one('hr.employee', string="Second Interviewer")
    country_office = fields.Many2one('res.country', required=True)
    is_ref_checked = fields.Boolean(required=True)
    is_security_checked = fields.Boolean(required=True)
    total_monthly_cost = fields.Float()
    salary_amount = fields.Integer()
    fin_cover_until = fields.Date()
    project_name = fields.Char()
    budget_line = fields.Many2one("budget.line")

    def _prepare_appointment_letter_fields_required(self):
        return {
            "partner_name": _("applicant's name"),
            "job_address": _("job address"),
            "salary_grade": _("salary grade"),
            "total_monthly_cost": _("total monthly cost"),
            "contract_type": _("contract type"),
            "first_interviewer_id": _("first interviewer"),
            "second_interviewer_id": _("second interviewer"),
            "job_id": _("applied job"),
            "job_location": _("job location"),
            "department_id": _("department"),
            "salary_amount": _("salary amount"),
            "working_hours": _("working hours"),
            "nationality": _("nationality"),
            "replaced_personal_id": _("replaced personal"),
            "source_id": _("source"),
            "fin_cover_until": _("fin cover until"),
            "project_name": _("project name"),
            "budget_line": _("budget line")
        }

    def action_print_appointment_letter(self):
        fields_required = self._prepare_appointment_letter_fields_required()
        for field_required in fields_required:
            if not getattr(self, field_required):
                raise ValidationError(_("Please add %s" % fields_required[field_required]))

        if self.is_referral and not self.referred_by:
            raise ValidationError(_("Please add referred by"))

        if not self.replaced_personal_id.contract_id.job_id:
            raise ValidationError(_("Please add replaced personnel position"))

        if not self.replaced_personal_id.contract_id.date_end:
            raise ValidationError(_("Please add replaced personal (last working day)"))

        if self.has_relatives:
            if not self.relatives_ids:
                raise ValidationError(_("Relatives can't be blank if the applicant has relatives"))

            for relative in self.relatives_ids:
                if not relative.contract_id.job_id:
                    raise ValidationError(_("Please add position for relative %s" % relative.display_name))

        return self.env.ref('job_candidate_offers.action_report_appointment_letter').report_action(self)

    def action_sign_print_document(self):
        if not self.is_position_in_rec_plan and not self.is_replacement:
            raise ValidationError(_("Please choose if the position is in recruitment plan or is replacement"))
        if self.has_relatives:
            if len(self.relatives_ids) == 0:
                raise ValidationError(_("Relatives can't be blank if the applicant has relatives"))
        if self.working_hours <= 0:
            raise ValidationError(_("Please add working hours"))
        if not self.is_ref_checked or not self.is_security_checked:
            raise ValidationError(_("Please mark ref and security checked"))
        if not self.job_address or not self.job_location:
            raise ValidationError(_("Please add job address and job location"))
        if self.total_monthly_cost <= 0:
            raise ValidationError(_("Please add total monthly cost"))
        if self.salary_amount <= 0:
            raise ValidationError(_("Please add salary amount"))
        if not self.project_name:
            raise ValidationError(_("Please add project name"))
        if not self.budget_line:
            raise ValidationError(_("Please add budget line"))
        if not self.fin_cover_until:
            raise ValidationError(_("Please add financial coverage until"))

        return super(HrApplicant, self).action_sign_print_document()

    def action_upload_letter_document(self):
        return {
            'type': 'ir.actions.act_window',
            "name": _("Upload Offer/Appointment Letter "),
            "view_mode": 'form',
            "res_model": "documents.document",
            "context": {
                "default_res_model": "hr.applicant",
                "default_res_id": self.id,
                # "default_folder_id": self.company_id.job_description_folder_id.id,
                # "default_tag_ids": self.company_id.job_description_tag_ids.ids,
                # "default_is_job_description": True
            },
            "view_id": self.env.ref("job_candidate_offers.view_document_upload_offer_letter_form").id,
            "target": "new"
        }
