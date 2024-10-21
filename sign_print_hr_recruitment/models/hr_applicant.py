# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HRApplicant(models.Model):
    _inherit = "hr.applicant"

    sign_request_ids = fields.Many2many("sign.request", string="Requested Signatures")
    sign_print_request_count = fields.Integer(compute="_compute_sign_print_request_count")

    @api.depends('sign_request_ids')
    def _compute_sign_print_request_count(self):
        for contract in self:
            contract.sign_print_request_count = len(contract.sign_request_ids)

    def action_sign_print_document(self):
        action = self.sudo().env.ref("sign_print_template.action_sign_print_template_wizard")
        result = action.read()[0]
        result["context"] = {"default_model": self._name}
        return result

    def action_get_sign_requests(self):
        self.ensure_one()
        if self.sign_print_request_count == 1:
            return self.sign_request_ids.go_to_document()

        return {
            "type": "ir.actions.act_window",
            "name": "Signature Requests",
            "view_mode": "kanban,list",
            "res_model": "sign.request",
            "domain": [("id", "in", self.sign_request_ids.ids)]
        }
