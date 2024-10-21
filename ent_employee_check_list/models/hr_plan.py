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
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from markupsafe import Markup
from odoo.tools.misc import clean_context


class HrPlanActivityTypeChecklist(models.Model):
    _inherit = 'mail.activity.plan.template'

    entry_checklist_plan = fields.Many2many('employee.checklist',
                                            'entry_obj_plan', 'check_hr_rel', 'hr_check_rel',
                                            string='Entry Process',
                                            domain="[('document_type', '=', 'entry'),('job_id', '=', job_id)]")
    exit_checklist_plan = fields.Many2many('employee.checklist', 'exit_obj_plan', 'exit_hr_rel', 'hr_exit_rel',
                                           string='Exit Process',
                                           domain="[('document_type', '=', 'exit'),('job_id', '=', job_id)]")

    # def unlink(self):
    #     """
    #     Function is used for while deleting the planing types
    #     it check if the record is related to checklist and raise
    #     error.
    #
    #     """
    #     check_id = self.env.ref('ent_employee_check_list.checklist_activity_type')
    #     for recd in self:
    #         if recd.id == check_id.id:
    #             raise UserError(_("Checklist Record Can't Be Delete!"))
    #     return super(HrPlanActivityTypeChecklist, self).unlink()


class EmployeeChecklistInherit(models.Model):
    _inherit = 'employee.checklist'

    entry_obj_plan = fields.Many2many('hr.employee', 'entry_checklist_plan', 'hr_check_rel', 'check_hr_rel',
                                      invisible=1)
    exit_obj_plan = fields.Many2many('hr.employee', 'exit_checklist_plan', 'hr_exit_rel', 'exit_hr_rel',
                                     invisible=1)


class MailActivityChecklist(models.Model):
    _inherit = 'mail.activity'

    # entry_checklist_plan = fields.Many2many('employee.checklist', 'check_hr_rel', 'hr_check_rel',
    #                                         string='Entry Process',
    #                                         domain=[('document_type', '=', 'entry')], help="Entry Checklist's")
    # exit_checklist_plan = fields.Many2many('employee.checklist', 'exit_hr_rel', 'hr_exit_rel',
    #                                        string='Exit Process',
    #                                        domain=[('document_type', '=', 'exit')], help="Exit Checklists's")
    # check_type_check = fields.Boolean()
    # on_board_type_check = fields.Boolean()
    # off_board_type_check = fields.Boolean()
    check_list_temp_id = fields.Many2one('employee.checklist')

    def _action_done(self, feedback=False, attachment_ids=None):
        model_name = self.env['ir.model'].search([('id', '=', self.res_model_id.id)]).model
        has_checklist = len(self.check_list_temp_id) > 0
        if model_name == "hr.employee":
            if has_checklist:
                employee = self.env['hr.employee'].search([('id', '=', self.res_id)])
                if self.check_list_temp_id.document_type == "entry":
                    employee.write({'entry_checklist': [(4, self.check_list_temp_id.id)]})
                    employee.compute_entry_progress()
                elif self.check_list_temp_id.document_type == "exit":
                    employee.write({'exit_checklist': [(4, self.check_list_temp_id.id)]})
                    employee.compute_exit_progress()

        res = super(MailActivityChecklist, self)._action_done(feedback=feedback, attachment_ids=attachment_ids)

        return res


class HrPlanWizardInherited(models.TransientModel):
    _inherit = 'mail.activity.schedule'

    def action_schedule_plan(self):
        applied_on = self._get_applied_on_records()
        for record in applied_on:
            body = _('The plan "%(plan_name)s" has been started', plan_name=self.plan_id.name)
            activity_descriptions = []
            for template in self._plan_filter_activity_templates_to_schedule():
                if template.responsible_type == 'on_demand':
                    responsible = self.plan_on_demand_user_id
                else:
                    responsible = template._determine_responsible(self.plan_on_demand_user_id, record)['responsible']
                date_deadline = self.env['mail.activity']._calculate_date_deadline(
                    template.activity_type_id, force_base_date=self.plan_date_deadline)
                record.activity_schedule(
                    activity_type_id=template.activity_type_id.id,
                    summary=template.summary,
                    note=template.note,
                    user_id=responsible.id,
                    date_deadline=date_deadline
                )
                # CUSTOM CODE // Related to employee checklist functionality
                temp_checklist = self.env['employee.checklist'].search([("activity_temp_id", '=', template.id)])
                if len(temp_checklist) > 0:
                    activities = self.env['mail.activity'].search([("res_id", '=', record.id),
                                                                  ("summary", '=', template.summary)])
                    sorted_activities = activities.sorted(key=lambda r: r.id)
                    target_activity = sorted_activities[len(sorted_activities)-1]
                    target_activity.write({"check_list_temp_id": temp_checklist.id})

                activity_descriptions.append(
                    _('%(activity)s, assigned to %(name)s, due on the %(deadline)s',
                      activity=template.summary or template.activity_type_id.name,
                      name=responsible.name, deadline=date_deadline))

            if activity_descriptions:
                body += Markup('<ul>%s</ul>') % (
                    Markup().join(Markup('<li>%s</li>') % description for description in activity_descriptions)
                )
            record.message_post(body=body)

        if len(applied_on) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.res_model,
                'res_id': applied_on.id,
                'name': applied_on.display_name,
                'view_mode': 'form',
                'views': [(False, "form")],
            }

        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'name': _('Launch Plans'),
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('id', 'in', applied_on.ids)],
        }

    # def action_launch(self):
    #     """
    #     Function is override for appending checklist values
    #     to the mail activity.
    #
    #     """
    #     for employee in self.employee_ids:
    #         # check_type_id = self.env.ref('ent_employee_check_list.checklist_activity_type')
    #         # on_id = self.env.ref('hr.onboarding_plan')
    #         # of_id = self.env.ref('hr.offboarding_plan')
    #         for activity_type in self.plan_id.plan_activity_type_ids:
    #             responsible = activity_type.get_responsible_id(employee)['responsible']
    #
    #             if self.env['hr.employee'].with_user(responsible).check_access_rights('read', raise_exception=False):
    #                 self.env['mail.activity'].create({
    #                     'res_id': employee.id,
    #                     'res_model_id': employee.env['ir.model']._get('hr.employee').id,
    #                     'summary': activity_type.summary,
    #                     'note': activity_type.note,
    #                     'activity_type_id': activity_type.activity_type_id.id,
    #                     'user_id': responsible.id,
    #                     'entry_checklist_plan': activity_type.entry_checklist_plan,
    #                     'exit_checklist_plan': activity_type.exit_checklist_plan,
    #                     'check_type_check': True,
    #                     'on_board_type_check': True,
    #                     'off_board_type_check': False
    #                 })
    #
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'hr.employee',
    #             'res_id': employee.id,
    #             'name': employee.display_name,
    #             'view_mode': 'form',
    #             'views': [(False, "form")],
    #         }


class HrPlanCheckList(models.Model):
    _inherit = 'mail.activity.plan'

    plan_type = fields.Selection(
        selection=[
            ("entry", "Onboarding"),
            ("exit", "Offboarding"),
            ("other", "Other")],
        default="entry",
        string="Plan Type",
        required=True)

    department_id = fields.Many2one("hr.department", required=True)
    checklist_ids = fields.One2many("employee.checklist",
                                    inverse_name="plan_id", readonly=True, ondelete='cascade')
    job_id = fields.Many2one('hr.job', required=True, domain="[('department_id', '=', department_id)]")

    @api.model_create_multi
    def create(self, vals):
        res = super(HrPlanCheckList, self).create(vals)
        list_to_create = []
        for temp in res.template_ids:
            list_to_create.append({
                "plan_id": res.id,
                "activity_temp_id": temp.id,
                'name': res.name
            })
        self.env['employee.checklist'].with_context({}).sudo().create(list_to_create)

        return res

    @api.constrains('job_id')
    def check_validity_of_job(self):
        for rec in self:
            plans = self.search([('job_id', '=', rec.job_id.id), ('plan_type', '=', rec.plan_type)])
            if len(plans) > 1:
                raise ValidationError(_("There is already plan of type %s in job %s",
                                        rec.plan_type,
                                        rec.job_id.name))

    def unlink(self):
        """
        Function is used for checking while deleting
        plan which is related to checklist record
        and raise error.

        """
        for rec in self:
            schedule_plans_count = self.env['mail.activity.schedule'].search_count([('plan_id', '=', rec.id)])
            if schedule_plans_count > 0:
                raise UserError(_("Can't delete this plan as it has been already used"))
            else:
                rec.checklist_ids.unlink()

        return super(HrPlanCheckList, self).unlink()

    def write(self, vals):
        schedule_plans_count = self.env['mail.activity.schedule'].search_count([('plan_id', '=', self.id)])
        if schedule_plans_count > 0:
            raise UserError(_("Can't update this plan as it has been already used"))

        return super(HrPlanCheckList, self).write(vals)
