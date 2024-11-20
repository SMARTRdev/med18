# -*- coding: utf-8 -*-

from odoo import fields, models, api


class HrPayslipRun(models.Model):
    _name = "hr.payslip.run"
    _inherit = ["hr.payslip.run", "approval.route.document"]

    use_approval_route = fields.Selection(string="Use Approval Route",
                                          related="company_id.use_approval_route_payslip_batch")
    approval_route_id = fields.Many2one(readonly=True, check_company=True)
    state = fields.Selection(
        selection_add=[("under_approval", "Under Approval"), ("approved", "Approved"), ("close",), ],
        ondelete={"approved": "set verify"})
    can_approve = fields.Boolean("Can Approve", compute="_compute_can_approve")
    action_reason_line_ids = fields.One2many("hr.payslip.run.action.reason.line", "payslip_run_id",
                                             string="Action Reason Lines", readonly=True)

    @api.depends_context("uid")
    @api.depends("approval_route_id", "current_approval_stage_id")
    def _compute_can_approve(self):
        for payslip_batch in self:
            can_approve = True
            if payslip_batch.use_approval_route != "no" and payslip_batch.approval_route_id and payslip_batch.is_under_approval:
                can_approve = payslip_batch.is_current_approver

            payslip_batch.can_approve = can_approve

    def action_submit_approval(self):
        payslip_batches = self.filtered(lambda p: p.state == "verify")
        for payslip_batch in payslip_batches:
            if payslip_batch.use_approval_route != "no" and payslip_batch.approval_route_id:
                payslip_batch.generate_approval_route()
                if payslip_batch.next_approval_stage_id:
                    payslip_batch._action_send_to_approve()

        payslip_batches.write({"state": "under_approval"})

    def action_approve(self):
        for payslip_batch in self:
            if payslip_batch.use_approval_route != "no" and payslip_batch.approval_route_id and payslip_batch.is_under_approval:
                payslip_batch._action_approve()
                if self._is_fully_approved():
                    payslip_batch.write({"state": "approved"})
            else:
                payslip_batch.write({"state": "approved"})

    def action_approve_with_comment(self):
        if not self.can_approve or self.state != "under_approval":
            return

        action = self.sudo().env.ref("approval_route_payslip_batch.action_hr_payslip_run_action_reason_wizard")
        result = action.read()[0]

        result["context"] = {"default_action_type": "approved"}

        return result

    def action_reject(self):
        if not self.can_approve or self.state != "under_approval":
            return

        action = self.sudo().env.ref("approval_route_payslip_batch.action_hr_payslip_run_action_reason_wizard")
        result = action.read()[0]

        result["context"] = {"default_action_type": "rejected"}

        return result

    def action_draft(self):
        self._clear_approval_stages()

        super().action_draft()


class HrPayslipRunActionReasonLine(models.Model):
    _name = "hr.payslip.run.action.reason.line"
    _description = "Payslip Batch Action Reason Line"

    payslip_run_id = fields.Many2one("hr.payslip.run", string="Payslip Batch", required=True, readonly=True,
                                     ondelete="cascade")
    type = fields.Selection([
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="Type", required=True)
    reason = fields.Text(string="Reason", readonly=True)
