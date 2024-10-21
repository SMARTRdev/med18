# -*- coding: utf-8 -*-

from odoo import models, fields


class HRDepartment(models.Model):
    _inherit = "hr.department"

    department_function_id = fields.Many2one("hr.department.function", string="Department Function")
