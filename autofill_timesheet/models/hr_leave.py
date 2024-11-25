# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def check_allocate_timesheet(self):
        if self.env["allocate.timesheet.line"].sudo().search_count(
                [("allocate_timesheet_id.date", ">=", self.date_from),
                 ("allocate_timesheet_id.date", "<=", self.date_to),
                 ("allocate_timesheet_id.state", "!=", "not_allocated"),
                 ("employee_id", "=", self.employee_id.id)], limit=1) > 0:
            raise ValidationError(
                _("You cannot create or change or remove Time Offs in a period of a confirmed Allocation"))

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.check_allocate_timesheet()

        return res

    def write(self, vals):
        if "payslip_state" not in vals:
            for leave in self:
                leave.check_allocate_timesheet()

        return super().write(vals)

    def unlink(self):
        for leave in self:
            leave.check_allocate_timesheet()

        return super().unlink()
