# -*- coding: utf-8 -*-

from odoo import models, fields


class HrPayslipBatchReportColumn(models.Model):
    _name = "hr.payslip.batch.report.column"
    _description = "HR Payslip Batch Report Column"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True, translate=True)
    rule_ids = fields.Many2many("hr.salary.rule", string="Salary Rules", required=True)
    company_ids = fields.Many2many("res.company", string="Companies")
    sequence = fields.Integer(string="Sequence", required=True, default=10)
    optional_display = fields.Boolean(string="Optional Display")
    net_salary = fields.Boolean(string="Net Salary")
