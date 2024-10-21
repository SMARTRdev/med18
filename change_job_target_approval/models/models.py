# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    planned_target = fields.Integer('Planned Target', readonly=True, default=0)
    original_planned = fields.Integer('Original Planned', compute='_compute_original_planned')

    def _compute_original_planned(self):
        for rec in self:
            rec.original_planned = rec.planned_target + rec.no_of_recruitment + rec.no_of_hired_employee


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[('modify_target', 'Modify Job Position planned target')])


class ApprovalJobLine(models.Model):
    _inherit = "approval.job.line"

    is_unplanned = fields.Boolean('Is Unplanned Job')
    new_planned_target = fields.Integer('New Planned Target')
    current_planned_target = fields.Integer('Current Planned Target',
                                            compute="_compute_current_planned_target",
                                            store=True)

    @api.depends('job_id')
    def _compute_current_planned_target(self):
        for rec in self:
            rec.current_planned_target = rec.job_id.planned_target


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    show_submit_button = fields.Boolean(compute="_compute_show_submit_button")
    show_modify_planned_job = fields.Boolean(compute="_compute_modify_planned_job")
    modify_planned_job_request_created = fields.Boolean()

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        for request in self:
            super(ApprovalRequest, request)._compute_request_status()
            if request.request_status == 'approved' and request.approval_type == 'modify_target':
                for job_line in request.job_line_ids:
                    job_line.job_id.planned_target = job_line.new_planned_target

            if request.request_status == 'approved' and request.approval_type == 'recruitment':
                for job_line in request.job_line_ids:
                    job_line.job_id.planned_target -= job_line.quantity

    @api.depends('job_line_ids')
    def _compute_show_submit_button(self):
        for rec in self:
            super(ApprovalRequest, rec)._compute_show_submit_button()
            if rec.approval_type == 'recruitment':
                for job in rec.job_line_ids:
                    if job.is_unplanned:
                        rec.show_submit_button = False
                        break

    @api.depends('job_line_ids')
    def _compute_modify_planned_job(self):
        for rec in self:
            rec.show_modify_planned_job = False

            if rec.modify_planned_job_request_created:
                return

            if rec.approval_type == 'recruitment':
                for job in rec.job_line_ids:
                    if job.is_unplanned:
                        rec.show_modify_planned_job = True
                        break

    def create_request_to_modify_planned_job(self):
        self.ensure_one()
        approval_category = self.env['approval.category'].search([('approval_type', '=', 'modify_target')])
        approval_category.ensure_one()
        jobs_ids = []
        jobs_names = []
        for job_line in self.job_line_ids:
            if job_line.is_unplanned:
                new_job = self.env['approval.job.line'].create(
                    {
                        'job_id': job_line.job_id.id,
                        'new_planned_target': job_line.quantity,
                        'department_id': job_line.department_id.id
                    }
                )
                jobs_ids.append(new_job.id)
                jobs_names.append(job_line.job_id.name)

        self.modify_planned_job_request_created = True

        return {
            'name': _('Modify Unplanned Job Request'),
            'view_mode': 'form',
            'res_model': 'approval.request',
            'views': [[False, 'form']],
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_line_ids': jobs_ids,
                'default_department_id': self.department_id.id,
                'default_category_id': approval_category.id,
                'default_name': "Unplanned Job Request for {}".format(jobs_names),
                'default_request_owner_id': self.env.user.id
            },
            'target': 'current',
        }
