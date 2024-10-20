# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ApprovalApprover(models.Model):
    _inherit = "approval.approver"

    importance_index = fields.Integer()


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def create(self, vals_list):
        res = super(ApprovalRequest, self).create(vals_list)
        for approver in res.approver_ids:
            if approver.importance_index == 0:
                res.approver_ids = [(3, approver.id)]
        return res

