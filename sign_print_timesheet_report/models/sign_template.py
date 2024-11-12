# -*- coding: utf-8 -*-

from odoo import models, fields


class SignTemplate(models.Model):
    _inherit = "sign.template"

    use_as_sign_print_timesheet_report = fields.Boolean(string="Use as Sign Print Timesheet Report")
