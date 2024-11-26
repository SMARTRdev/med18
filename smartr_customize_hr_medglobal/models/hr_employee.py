# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HREmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    restrict_employees_company = fields.Boolean(related="company_id.restrict_employees")
    in_sub_company = fields.Boolean(compute="_compute_in_sub_company", string="In Sub Company",
                                    readonly=False, store=True)
    department_function_id = fields.Many2one(related="department_id.department_function_id",
                                             string="Department Function", readonly=True, store=True)

    @api.depends("company_id.restrict_employees")
    def _compute_in_sub_company(self):
        for employee in self.filtered(lambda e: e.in_sub_company and not e.company_id.restrict_employees):
            employee.in_sub_company = False


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def create(self, vals_list):
        if 'job_id' in vals_list:
            job_position = self.env['hr.job'].browse(vals_list['job_id'])
            if job_position.no_of_recruitment <= 0:
                if not self.env.user._is_superuser():
                    raise UserError(_("You can't create employee in job position {} because target is zero."
                                      .format(job_position.name)))
            else:
                job_position.no_of_recruitment -= 1

        return super().create(vals_list)
