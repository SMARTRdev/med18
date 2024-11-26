# -*- coding: utf-8 -*-

from odoo import models, fields


class HREmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    exclude_timesheets_autofill = fields.Boolean(string="Exclude from Timesheets Autofill", tracking=True)
