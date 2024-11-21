# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    percentage_timesheet_report = fields.Selection([
        ("allocation", "Allocation"),
        ("distribution", "Distribution")], string="Percentage in Timesheet Report", required=True, default="allocation")
