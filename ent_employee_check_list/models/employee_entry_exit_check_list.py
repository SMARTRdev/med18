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

from odoo import models, fields, api


class EmployeeEntryDocuments(models.Model):
    _name = 'employee.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"
    _order = 'sequence'

    name = fields.Char(string='Name', related="activity_temp_id.summary", required=1, help="Checklist Name")
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')], string='Checklist Type', help='Type of Checklist',
                                     related="plan_id.plan_type")
    sequence = fields.Integer('Sequence')
    plan_id = fields.Many2one("mail.activity.plan", inverse_name="checklist_ids")
    activity_temp_id = fields.Many2one("mail.activity.plan.template")
    department_id = fields.Many2one("hr.department", related="plan_id.department_id", store=True)
    job_id = fields.Many2one('hr.job', related="plan_id.job_id", store=True)


class HrEmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    document_name = fields.Many2one('employee.checklist',
                                    string='Checklist Document',
                                    help='Choose the document in the checklist here.'
                                         ' Automatically the checklist box become true')