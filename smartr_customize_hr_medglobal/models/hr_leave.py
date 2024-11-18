# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    required_document = fields.Boolean(compute="_compute_required_document", string="Required Document")

    @api.depends("holiday_status_id", "number_of_days")
    def _compute_required_document(self):
        for leave in self:
            required_document = False
            required_document_days = leave.holiday_status_id.required_document_days
            if leave.leave_type_support_document and leave.number_of_days > required_document_days:
                required_document = True
            leave.required_document = required_document

    def write(self, vals):
        hr_payslip_obj = self.env["hr.payslip"].sudo()
        for leave in self:
            if hr_payslip_obj.search_count([
                ("employee_id", "=", leave.employee_id.id),
                ("date_from", "<=", leave.date_to),
                ("date_to", ">=", leave.date_from),
                ("state", "in", ["done", "paid"])
            ]) != 0:
                raise ValidationError(_("You can't edit a time off when payslip is done."))

        return super().write(vals)
