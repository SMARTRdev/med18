# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_approval_route_payslip_batch = fields.Selection(string="Use Approval Route for Payslip Batch",
                                                        related="company_id.use_approval_route_payslip_batch",
                                                        readonly=False)
