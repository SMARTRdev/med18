# -*- coding: utf-8 -*-
from odoo import models, fields


class ApprovalRequest(models.Model):
    _inherit = "approval.request"

    category_id = fields.Many2one(domain=[("approval_type", "!=", "model")])
    res_id = fields.Integer(string="Record ID")
