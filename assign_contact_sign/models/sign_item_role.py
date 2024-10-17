# -*- coding: utf-8 -*-

from odoo import models, fields


class SignItemParty(models.Model):
    _inherit = "sign.item.role"

    contact_type = fields.Selection([
        ("employee", "Employee"),
        ("employee_manager", "Employee Manager")], string="Contact Type")
    assign_contact_id = fields.Many2one("res.partner", string="Assign Contact")
