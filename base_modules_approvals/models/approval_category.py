# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    approval_type = fields.Selection(selection_add=[("model", "Model")], ondelete={"model": "cascade"})
    model_id = fields.Many2one("ir.model", string="Model")

    @api.onchange("approval_type")
    def onchange_model_approval_type(self):
        if self.approval_type != "model" and self.model_id:
            self.model_id = False
