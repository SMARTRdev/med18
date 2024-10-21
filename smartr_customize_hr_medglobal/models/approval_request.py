# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

#TODO Move this whole file to a general (BASE) model for the project (Client)


class ApprovalMainCategory(models.Model):
    _name = "approval.main.category"
    _description = "Approval Request Reject Reason"

    name = fields.Char(string="Name", translate=True, required=True)


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    main_category_id = fields.Many2one("approval.main.category", string="Main Category")


class ApprovalApprover(models.Model):
    _inherit = "approval.approver"

    importance_index = fields.Integer()


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    approvers_computed = fields.Boolean()

    def update_final_approvers(self):
        super(ApprovalRequest, self)._compute_approver_ids()

        for approver in self.approver_ids:
            approver.importance_index = 0

        self.update_approver_index_by_budget()
        self.update_approver_index_by_department()

        if self.category_id.manager_approval in ['approver', 'required']:
            employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
            manager = self.approver_ids.filtered(lambda a: a.user_id.id == employee.parent_id.user_id.id)
            if manager.id:
                manager.importance_index += 1

        for approver in self.approver_ids:
            if not approver.department_id.id and not approver.budget_id.id:
                approver.importance_index += 1

            if approver.importance_index == 0:
                self.approver_ids = [(3, approver.id)]

        self.approvers_computed = True

    @api.onchange('department_id', 'budget_id', 'request_owner_id', 'category_id')
    def reset_compute_approvers(self):
        for rec in self:
            rec.approvers_computed = False
            rec.show_submit_button = False

    # @api.depends('approvers_computed')
    # def _compute_show_submit_button(self):
    #     for rec in self:
    #         if not rec.approvers_computed:
    #             rec.show_submit_button = False
    #         else:
    #             rec.show_submit_button = True

    def action_confirm(self):
        if not self.approvers_computed:
            raise ValidationError("you should compute approvers to submit your request")

        if self.approval_type in ['recruitment', 'modify_target', 'new_job_position']:
            if len(self.job_line_ids) <= 0:
                raise ValidationError("you should add at least one job to submit your request")

            if self.approval_type in ['recruitment', 'modify_target']:
                for job in self.job_line_ids:
                    if not job.is_new and not job.job_id:
                        raise ValidationError("you should select the job title to submit your request")
                    elif job.is_new and len(job.job_title) <= 1:
                        raise ValidationError("you should add the title of the new job to submit your request ")

                    if not job.is_new and not job.job_id.has_job_description:
                        raise ValidationError("please add job description for job: {} to submit your request".format(job.job_id.name))

            if self.approval_type == 'new_job_position':
                for job in self.job_line_ids:
                    if not job.job_title:
                        raise ValidationError("you should add the title of the new job to submit your request ")

        return super(ApprovalRequest, self).action_confirm()