# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    allowed_approval_category_ids = fields.Many2many("approval.category", string="Allowed Approval Categories")

    def write(self, vals):
        res = super(ResUsers, self).write(vals)

        if self.ids and any(key in ["allowed_approval_category_ids"] for key in vals.keys()):
            self.env["ir.model.access"].call_cache_clearing_methods()

        return res
