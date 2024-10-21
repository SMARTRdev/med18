# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRContractSalaryRuleAccount(models.Model):
    _name = "hr.contract.salary.rule.account"
    _description = "HR Contract Salary Rule Account"

    contract_id = fields.Many2one("hr.contract", string="Contract", ondelete="cascade", required=True)
    structure_type_id = fields.Many2one(related="contract_id.structure_type_id")
    salary_rule_ids = fields.Many2many("hr.salary.rule", string="Salary Rule", required=True,
                                       domain="[('struct_id.type_id','=',structure_type_id)]")
    account_debit_id = fields.Many2one("account.account", string="Debit Account", company_dependent=True,
                                       domain=[("deprecated", "=", False)], required=True)
    account_credit_id = fields.Many2one("account.account", string="Credit Account", company_dependent=True,
                                        domain=[("deprecated", "=", False)], required=True)


class HRContract(models.Model):
    _inherit = "hr.contract"

    is_social_security_exempt = fields.Boolean(string="Is Social Security Exempt", tracking=True)
    salary_rule_account_ids = fields.One2many("hr.contract.salary.rule.account", "contract_id",
                                              string="Salary Rule Accounts", copy=True)

    @api.onchange("structure_type_id")
    def onchange_structure_type_id(self):
        self.salary_rule_account_ids = False
