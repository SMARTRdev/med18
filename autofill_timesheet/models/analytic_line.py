# -*- coding: utf-8 -*-

import calendar

from odoo import models, fields, api


class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    autofill_timesheet_month = fields.Date(string="Autofill Timesheet Month", readonly=True, copy=False)
    hours_percentage_month_project = fields.Float(compute="_compute_hours_percentage_month_project",
                                                  string="Hours Project Percentage", store=True, readonly=True,
                                                  group_operator="avg")

    @api.depends("employee_id", "project_id", "unit_amount", "date", "is_timesheet")
    def _compute_hours_percentage_month_project(self):
        for analytic_line in self:
            hours_percentage_month_project = 0

            if analytic_line.is_timesheet and analytic_line.project_id and analytic_line.unit_amount and analytic_line.date:
                start_date_month = analytic_line.date.replace(day=1)
                end_date_month = analytic_line.date.replace(
                    day=calendar.monthrange(analytic_line.date.year, analytic_line.date.month)[1])

                total_hours = sum(line.unit_amount for line in self.search(
                    [("is_timesheet", "=", True), ("date", ">=", start_date_month), ("date", "<=", end_date_month),
                     ("employee_id", "=", analytic_line.employee_id.id)]))

                total_hours_project = sum(line.unit_amount for line in self.search(
                    [("is_timesheet", "=", True), ("date", ">=", start_date_month), ("date", "<=", end_date_month),
                     ("employee_id", "=", analytic_line.employee_id.id),
                     ("project_id", "=", analytic_line.project_id.id)]))

                hours_percentage_month_project = round(total_hours_project / total_hours, 2)

            analytic_line.hours_percentage_month_project = hours_percentage_month_project
