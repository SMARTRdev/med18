# -*- coding: utf-8 -*-
from odoo import models, fields, api


class BudgetAnalytic(models.Model):
    _inherit = "budget.analytic"

    code = fields.Char(string="Code", tracking=True)
    last_sequence_line = fields.Integer(string="Last Sequence Line", readonly=True)
    description = fields.Char("Description")

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        self.env.registry.clear_cache('groups')

        arch, view = super()._get_view(view_id, view_type, **options)

        current_user = self.env.user
        if view_type == "form" and current_user.has_group(
                "customize_budget.group_allow_change_budget_lines_after_draft"):
            for node in arch.xpath("//field[@name='budget_line_ids']"):
                node.set("readonly", "0")

        return arch, view


class BudgetLine(models.Model):
    _inherit = "budget.line"
    _rec_name = "sequence_code"

    sequence_code = fields.Char(string="Sequence Code", readonly=True)

    def generate_sequence_code(self):
        budget_analytic = self.budget_analytic_id
        budget_analytic.write({"last_sequence_line": budget_analytic.last_sequence_line + 1})
        self.write({"sequence_code": budget_analytic.code + "-" + "%0*d" % (3, budget_analytic.last_sequence_line)})

        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.generate_sequence_code()
        return res
