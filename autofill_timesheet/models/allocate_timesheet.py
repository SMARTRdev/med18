# -*- coding: utf-8 -*-

import calendar
import math
import random

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AllocateTimesheet(models.Model):
    _name = "allocate.timesheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Allocate Timesheets"

    name = fields.Char(compute="_compute_allocate_month_name", string="Name", index=True, store=True, readonly=True)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True, tracking=True)
    start_date_month = fields.Date(compute="_compute_allocate_month_name", string="Start Date Month", store=True,
                                   readonly=True)
    allocate_month = fields.Char(compute="_compute_allocate_month_name", string="Allocate Month", store=True,
                                 readonly=True)
    state = fields.Selection([
        ("not_allocated", "Not Allocated"),
        ("allocated", "Allocated"),
        ("partial_payroll", "Partial Payroll"),
        ("in_payroll", "In Payroll")], string="Status", required=True, default="not_allocated", index=True, copy=False,
        tracking=True)
    available_employee_ids = fields.Many2many("hr.employee", compute="_compute_available_employee_ids")
    employee_ids = fields.Many2many("hr.employee", string="Employees", required=True,
                                    domain="[('id','in',available_employee_ids)]")
    line_ids = fields.One2many("allocate.timesheet.line", "allocate_timesheet_id", string="Lines")
    copy_allocate_timesheet_id = fields.Many2one("allocate.timesheet", string="Copy Allocate Timesheet", tracking=True,
                                                 domain="[('date','<',start_date_month)]")
    company_id = fields.Many2one("res.company", string="Company", required=True, tracking=True,
                                 default=lambda self: self.env.company)

    @api.constrains("employee_ids")
    def _check_employees(self):
        for allocate_timesheet in self:
            end_date_month = allocate_timesheet.date.replace(
                day=calendar.monthrange(allocate_timesheet.date.year, allocate_timesheet.date.month)[1])
            if self.search_count(
                    [("id", "!=", allocate_timesheet.id), ("date", ">=", allocate_timesheet.start_date_month),
                     ("date", "<=", end_date_month),
                     ("employee_ids", "in", allocate_timesheet.employee_ids.ids)]) != 0:
                raise ValidationError(
                    _("Allocate timesheet for same month %s is already exists for some employees" % allocate_timesheet.allocate_month))

    @api.depends("date")
    def _compute_allocate_month_name(self):
        for allocate_timesheet in self:
            name = False
            start_date_month = False
            allocate_month = False
            if allocate_timesheet.date:
                start_date_month = allocate_timesheet.date.replace(day=1)
                allocate_month = allocate_timesheet.date.strftime("%B %Y")

                end_date_month = allocate_timesheet.date.replace(
                    day=calendar.monthrange(allocate_timesheet.date.year, allocate_timesheet.date.month)[1])
                allocate_timesheet_count = self.search_count(
                    [("id", "!=", allocate_timesheet._origin.id), ("date", ">=", allocate_timesheet.start_date_month),
                     ("date", "<=", end_date_month)], limit=1)

                name = f'{allocate_timesheet.date.strftime("%Y%m")}-{"%0*d" % (2, allocate_timesheet_count + 1)}'

            allocate_timesheet.start_date_month = start_date_month
            allocate_timesheet.allocate_month = allocate_month
            allocate_timesheet.name = name

    @api.depends("date", "company_id")
    def _compute_available_employee_ids(self):
        account_analytic_line_obj = self.env["account.analytic.line"]
        for allocate_timesheet in self:
            start_date_month = allocate_timesheet.start_date_month
            end_date_month = allocate_timesheet.date.replace(
                day=calendar.monthrange(allocate_timesheet.date.year, allocate_timesheet.date.month)[1])

            domain = [("company_id", "=", allocate_timesheet.company_id.id), ("is_timesheet", "=", True),
                      ("date", ">=", start_date_month), ("date", "<=", end_date_month)]

            employees = self.search([("id", "!=", allocate_timesheet._origin.id), ("date", ">=", start_date_month),
                                     ("date", "<=", end_date_month),
                                     ("company_id", "=", allocate_timesheet.company_id.id)]).employee_ids

            if employees:
                domain += [("employee_id", "not in", employees.ids)]

            allocate_timesheet.available_employee_ids = account_analytic_line_obj.search(domain).employee_id

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
            if line.state != "not_allocated":
                raise ValidationError(_("You cannot delete allocate timesheet when status is not 'Not Allocated'"))

        return super().unlink()

    def action_generate_allocation(self):
        if self.state != "not_allocated":
            return

        start_date_month = self.start_date_month
        end_date_month = self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1])

        account_analytic_lines = self.env["account.analytic.line"].search(
            [("is_timesheet", "=", True), ("date", ">=", start_date_month), ("date", "<=", end_date_month),
             ("employee_id", "in", self.employee_ids.ids)])
        lines = []
        employees = account_analytic_lines.employee_id
        for employee in employees:
            total_working_hours = 0
            total_time_off_hours = 0

            for account_analytic_line in account_analytic_lines.filtered(lambda a: a.employee_id == employee):
                total_working_hours += account_analytic_line.unit_amount
                if account_analytic_line.holiday_id:
                    total_time_off_hours += account_analytic_line.unit_amount

            work_hours = employee.contract_id.get_work_hours(start_date_month, end_date_month)
            total_actual_working_hours = 0
            for work_entry_type_id, hours in sorted(work_hours.items(), key=lambda x: x[1]):
                total_actual_working_hours += hours

            net_working_hours = total_working_hours - total_time_off_hours
            net_working_hours_percentage = 0
            if net_working_hours != 0:
                net_working_hours_percentage = ((total_actual_working_hours - total_time_off_hours)
                                                / net_working_hours) * 100

            line = self.line_ids.filtered(lambda l: l.employee_id == employee)
            vals = {
                "employee_id": employee.id,
                "total_actual_working_hours": total_actual_working_hours,
                "total_working_hours": total_working_hours,
                "total_time_off_hours": total_time_off_hours,
                "net_working_hours": net_working_hours,
                "net_working_hours_percentage": net_working_hours_percentage
            }
            if line:
                lines.append((1, line.id, vals))
            else:
                if self.copy_allocate_timesheet_id:
                    allocate_timesheet_line = self.copy_allocate_timesheet_id.line_ids.filtered(
                        lambda l: l.employee_id == employee)
                    if allocate_timesheet_line:
                        vals.update({"analytic_distribution": allocate_timesheet_line.analytic_distribution})

                vals.update({"employee_id": employee.id})
                lines.append((0, 0, vals))

        for line in self.line_ids.filtered(lambda l: l.employee_id not in employees):
            lines.append((3, line.id))

        self.write({"line_ids": lines})

    def action_update_allocate(self):
        if self.state != "not_allocated" or not self.copy_allocate_timesheet_id:
            return

        for line in self.line_ids:
            allocate_timesheet_line = self.copy_allocate_timesheet_id.line_ids.filtered(
                lambda l: l.employee_id == line.employee_id)
            if allocate_timesheet_line:
                line.write({"analytic_distribution": allocate_timesheet_line.analytic_distribution})

        return True

    def action_distribute(self):
        if self.state != "not_allocated":
            return

        if not self.line_ids:
            raise ValidationError(_("No there allocated to distribute"))

        for line in self.line_ids:
            line.action_distribute()

        self.write({"state": "allocated"})

        return self.action_get_timesheets()

    def action_reset_allocation(self):
        if self.state != "allocated":
            return

        start_date_month = self.start_date_month
        end_date_month = self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1])

        account_analytic_lines = self.env["account.analytic.line"].search(
            [("is_timesheet", "=", True), ("date", ">=", start_date_month), ("date", "<=", end_date_month),
             ("holiday_id", "=", False), ("employee_id", "in", self.employee_ids.ids)])
        if account_analytic_lines:
            account_analytic_lines.unlink()

        autofill_timesheet_lines = self.env["autofill.timesheet.line"].search(
            [("employee_id", "in", self.employee_ids.ids),
             ("autofill_timesheet_id.start_date_month", "=", start_date_month),
             ("autofill_timesheet_id.company_id", "=", self.company_id.id)])

        if autofill_timesheet_lines:
            autofill_timesheet_project = self.company_id.autofill_timesheet_project_id
            if not autofill_timesheet_project:
                raise ValidationError(_("check configuration to choose project before autofill timesheet"))

            leaves = self.env["hr.leave"].sudo().search(
                [("state", "not in", ["refuse", "validate"]), ("employee_id", "in", self.employee_ids.ids),
                 ("date_from", ">=", start_date_month), ("date_to", "<=", end_date_month),
                 ("company_id", "=", self.company_id.id)])

            if leaves:
                raise ValidationError(
                    _("Some employees '%s' have time off requests that are still under approval" % ",".join(
                        employee.display_name for employee in leaves.employee_id)))

            task = self.env["project.task"].search(
                [("project_id", "=", autofill_timesheet_project.id),
                 ("autofill_timesheet_month", "=", start_date_month),
                 "|", ("company_id", "=", False), ("company_id", "=", self.company_id.id)])

            if not task:
                task = self.env["project.task"].create({
                    "name": start_date_month.strftime("%B %Y"),
                    "project_id": autofill_timesheet_project.id,
                    "company_id": self.company_id.id,
                    "autofill_timesheet_month": start_date_month
                })

            for autofill_timesheet_line in autofill_timesheet_lines:
                autofill_timesheet_line.action_autofill(start_date_month, end_date_month, autofill_timesheet_project,
                                                        task)

        self.write({"state": "not_allocated"})

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


class AllocateTimesheetLine(models.Model):
    _name = "allocate.timesheet.line"
    _inherit = ["analytic.mixin"]
    _description = "Allocate Timesheet Line"

    allocate_timesheet_id = fields.Many2one("allocate.timesheet", string="Allocate Timesheet", ondelete="cascade",
                                            required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, readonly=True)
    total_actual_working_hours = fields.Float(string="Total Actual Working Hours", readonly=True)
    total_working_hours = fields.Float(string="Total Working Hours", readonly=True)
    total_time_off_hours = fields.Float(string="Total Time Off Hours", readonly=True)
    net_working_hours = fields.Float(string="Net Working Hours", readonly=True)
    net_working_hours_percentage = fields.Float(string="Net Working Hours (%)", readonly=True)
    allocate_percentage = fields.Float(compute="_compute_allocate_percentage", string="Allocate Percentage", store=True,
                                       readonly=True)
    has_payslip = fields.Boolean(string="Has Payslip", readonly=True)
    unlock = fields.Boolean(string="unLock")

    @api.constrains("allocate_percentage")
    def _check_allocate_percentage(self):
        for line in self.filtered(lambda l: l.analytic_distribution):
            if line.allocate_percentage != 100:
                raise ValidationError(
                    _("Allocate percentage is not equal to 100 for employee %s" % line.employee_id.display_name))

    @api.depends("analytic_distribution")
    def _compute_allocate_percentage(self):
        for line in self:
            allocate_percentage = 0
            if line.analytic_distribution:
                for account_ids, distribution in line.analytic_distribution.items():
                    allocate_percentage += distribution

            line.allocate_percentage = allocate_percentage

    def action_distribute(self):
        if self.has_payslip:
            return

        if self.net_working_hours_percentage != 100:
            raise ValidationError(
                _("Can not allocate the timesheets of the employee %s, \n"
                  "their are gaps between their working schedule and recorded timesheets") % self.employee_id.display_name)

        account_analytic_account_obj = self.env["account.analytic.account"]
        account_analytic_line_obj = self.env["account.analytic.line"]
        project_obj = self.env["project.project"]
        project_task_obj = self.env["project.task"]

        allocate_timesheet = self.allocate_timesheet_id
        start_date_month = allocate_timesheet.start_date_month
        end_date_month = start_date_month.replace(
            day=calendar.monthrange(start_date_month.year, start_date_month.month)[1])

        if self.allocate_percentage != 100:
            raise ValidationError(
                _("Allocate percentage is not equal to 100 for employee %s" % self.employee_id.display_name))

        project_ids = []
        analytic_distribution = self.analytic_distribution.items()
        analytic_distribution_hours = {}
        for account_id, distribution in analytic_distribution:
            analytic_account = account_analytic_account_obj.browse(int(account_id))
            if not analytic_account.project_ids:
                raise ValidationError(_("No found project for analytic account %s" % analytic_account.display_name))

            project_ids += analytic_account.project_ids.ids
            analytic_distribution_hours.update(
                {account_id: round(self.net_working_hours * (distribution / 100), 2)})

        account_analytic_lines = account_analytic_line_obj.search(
            [("employee_id", "=", self.employee_id.id), ("is_timesheet", "=", True), ("holiday_id", "=", False),
             ("date", ">=", start_date_month), ("date", "<=", end_date_month)], order="date")

        hours_only_allocation = allocate_timesheet.company_id.hours_only_allocation
        first_day_project_ids = project_ids.copy()
        for account_analytic_line in account_analytic_lines:
            remaining_unit_amount = account_analytic_line.unit_amount
            available_project_ids = project_ids.copy()

            for project_id in project_ids:
                available_project = project_obj.browse(project_id)
                if available_project.date_start and available_project.date and (
                        account_analytic_line.date < available_project.date_start or account_analytic_line.date > available_project.date):
                    available_project_ids.remove(project_id)

            if not available_project_ids:
                continue

            while remaining_unit_amount > 0:
                if not available_project_ids:
                    break

                available_first_day_project_ids = first_day_project_ids.copy()
                if first_day_project_ids:
                    for first_day_project_id in first_day_project_ids:
                        if first_day_project_id not in available_project_ids:
                            available_first_day_project_ids.remove(first_day_project_id)

                if available_first_day_project_ids:
                    project_id = random.choice(available_first_day_project_ids)
                else:
                    project_id = random.choice(available_project_ids)

                project = project_obj.browse(project_id)
                remaining_hours = analytic_distribution_hours[str(project.analytic_account_id.id)]

                task = project_task_obj.search(
                    [("project_id", "=", project_id), ("autofill_timesheet_month", "=", start_date_month)])

                if not task:
                    task = project_task_obj.create({
                        "name": start_date_month.strftime("%B %Y"),
                        "project_id": project_id,
                        "autofill_timesheet_month": start_date_month
                    })

                vals = {
                    "project_id": project_id,
                    "task_id": task.id
                }

                if hours_only_allocation and remaining_hours <= remaining_unit_amount:
                    decimal_number, number_remaining_hours = math.modf(remaining_hours)
                    if decimal_number != 0:
                        if decimal_number > 0.5:
                            old_remaining_hours = remaining_hours
                            remaining_hours = math.ceil(old_remaining_hours)
                        else:
                            old_remaining_hours = remaining_hours
                            remaining_hours = math.floor(old_remaining_hours)

                        analytic_distribution_hours[str(project.analytic_account_id.id)] = remaining_hours

                        if old_remaining_hours > remaining_hours:
                            for key, analytic_distribution_hour in analytic_distribution_hours.items():
                                if key != str(
                                        project.analytic_account_id.id) and analytic_distribution_hour > decimal_number:
                                    analytic_distribution_hours[key] = round(
                                        analytic_distribution_hours[key] + decimal_number, 2)

                new_account_analytic_line = False
                if (remaining_hours > remaining_unit_amount) and (
                        len(first_day_project_ids) <= 1 or len(available_project_ids) == 1):
                    remaining_unit_amount = 0
                    analytic_distribution_hours[
                        str(project.analytic_account_id.id)] = round(
                        remaining_hours - account_analytic_line.unit_amount, 2)

                    if project_id in first_day_project_ids:
                        first_day_project_ids.remove(project_id)
                else:
                    new_unit_amount = remaining_hours
                    if len(first_day_project_ids) > 1 and remaining_hours > 1:
                        if remaining_hours > 1:
                            new_unit_amount = 1

                    if project.id in first_day_project_ids:
                        first_day_project_ids.remove(project.id)

                    vals.update({
                        "unit_amount": new_unit_amount
                    })

                    if remaining_hours > remaining_unit_amount:
                        analytic_distribution_hours[
                            str(project.analytic_account_id.id)] = round(remaining_hours - new_unit_amount, 2)
                    else:
                        del analytic_distribution_hours[str(project.analytic_account_id.id)]
                        for delete_project in project.analytic_account_id.project_ids:
                            project_ids.remove(delete_project.id)

                            if delete_project.id in available_project_ids:
                                available_project_ids.remove(delete_project.id)

                    remaining_unit_amount = round(account_analytic_line.unit_amount - new_unit_amount, 2)
                    if remaining_unit_amount > 0:
                        new_account_analytic_line = account_analytic_line.copy()
                        new_account_analytic_line.write({"unit_amount": remaining_unit_amount})

                account_analytic_line.write(vals)

                if new_account_analytic_line:
                    account_analytic_line = new_account_analytic_line

        return True
