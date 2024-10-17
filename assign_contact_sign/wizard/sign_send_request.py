# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SignSendRequest(models.TransientModel):
    _inherit = "sign.send.request"

    @api.model
    def _default_signer_ids(self):
        signer_ids = super()._default_signer_ids()
        sign_item_role_obj = self.env["sign.item.role"]

        for signer in signer_ids:
            role = sign_item_role_obj.browse(signer[2]["role_id"])
            signer[2]["partner_id"] = role.assign_contact_id.id
        return signer_ids

    signer_ids = fields.One2many(default=_default_signer_ids)

    @api.onchange("template_id", "set_sign_order")
    def _onchange_template_id(self):
        super()._onchange_template_id()

        for signer in self.signer_ids:
            signer.partner_id = signer.role_id.assign_contact_id.id
