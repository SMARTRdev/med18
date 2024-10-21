# -*- coding: utf-8 -*-

from odoo import models, fields


class HRDepartmentFunction(models.Model):
    _name = "hr.department.function"
    _description = "HR Department Function"

    name = fields.Char(string="Name", required=True, translate=True)
