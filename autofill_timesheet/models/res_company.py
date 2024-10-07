# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    autofill_timesheet_project_id = fields.Many2one("project.project", string="Autofill Timesheet Project")
    autofill_custom_hours_employees = fields.Boolean(string="Autofill Custom Hours for Employees")
    hours_only_allocation = fields.Boolean(string="Hours Only Allocation")
