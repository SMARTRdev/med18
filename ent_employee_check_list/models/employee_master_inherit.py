# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
import ast
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HREmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    entry_checklist = fields.Many2many('employee.checklist', 'entry_obj', 'check_hr_rel', 'hr_check_rel',
                                       string='Entry Process',
                                       domain="[('document_type', '=', 'entry'),('job_id', '=', job_id)]",
                                       readonly=True,
                                       help="Entry Checklist's")
    exit_checklist = fields.Many2many('employee.checklist', 'exit_obj', 'exit_hr_rel', 'hr_exit_rel',
                                      string='Exit Process',
                                      readonly=True,
                                      domain="[('document_type', '=', 'exit'),('job_id', '=', job_id)]")

    @api.depends('exit_checklist')
    def compute_exit_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'exit'),
                                                                     ('job_id', '=', each.job_id.id)])
            entry_len = len(each.exit_checklist)
            if total_len != 0:
                each.exit_progress = round((entry_len * 100) / total_len)

    @api.depends('entry_checklist')
    def compute_entry_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'entry'),
                                                                     ('job_id', '=', each.job_id.id)])
            entry_len = len(each.entry_checklist)
            if total_len != 0:
                each.entry_progress = round((entry_len * 100) / total_len)

    entry_progress = fields.Float(compute=compute_entry_progress, string='Entry Progress', store=True, default=0.0,
                                  help="Percentage of Entry Checklists's")
    exit_progress = fields.Float(compute=compute_exit_progress, string='Exit Progress', store=True, default=0.0,
                                 help="Percentage of Exit Checklists's")
    maximum_rate = fields.Integer(default=100)
    check_list_enable = fields.Boolean(invisible=True, copy=False)


class EmployeeMasterInherit(models.Model):
    _inherit = 'hr.employee'

    job_id = fields.Many2one(required=True)
    show_checklist = fields.Boolean(compute="compute_show_checklist")

    def create(self, vals_list):
        for val in vals_list:
            if 'job_id' in val:
                onboarding_plan = self.env['mail.activity.plan'].search([('job_id', '=', val['job_id']),
                                                                         ('plan_type', '=', 'entry')])
                if not onboarding_plan and not self.env.user._is_superuser():
                    job_position = self.env['hr.job'].browse(val['job_id'])
                    raise UserError(_("You have to add onboarding plan for job position {}.".format(job_position.name)))

        res = super().create(vals_list)
        for employee in res:
            onboarding_plan = self.env['mail.activity.plan'].search([('job_id', '=', employee.job_id.id),
                                                                     ('plan_type', '=', 'entry')], limit=1)
            if onboarding_plan:
                plan = self.env['mail.activity.schedule'].with_context({
                    'active_id': employee.id,
                    'active_ids': [employee.id],
                    'active_model': 'hr.employee'}).create({
                    'plan_id': onboarding_plan.id,
                    'plan_date_deadline': datetime.datetime.today()
                })
                plan.action_schedule_plan()
        return res

    def compute_show_checklist(self):
        for rec in self:
            scheduled_plans = self.env['mail.activity.schedule'].search([('res_model', '=', "hr.employee")])
            if len(scheduled_plans) == 0:
                rec.show_checklist = False
                return
            for scheduled_plan in scheduled_plans:
                is_present = rec.id in ast.literal_eval(scheduled_plan.res_ids)
                rec.show_checklist = is_present


class EmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    @api.model
    def create(self, vals):
        result = super(EmployeeDocumentInherit, self).create(vals)
        if result.document_name.document_type == 'entry':
            result.employee_ref.write({'entry_checklist': [(4, result.document_name.id)]})
        if result.document_name.document_type == 'exit':
            result.employee_ref.write({'exit_checklist': [(4, result.document_name.id)]})
        return result

    def unlink(self):
        for result in self:
            if result.document_name.document_type == 'entry':
                result.employee_ref.write({'entry_checklist': [(5, result.document_name.id)]})
            if result.document_name.document_type == 'exit':
                result.employee_ref.write({'exit_checklist': [(5, result.document_name.id)]})
        res = super(EmployeeDocumentInherit, self).unlink()
        return res


class EmployeeChecklistInherit(models.Model):
    _inherit = 'employee.checklist'

    entry_obj = fields.Many2many('hr.employee', 'entry_checklist', 'hr_check_rel', 'check_hr_rel',
                                 invisible=1)
    exit_obj = fields.Many2many('hr.employee', 'exit_checklist', 'hr_exit_rel', 'exit_hr_rel',
                                invisible=1)
