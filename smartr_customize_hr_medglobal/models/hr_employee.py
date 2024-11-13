# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HREmployee(models.Model):
    _inherit = "hr.employee"

    restrict_employees_company = fields.Boolean(related="company_id.restrict_employees")
    in_sub_company = fields.Boolean(compute="_compute_in_sub_company", string="In Sub Company",
                                    readonly=False, store=True)

    @api.depends("company_id.restrict_employees")
    def _compute_in_sub_company(self):
        for employee in self.filtered(lambda e: e.in_sub_company and not e.company_id.restrict_employees):
            employee.in_sub_company = False
