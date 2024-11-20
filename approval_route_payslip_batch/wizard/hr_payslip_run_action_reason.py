# -*- coding: utf-8 -*-

from odoo import models, fields


class HrPayslipRunActionReasonWizard(models.TransientModel):
    _name = "hr.payslip.run.action.reason"
    _description = "Payslip Batch Action Reason"

    action_type = fields.Selection([
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="Type", required=True)
    action_reason = fields.Text(string="Reason", required=True)

    def action_apply(self):
        payslip_batch = self.env["hr.payslip.run"].browse(self._context.get("active_id"))

        self.env["hr.payslip.run.action.reason.line"].create({
            "payslip_run_id": payslip_batch.id,
            "type": self.action_type,
            "reason": self.action_reason
        })

        if self.action_type == "approved":
            payslip_batch.action_approve()
        else:
            payslip_batch.write({"state": "draft"})

        return True
