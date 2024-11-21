# -*- coding: utf-8 -*-

from odoo import models, fields


class HRPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    currency_rate = fields.Float(string="Currency Rate")

    def action_get_sign_request_ids(self):
        return self.env["sign.request"].search(
            [("timesheet_report_employee_id", "in", self.slip_ids.employee_id.ids),
             ("timesheet_report_date", ">=", self.date_start),
             ("timesheet_report_date", "<=", self.date_end)]).ids
