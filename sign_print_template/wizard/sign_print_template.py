# -*- coding: utf-8 -*-

import base64

from odoo import models, fields, _


class SignPrintTemplateWizard(models.TransientModel):
    _name = "sign.print.template"
    _description = "Sign & Print Template"

    sign_template_id = fields.Many2one("sign.template", string="Sign Template", required=True)
    model = fields.Char(string="Model", required=True)
    report_id = fields.Many2one("ir.actions.report", string="Report", required=True, domain="[('model','=',model)]")

    def action_sign_print(self):
        sign_template = self.sign_template_id.copy()

        record = self.env[self._context["active_model"]].browse(self._context["active_id"])
        report = self.report_id.sudo()._render_qweb_pdf(self.report_id.id, record.ids)
        attachment = self.env['ir.attachment'].create({
            "name": self.report_id.name + ".pdf",
            "type": "binary",
            "datas": base64.b64encode(report[0]),
            "res_model": sign_template._name,
            "res_id": sign_template.id,
            "mimetype": 'application/pdf'
        })

        sign_template.write({"attachment_id": attachment.id})

        roles = sign_template.sign_item_ids.responsible_id.sorted()
        signers_count = len(roles)
        signer_ids = [(0, 0, {
            "role_id": role.id,
            "partner_id": self.env.user.partner_id.id,
        }) for default_signing_order, role in enumerate(roles)]

        sign_send_request = (
            self.env["sign.send.request"].with_context(active_id=sign_template.id,
                                                       sign_directly_without_mail=False).create(
                {
                    "template_id": sign_template.id,
                    "filename": sign_template.display_name,
                    "subject": _("Signature Request - %(file_name)s", file_name=sign_template.attachment_id.name),
                    "signers_count": signers_count,
                    "signer_ids": signer_ids
                }))
        return sign_send_request.with_context(no_sign_mail=True, sign_all=True).sign_directly()
