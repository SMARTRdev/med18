# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ApprovalCategoryApprover(models.Model):
    _inherit = "approval.category.approver"

    department_id = fields.Many2one("hr.department", string="Department")


class ApprovalApprover(models.Model):
    _inherit = "approval.approver"

    department_id = fields.Many2one("hr.department", string="Department", readonly=True)


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    department_id = fields.Many2one("hr.department", "Department", check_company=True)
    available_departments_ids = fields.Many2many('hr.department', compute='_compute_departments_ids')

    @api.onchange('request_owner_id')
    def _default_department_id(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
        if employee:
            if employee.department_id:
                self.department_id = employee.department_id.id
            else:
                self.department_id = self.env['hr.department'].search([], limit=1).id
        else:
            self.department_id = self.env['hr.department'].search([], limit=1).id

    @api.onchange('department_id')
    def _compute_departments_ids(self):
        if self.department_id:
            self.write({'available_departments_ids': [(4, self.department_id.id)]})
            self.get_department_children(self.department_id, self)
        else:
            employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
            if employee:
                self.available_departments_ids = [(4, employee.department_id.id)]
            else:
                self.available_departments_ids = False

    def get_department_children(self, department, rec):
        children = department.child_ids
        if len(children) > 0:
            for child in children:
                rec.write({'available_departments_ids': [(4, child.id)]})
                self.get_department_children(child, rec)

    def update_approver_index_by_department(self):
        for approver in self.approver_ids:
            template = self.category_id.approver_ids.filtered(
                lambda temp_approver: temp_approver.user_id == approver.user_id)
            approver.department_id = template.department_id.id
            if approver.department_id == self.department_id and self.department_id:
                approver.importance_index += 1
