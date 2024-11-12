# -*- coding: utf-8 -*-

from odoo import models, fields


class HRPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    currency_rate = fields.Float(string="Currency Rate")
