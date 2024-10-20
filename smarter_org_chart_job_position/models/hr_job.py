from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'

    parent_id = fields.Many2one("hr.job", "Manager Role")
    child_ids = fields.One2many("hr.job", 'parent_id')
    department_color = fields.Integer("Department Color", related="department_id.color")
    hierarchy_level = fields.Integer("Hierarchy Level",
                                     compute="_compute_hierarchy_level",
                                     store=True,
                                     readonly=True)
    is_root = fields.Boolean("Is Root in Hierarchy", default=False)
    manual_hierarchy_level = fields.Integer("Manual Hierarchy Level")
    force_manual = fields.Boolean("Force Manual Hierarchy", default=False)
    color = fields.Integer(compute="compute_color")

    def compute_color(self):
        for rec in self:
            if rec.no_of_employee < 1:
                rec.color = 3
            else:
                rec.color = 0

    @api.constrains('manual_hierarchy_level')
    def _check_hierarchy_level(self):
        for job in self:
            if 0 > job.manual_hierarchy_level or job.manual_hierarchy_level > 20:
                raise ValidationError("Manual Hierarchy Level should be value between 0 and 20.")

    @api.depends("is_root", "parent_id", "manual_hierarchy_level", "force_manual")
    def _compute_hierarchy_level(self):
        for rec in self:
            if rec.force_manual:
                rec.hierarchy_level = rec.manual_hierarchy_level
            elif rec.is_root:
                rec.hierarchy_level = 0
            elif len(rec.parent_id) > 0:
                rec.hierarchy_level = rec.parent_id.hierarchy_level + 1
            else:
                rec.hierarchy_level = rec.manual_hierarchy_level

    @api.onchange("hierarchy_level", "parent_id", "is_root", "manual_hierarchy_level", "force_manual")
    def compute_is_valid_parent(self):
        for rec in self:
            if rec.is_root and len(rec.parent_id) > 0:
                raise ValidationError(_("Root Job positions can't have manager"))
            if len(rec.parent_id) > 0 and rec.parent_id == rec._origin:
                raise ValidationError(_("Job position can't be manager of itself"))
            if len(rec.parent_id) > 0 and rec.parent_id.hierarchy_level >= rec.hierarchy_level:
                raise ValidationError(_("Selected manager role is invalid, "
                                        "as Job position can't have manager lower in hierarchy"))