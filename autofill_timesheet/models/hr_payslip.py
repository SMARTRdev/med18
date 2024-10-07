# -*- coding: utf-8 -*-

from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_get_allocate_timesheet_line(self):
        return self.env["allocate.timesheet.line"].sudo().search(
            [("allocate_timesheet_id.date", ">=", self.date_from),
             ("allocate_timesheet_id.date", "<=", self.date_to),
             ("employee_id", "=", self.employee_id.id)], limit=1)

    def _action_create_account_move(self):
        result = super()._action_create_account_move()

        for payslip in self:
            if not payslip.move_id.line_ids:
                continue

            allocate_timesheet_line = payslip.action_get_allocate_timesheet_line()

            if allocate_timesheet_line:
                payslip.move_id.line_ids.write({"analytic_distribution": allocate_timesheet_line.analytic_distribution})
                allocate_timesheet_line.write({"has_payslip": True})

                allocate_timesheet = allocate_timesheet_line.allocate_timesheet_id
                if allocate_timesheet.state == "allocated":
                    if len(allocate_timesheet.line_ids) == len(
                            allocate_timesheet.line_ids.filtered(lambda l: l.has_payslip)):
                        allocate_timesheet.write({"state": "in_payroll"})
                    else:
                        allocate_timesheet.write({"state": "partial_payroll"})
                elif allocate_timesheet.state == "partial_payroll" and len(allocate_timesheet.line_ids) == len(
                        allocate_timesheet.line_ids.filtered(lambda l: l.has_payslip)):
                    allocate_timesheet.write({"state": "in_payroll"})
        return result

    def action_payslip_cancel(self):
        for payslip in self:
            if not payslip.move_id.line_ids:
                continue

            allocate_timesheet_line = payslip.action_get_allocate_timesheet_line()

            if allocate_timesheet_line:
                allocate_timesheet_line.write({"has_payslip": False})

                allocate_timesheet = allocate_timesheet_line.allocate_timesheet_id
                if allocate_timesheet.state == "partial_payroll" and len(
                        allocate_timesheet.line_ids.filtered(lambda l: l.has_payslip)) == 0:
                    allocate_timesheet.write({"state": "allocated"})
                elif allocate_timesheet.state == "in_payroll" and len(
                        allocate_timesheet.line_ids.filtered(lambda l: l.has_payslip)) > 0:
                    allocate_timesheet.write({"state": "partial_payroll"})

        return super().action_payslip_cancel()
