# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    documents_job_description_settings = fields.Boolean(related='company_id.documents_job_description_settings',
                                                        readonly=False, string="Job Description")
    job_description_folder_id = fields.Many2one('documents.document',
                                                related='company_id.job_description_folder_id',
                                                readonly=False, string="Job Description default workspace")
    job_description_tag_ids = fields.Many2many('documents.tag', 'job_description_tags_rel',
                                               related='company_id.job_description_tag_ids',
                                               readonly=False, string="Job Description Tags")


class ResCompany(models.Model):
    _inherit = "res.company"

    documents_job_description_settings = fields.Boolean(default=False)
    account_folder_id = fields.Many2one("documents.document", string="Job Description Workspace", check_company=True,
                                        default=lambda self: self.env.ref('documents.document_finance_folder',
                                                                          raise_if_not_found=False),
                                        domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)])
    job_description_folder_id = fields.Many2one(
        'documents.document',
        string="Approvals Workspace",
        default=lambda self: self.env.ref('add_job_description_attachment.documents_job_description_folder',
                                          raise_if_not_found=False),
        check_company=True,
        domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)])
    job_description_tag_ids = fields.Many2many('documents.tag', 'job_description_tags_rel')


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    is_job_description = fields.Boolean()


class HrJob(models.Model):
    _inherit = 'hr.job'

    has_job_description = fields.Boolean(compute="_compute_document_ids")

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids').filtered(lambda self: not self.emp_id)
        app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([
            '|',
            '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'hr.applicant':
                result[app_to_job[attachment.res_id]] |= attachment
            else:
                result[attachment.res_id] |= attachment

        for job in self:
            job.document_ids = result.get(job.id, False)
            job.documents_count = len(job.document_ids)
            doc_for_jb = self.env['documents.document'].search([('attachment_id', 'in', job.document_ids.ids),
                                                                ('is_job_description', '=', True)])
            if len(doc_for_jb) > 0:
                job.has_job_description = True
            else:
                job.has_job_description = False

    def action_upload_job_description_document(self):
        return {
            'type': 'ir.actions.act_window',
            "name": _("Upload Job Description"),
            "view_mode": 'form',
            "res_model": "documents.document",
            "context": {
                "default_res_model": "hr.job",
                "default_res_id": self.id,
                "default_folder_id": self.company_id.job_description_folder_id.id,
                "default_tag_ids": self.company_id.job_description_tag_ids.ids,
                "default_is_job_description": True
            },
            "view_id": self.env.ref("add_job_description_attachment.view_document_upload_job_description_form").id,
            "target": "new"
        }
