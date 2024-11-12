# -*- coding: utf-8 -*-

import calendar
import datetime
import math

from dateutil.relativedelta import relativedelta
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AutofillTimesheet(models.Model):
    _name = "autofill.timesheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Autofill Timesheets"

    name = fields.Char(compute="_compute_autofill_month_name", string="Name", index=True, store=True, readonly=True)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True, tracking=True)
    start_date_month = fields.Date(compute="_compute_autofill_month_name", string="Start Date Month", store=True,
                                   readonly=True)
    autofill_month = fields.Char(compute="_compute_autofill_month_name", string="Autofill Month", store=True,
                                 readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed")], string="Status", required=True, default="draft", index=True, copy=False,
        tracking=True)
    available_employee_ids = fields.Many2many("hr.employee", compute="_compute_available_employee_ids")
    employee_ids = fields.Many2many("hr.employee", string="Employees", required=True,
                                    domain="[('id','in',available_employee_ids)]")
    line_ids = fields.One2many("autofill.timesheet.line", "autofill_timesheet_id", string="Lines")
    company_id = fields.Many2one("res.company", string="Company", required=True, tracking=True,
                                 default=lambda self: self.env.company)
    autofill_custom_hours_employees = fields.Boolean(related="company_id.autofill_custom_hours_employees")

    @api.constrains("employee_ids")
    def _check_employees(self):
        for autofill_timesheet in self:
            end_date_month = autofill_timesheet.date.replace(
                day=calendar.monthrange(autofill_timesheet.date.year, autofill_timesheet.date.month)[1])
            if self.search_count(
                    [("id", "!=", autofill_timesheet.id), ("date", ">=", autofill_timesheet.start_date_month),
                     ("date", "<=", end_date_month),
                     ("employee_ids", "in", autofill_timesheet.employee_ids.ids)]) != 0:
                raise ValidationError(
                    _("Autofill timesheet for same month %s is already exists for some employees" % autofill_timesheet.autofill_month))

    @api.depends("date")
    def _compute_autofill_month_name(self):
        for autofill_timesheet in self:
            name = False
            start_date_month = False
            autofill_month = False
            if autofill_timesheet.date:
                start_date_month = autofill_timesheet.date.replace(day=1)
                autofill_month = autofill_timesheet.date.strftime("%B %Y")

                end_date_month = autofill_timesheet.date.replace(
                    day=calendar.monthrange(autofill_timesheet.date.year, autofill_timesheet.date.month)[1])
                autofill_timesheet_count = self.search_count(
                    [("id", "!=", autofill_timesheet._origin.id), ("date", ">=", autofill_timesheet.start_date_month),
                     ("date", "<=", end_date_month)], limit=1)

                name = f'{autofill_timesheet.date.strftime("%Y%m")}-{"%0*d" % (2, autofill_timesheet_count + 1)}'

            autofill_timesheet.start_date_month = start_date_month
            autofill_timesheet.autofill_month = autofill_month
            autofill_timesheet.name = name

    @api.depends("date", "company_id")
    def _compute_available_employee_ids(self):
        employee_obj = self.env["hr.employee"]

        for autofill_timesheet in self:
            start_date_month = autofill_timesheet.start_date_month
            end_date_month = autofill_timesheet.date.replace(
                day=calendar.monthrange(autofill_timesheet.date.year, autofill_timesheet.date.month)[1])

            employees = self.search([("id", "!=", autofill_timesheet._origin.id), ("date", ">=", start_date_month),
                                     ("date", "<=", end_date_month),
                                     ("company_id", "=", autofill_timesheet.company_id.id)]).employee_ids

            domain = [("company_id", "=", autofill_timesheet.company_id.id),
                      ("exclude_timesheets_autofill", "=", False)]
            if employees:
                domain += [("id", "not in", employees.ids)]

            autofill_timesheet.available_employee_ids = employee_obj.search(domain)

    @api.onchange("date")
    def onchange_date(self):
        if self.employee_ids and any(employee not in self.available_employee_ids for employee in self.employee_ids):
            self.employee_ids = False

    @api.onchange("company_id")
    def onchange_company(self):
        if self.employee_ids and any(employee not in self.available_employee_ids for employee in self.employee_ids):
            self.employee_ids = False

    def unlink(self):
        for line in self:
            if line.state == "confirmed":
                raise ValidationError(_("You cannot delete autofill timesheet when status is confirmed'"))

        return super().unlink()

    def get_actual_working_hours(self, employee):
        actual_working_hours = 0

        date = self.start_date_month
        end_date_month = date.replace(day=calendar.monthrange(date.year, date.month)[1])

        resource_calendar = employee.contract_id.resource_calendar_id
        if resource_calendar:
            contracts = self.env["hr.contract"].search(
                [("employee_id", "=", employee.id), ("state", "in", ["open", "close"]), "|",
                 ("date_end", "=", False), ("date_end", ">=", date)])

            if len(contracts) == 1 and date < contracts.date_start:
                date = contracts.date_start

            while date <= end_date_month:
                if not contracts.filtered(lambda c: c.date_start <= date and (not c.date_end or c.date_end >= date)):
                    date += datetime.timedelta(1)
                    continue

                attendance_lines = resource_calendar.attendance_ids.filtered(
                    lambda a: not a.week_type or int(a.week_type) == self.env[
                        "resource.calendar.attendance"].get_week_type(date))

                if attendance_lines:
                    attendance_lines = attendance_lines.filtered(
                        lambda a: int(a.dayofweek) == date.weekday() and a.day_period != "lunch")

                if attendance_lines:
                    actual_working_hours += sum(attendance_line.duration_hours for attendance_line in attendance_lines)

                date += datetime.timedelta(1)

        return actual_working_hours

    def action_generate_autofill(self):
        lines = []
        for employee in self.employee_ids:
            line = self.line_ids.filtered(lambda l: l.employee_id == employee)

            if line:
                lines.append((4, line.id))
            else:
                working_hours = self.get_actual_working_hours(employee)
                lines.append((0, 0, {
                    "employee_id": employee.id,
                    "actual_working_hours": working_hours,
                    "working_hours_percentage": 100,
                    "working_hours": working_hours
                }))

        for line in self.line_ids.filtered(lambda l: l.employee_id not in self.employee_ids):
            lines.append((3, line.id))

        self.write({"line_ids": lines})

    def action_confirm(self):
        if self.state != "draft":
            return

        if not self.line_ids:
            raise ValidationError(_("No there employees to autofill"))

        autofill_timesheet_project = self.company_id.autofill_timesheet_project_id
        if not autofill_timesheet_project:
            raise ValidationError(_("check configuration to choose project before autofill timesheet"))

        start_date_month = self.start_date_month
        end_date_month = self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1])

        leaves = self.env["hr.leave"].sudo().search(
            [("state", "not in", ["refuse", "validate"]), ("employee_id", "in", self.employee_ids.ids),
             ("date_from", ">=", start_date_month), ("date_to", "<=", end_date_month),
             ("company_id", "=", self.company_id.id)])

        if leaves:
            raise ValidationError(
                _("Some employees '%s' have time off requests that are still under approval" % ",".join(
                    employee.display_name for employee in leaves.employee_id)))

        task = self.env["project.task"].search(
            [("project_id", "=", autofill_timesheet_project.id), ("autofill_timesheet_month", "=", start_date_month),
             "|", ("company_id", "=", False), ("company_id", "=", self.company_id.id)])

        if not task:
            task = self.env["project.task"].create({
                "name": start_date_month.strftime("%B %Y"),
                "project_id": autofill_timesheet_project.id,
                "company_id": self.company_id.id,
                "autofill_timesheet_month": start_date_month
            })

        for line in self.line_ids:
            line.action_autofill(start_date_month, end_date_month, autofill_timesheet_project, task)

        self.write({"state": "confirmed"})

        return self.action_get_timesheets()

    def action_get_timesheets(self):
        start_date_month = self.start_date_month
        end_date_month = self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1])
        domain = [("is_timesheet", "=", True), ("date", ">=", start_date_month),
                  ("date", "<=", end_date_month),
                  ("employee_id", "in", self.employee_ids.ids)]
        action = self.env["ir.actions.act_window"]._for_xml_id("hr_timesheet.timesheet_action_all")

        action.pop("id", None)
        action.pop("xml_id", None)
        action.pop("display_name", None)
        action.update({
            "name": _("Timesheets"),
            "domain": domain,
            "view_mode": "list,grid,kanban,pivot,graph,form",
            "mobile_view_mode": "grid",
            "views": [
                [self.env.ref("hr_timesheet.timesheet_view_tree_user").id, "list"],
                [self.env.ref("timesheet_grid.timesheet_view_grid_by_employee_editable_manager").id, "grid"],
                [self.env.ref("hr_timesheet.view_kanban_account_analytic_line").id, "kanban"],
                [self.env.ref("hr_timesheet.view_hr_timesheet_line_pivot").id, "pivot"],
                [self.env.ref("hr_timesheet.view_hr_timesheet_line_graph_all").id, "graph"],
                [self.env.ref("hr_timesheet.hr_timesheet_line_form").id, "form"],
            ],
        })

        action["context"] = {
            "group_expand": True,
            "is_timesheet": 1,
            "grid_anchor": start_date_month
        }

        return action

    def action_reset_to_draft(self):
        if self.state != "confirmed":
            return

        return self.write({"state": "draft"})


class AutofillTimesheetLine(models.Model):
    _name = "autofill.timesheet.line"
    _description = "Autofill Timesheet Line"

    autofill_timesheet_id = fields.Many2one("autofill.timesheet", string="Autofill Timesheet", ondelete="cascade",
                                            required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, readonly=True)
    actual_working_hours = fields.Float(string="Actual Working Hours", readonly=True)
    working_hours_percentage = fields.Float(string="Working Hours (%)")
    working_hours = fields.Float(string="Working Hours")
    daily_distribution = fields.Boolean(string="Daily Distribution")

    @api.onchange("working_hours_percentage")
    def onchange_working_hours_percentage(self):
        self.working_hours = self.actual_working_hours * self.working_hours_percentage / 100

    def _prepare_timesheet(self, project, task, date, remaining_hours):
        return {
            "employee_id": self.employee_id.id,
            "project_id": project.id,
            "company_id": self.autofill_timesheet_id.company_id.id,
            "task_id": task.id,
            "date": date,
            "unit_amount": remaining_hours,
            "is_timesheet": True
        }

    def action_autofill(self, start_date, end_date, project, task):
        contracts = self.env["hr.contract"].search(
            [("employee_id", "=", self.employee_id.id), ("state", "in", ["open", "close"]), "|",
             ("date_end", "=", False), ("date_end", ">=", start_date)])

        if not contracts:
            raise ValidationError(_("Employee %s not have contract" % self.employee_id.display_name))

        if len(contracts) == 1 and start_date < contracts.date_start:
            start_date = contracts.date_start

        for contract in contracts:
            if contract.date_end and contract.date_end < end_date:
                contract._recompute_work_entries(start_date, contract.date_end)
            elif start_date < contract.date_start:
                contract._recompute_work_entries(contract.date_start, end_date)
            else:
                contract._recompute_work_entries(start_date, end_date)

        account_analytic_line_obj = self.env["account.analytic.line"]

        remaining_working_hours = self.working_hours
        if remaining_working_hours <= 0:
            raise ValidationError(_("Working hours must be positive for employee %s") % self.employee_id.display_name)

        if remaining_working_hours > self.actual_working_hours:
            raise ValidationError(
                _("Working hours must be less than or equal to actual working hours for employee %s") % self.employee_id.display_name)

        resource_calendar = self.employee_id.contract_id.resource_calendar_id
        if not resource_calendar:
            raise ValidationError(_("No there working hours Schedule for employee %s" % self.employee_id.display_name))

        hours_day = 0
        if self.daily_distribution:
            number_working_days = 0
            date = start_date
            while date <= end_date:
                attendance_lines = resource_calendar.attendance_ids.filtered(
                    lambda a: not a.week_type or int(a.week_type) == self.env[
                        "resource.calendar.attendance"].get_week_type(date))
                if attendance_lines:
                    attendance_lines = attendance_lines.filtered(
                        lambda a: int(a.dayofweek) == date.weekday() and a.day_period != "lunch")

                if attendance_lines:
                    number_working_days += 1

                date += datetime.timedelta(1)

            hours_day = math.ceil(remaining_working_hours / number_working_days)

        hr_work_entry_obj = self.env["hr.work.entry"]
        while start_date <= end_date and remaining_working_hours != 0:
            if not contracts.filtered(
                    lambda c: c.date_start <= start_date and (not c.date_end or c.date_end >= start_date)):
                start_date += datetime.timedelta(1)
                continue

            attendance_lines = resource_calendar.attendance_ids.filtered(
                lambda a: not a.week_type or int(a.week_type) == self.env[
                    "resource.calendar.attendance"].get_week_type(start_date))
            if attendance_lines:
                attendance_lines = attendance_lines.filtered(
                    lambda a: int(a.dayofweek) == start_date.weekday() and a.day_period != "lunch")

            if attendance_lines:
                working_hours = sum(attendance_line.duration_hours for attendance_line in attendance_lines)

                if self.daily_distribution:
                    working_hours = hours_day

                total_hours_timesheet = sum(account_analytic_line.unit_amount for account_analytic_line in
                                            account_analytic_line_obj.search(
                                                [("is_timesheet", "=", True), ("employee_id", "=", self.employee_id.id),
                                                 ("date", "=", start_date)]))

                remaining_hours = working_hours - total_hours_timesheet
                if remaining_hours > 0:
                    if remaining_hours > remaining_working_hours:
                        remaining_hours = remaining_working_hours
                        remaining_working_hours = 0
                    else:
                        remaining_working_hours -= working_hours

                    account_analytic_line_obj.create(
                        self._prepare_timesheet(project, task, start_date, remaining_hours))

                    if working_hours != 0:
                        work_entry = hr_work_entry_obj.search([
                            ("employee_id", "=", self.employee_id.id),
                            ("date_stop", ">=", start_date),
                            ("date_start", "<=", start_date),
                            ("state", "!=", "validated")], limit=1)
                        if work_entry:
                            work_entry.date_stop = work_entry.date_start + relativedelta(
                                hours=remaining_hours + total_hours_timesheet)

            start_date += datetime.timedelta(1)

        if start_date <= end_date:
            work_entries = hr_work_entry_obj.search([
                ("employee_id", "=", self.employee_id.id),
                ("date_stop", ">=", start_date),
                ("date_start", "<=", end_date)])
            if work_entries:
                work_entries.unlink()
