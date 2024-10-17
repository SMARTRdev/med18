# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.addons.approvals.models.approval_category import CATEGORY_SELECTION


class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    has_budget = fields.Selection(CATEGORY_SELECTION, string="Has Budget", default="no", required=True)
    has_budget_line_no = fields.Selection(CATEGORY_SELECTION, string="Has Budget Line No.", default="no", required=True)


class ApprovalCategoryApprover(models.Model):
    _inherit = "approval.category.approver"

    budget_id = fields.Many2one("crossovered.budget", string="Budget")


class ApprovalApprover(models.Model):
    _inherit = "approval.approver"

    approver_action = fields.Char(string="Approver Action")
    budget_id = fields.Many2one("crossovered.budget", string="Budget", readonly=True)


class ApprovalRequest(models.Model):
    _inherit = "approval.request"

    has_budget = fields.Selection(related="category_id.has_budget")
    budget_id = fields.Many2one("crossovered.budget", string="Budget", tracking=True)
    date = fields.Datetime(default=fields.Datetime.now)
    has_budget_line_no = fields.Selection(related="category_id.has_budget_line_no")

    request_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')])

    def update_approver_index_by_budget(self):
        for approver in self.approver_ids:
            template = self.category_id.approver_ids.filtered(
                lambda temp_approver: temp_approver.user_id == approver.user_id)
            approver.budget_id = template.budget_id.id
            if template.budget_id == self.budget_id and self.budget_id:
                approver.importance_index += 1

    def _compute_is_request_owner(self):
        current_user = self.env.user
        for request in self:
            request.is_request_owner = (current_user == request.request_owner_id)