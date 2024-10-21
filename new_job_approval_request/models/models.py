# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[('new_job_position', 'New Job Position')])


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    show_submit_button = fields.Boolean(compute="_compute_show_submit_button")
    show_create_new_job = fields.Boolean(compute="_compute_create_new_job")
    new_job_request_created = fields.Boolean()

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        for request in self:
            super(ApprovalRequest, request)._compute_request_status()
            if request.request_status == 'approved' and request.approval_type == 'new_job_position':
                for job_line in request.job_line_ids:
                    job = self.env['hr.job'].create({
                        'name': job_line.job_title,
                        'parent_id': job_line.parent_id.id,
                        'department_id': job_line.department_id.id,
                        'planned_target': job_line.planned_target
                    })
                    job_line.write({"job_id": job.id})

    @api.depends('job_line_ids')
    def _compute_create_new_job(self):
        for rec in self:
            rec.show_create_new_job = False

            if rec.new_job_request_created:
                return

            if rec.approval_type == 'recruitment':
                for job in rec.job_line_ids:
                    if job.is_new:
                        rec.show_create_new_job = True
                        job.job_id = False
                        break
                    else:
                        job.job_title = False

    @api.depends('job_line_ids')
    def _compute_show_submit_button(self):
        for rec in self:
            super(ApprovalRequest, rec)._compute_show_submit_button()
            if rec.approval_type == 'recruitment':
                for job in rec.job_line_ids:
                    if job.is_new:
                        rec.show_submit_button = False
                        break

    def create_request_for_new_job(self):
        self.ensure_one()
        approval_category = self.env['approval.category'].search([('approval_type', '=', 'new_job_position')])
        approval_category.ensure_one()
        jobs_ids = []
        jobs_names = []
        for job_line in self.job_line_ids:
            if job_line.is_new:
                new_job = self.env['approval.job.line'].create(
                    {
                        'job_title': job_line.job_title,
                        'department_id': job_line.department_id.id,
                    }
                )
                jobs_ids.append(new_job.id)
                jobs_names.append(job_line.job_title)

        self.new_job_request_created = True

        return {
            'name': _('New Job Position Request'),
            'view_mode': 'form',
            'res_model': 'approval.request',
            'views': [[False, 'form']],
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_line_ids': jobs_ids,
                'default_department_id': self.department_id.id,
                'default_category_id': approval_category.id,
                'default_name': "New Job Position Request for {}".format(jobs_names),
                'default_request_owner_id': self.env.user.id
            },
            'target': 'current',
        }


class ApprovalJobLine(models.Model):
    _inherit = "approval.job.line"

    is_new = fields.Boolean('Is New')
    job_title = fields.Char()
    parent_id = fields.Many2one("hr.job", "Manager Role")
    planned_target = fields.Integer('Planned Target')

    def action_get_job_position(self):
        if not self.job_id:
            return

        form = self.env.ref("hr.view_hr_job_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.job",
            "view_mode": "form",
            "res_id": self.job_id.id,
            "views": [(form.id, "form")],
            "view_id": form.id,
        }
