# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    percentage_timesheet_report = fields.Selection(related="company_id.percentage_timesheet_report",
                                                   string="Percentage in Timesheet Report",
                                                   readonly=False, required=True)
