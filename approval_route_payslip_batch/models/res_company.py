# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    use_approval_route_payslip_batch = fields.Selection([
        ("no", "No"),
        ("optional", "Optional"),
        ("required", "Required")], string="Use Approval Route for Payslip Batch", default="no")
