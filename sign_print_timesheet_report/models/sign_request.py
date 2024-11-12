# -*- coding: utf-8 -*-

from odoo import models, fields


class SignRequest(models.Model):
    _inherit = "sign.request"

    timesheet_report_employee_id = fields.Many2one("hr.employee", string="Employee (Timesheet Report)", readonly=True,
                                                   copy=False)
    timesheet_report_date = fields.Date(string="Timesheet Report Date", readonly=True, copy=False)
