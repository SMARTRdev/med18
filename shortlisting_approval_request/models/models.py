# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    approval_type = fields.Selection(selection_add=[('short_listing', 'Shortlist Candidates')])
    get_candidates_from_stage_id = fields.Many2one("hr.recruitment.stage", string="Get Candidates from Stage")
    move_candidates_to_stage_id = fields.Many2one("hr.recruitment.stage", string="Move Candidates to Stage")


class ApprovalJobLine(models.Model):
    _inherit = "approval.job.line"

    job_applications = fields.Many2one('hr.job')


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    job_id = fields.Many2one("hr.job", "Jobs",
                             domain="[('department_id', '=', department_id), ('department_id', '!=', False)]")
    job_applications = fields.Many2one('hr.job')
    pre_short_listed_ids = fields.Many2many('hr.applicant', compute="_compute_pre_short_listed_ids")
    approved_short_listed_ids = fields.Many2many('hr.applicant', readonly=True)
    can_access_short_listed = fields.Boolean(compute="_compute_can_access_shortlisted")

    @api.onchange('department_id')
    def _compute_can_access_shortlisted(self):
        for rec in self:
            rec.can_access_short_listed = rec.env.user.has_group(
                'shortlisting_approval_request.group_access_shortlisted')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            required_approved = all(a.status == 'approved' for a in request.approver_ids.filtered('required'))
            minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(
                status_lst)
            if status_lst:
                if status_lst.count('approved') >= minimal_approver and required_approved:
                    is_short_listing = request.approval_type == 'short_listing'
                    has_access = request.can_access_short_listed
                    if is_short_listing and has_access:
                        self.approve_short_listing_candidates(request)

            super(ApprovalRequest, request)._compute_request_status()

    def approve_short_listing_candidates(self, rec):
        rec.approved_short_listed_ids = rec.pre_short_listed_ids
        for applicant in rec.pre_short_listed_ids:
            applicant.stage_id = self.category_id.move_candidates_to_stage_id.id

    @api.depends('job_id')
    def _compute_pre_short_listed_ids(self):
        for rec in self:
            if rec.approval_type == 'short_listing' and rec.can_access_short_listed:
                if rec.request_status == 'approved':
                    rec.pre_short_listed_ids = rec.approved_short_listed_ids
                else:
                    rec.pre_short_listed_ids = (self.env['hr.applicant']
                    .sudo().search(
                        [
                            ('department_id', '=', rec.department_id.id),
                            ('job_id', '=', rec.job_id.id),
                            ('stage_id', '=', self.category_id.get_candidates_from_stage_id.id)
                        ]))
            else:
                rec.sudo().write({"pre_short_listed_ids": False})
