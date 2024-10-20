# -*- coding: utf-8 -*-

from odoo import models


class SignPrintTemplateWizard(models.TransientModel):
    _inherit = "sign.print.template"

    def action_sign_print(self):
        result = super().action_sign_print()
        if self._context.get("active_model") == "hr.applicant":
            self.env["hr.applicant"].browse(self._context["active_id"]).write(
                {"sign_request_ids": [(4, result["context"]["id"])]})

        return result
