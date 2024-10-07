# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    autofill_timesheet_project_id = fields.Many2one("project.project", string="Project", check_company=True,
                                                    related="company_id.autofill_timesheet_project_id", readonly=False)
    autofill_custom_hours_employees = fields.Boolean(related="company_id.autofill_custom_hours_employees",
                                                  string="Autofill Custom Hours for Employees", readonly=False)
    hours_only_allocation = fields.Boolean(related="company_id.hours_only_allocation", string="Hours Only Allocation",
                                           readonly=False)
