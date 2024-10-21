# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLeave(models.Model):
    _inherit = "hr.leave.type"

    required_document_days = fields.Float(string="Required Document Days")
