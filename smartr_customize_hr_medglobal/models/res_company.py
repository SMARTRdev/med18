# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    restrict_employees = fields.Boolean(string="Restrict Employees")