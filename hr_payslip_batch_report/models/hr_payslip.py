# -*- coding: utf-8 -*-

from odoo import models, fields


class HRPayslip(models.Model):
    _inherit = "hr.payslip"

    comments = fields.Char(string="Comments")
    payment_by_hq = fields.Boolean(related="contract_id.payment_by_hq", string="Payment by HQ", readonly=True,
                                   store=True)

    def get_allocate_timesheet_project_codes(self):
        project_codes = ""
        allocate_timesheet_line = self.action_get_allocate_timesheet_line()
        account_analytic_account_obj = self.env["account.analytic.account"]
        if allocate_timesheet_line and allocate_timesheet_line.analytic_distribution:
            for account_id, distribution in allocate_timesheet_line.analytic_distribution.items():
                analytic_account = account_analytic_account_obj.browse(int(account_id))
                if project_codes:
                    project_codes += ","

                project_codes += f'{analytic_account.display_name}:{distribution}'
                
        return project_codes