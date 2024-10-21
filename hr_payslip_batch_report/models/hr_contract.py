# -*- coding: utf-8 -*-

from odoo import models, fields


class HRContract(models.Model):
    _inherit = "hr.contract"

    payment_by_hq = fields.Boolean(string="Payment By HQ", tracking=True)
