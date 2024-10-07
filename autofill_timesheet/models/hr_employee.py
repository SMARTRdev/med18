# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    exclude_timesheets_autofill = fields.Boolean(string="Exclude from Timesheets Autofill", tracking=True)
