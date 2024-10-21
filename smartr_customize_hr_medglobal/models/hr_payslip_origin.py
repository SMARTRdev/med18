# -*- coding: utf-8 -*-

from odoo.addons.hr_payroll_account.models.hr_payslip import HrPayslip
from odoo.tools import float_is_zero


def _prepare_slip_lines(self, date, line_ids):
    self.ensure_one()
    precision = self.env['decimal.precision'].precision_get('Payroll')
    new_lines = []
    for line in self.line_ids.filtered(lambda line: line.category_id):
        amount = line.total
        if line.code == 'NET':  # Check if the line is the 'Net Salary'.
            for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                    if amount > 0:
                        amount -= abs(tmp_line.total)
                    elif amount < 0:
                        amount += abs(tmp_line.total)
        if float_is_zero(amount, precision_digits=precision):
            continue

        debit_account_id = line.salary_rule_id.account_debit.id
        credit_account_id = line.salary_rule_id.account_credit.id

        # get salary rule from contract
        salary_rule_accounts = line.contract_id.salary_rule_account_ids.filtered(
            lambda sro: line.salary_rule_id in sro.salary_rule_ids)
        account_debit_contract = False
        account_credit_contract = False

        if salary_rule_accounts:
            salary_rule_account = salary_rule_accounts[0]
            account_debit_contract = salary_rule_account.account_debit_id
            account_credit_contract = salary_rule_account.account_credit_id

            debit_account_id = account_debit_contract.id
            credit_account_id = account_credit_contract.id

        if debit_account_id:  # If the rule has a debit account.
            debit = amount if amount > 0.0 else 0.0
            credit = -amount if amount < 0.0 else 0.0

            debit_line = self._get_existing_lines(
                line_ids + new_lines, line, debit_account_id, debit, credit)

            if not debit_line:
                debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                if account_debit_contract:
                    debit_line['tax_ids'] = [(4, tax_id) for tax_id in account_debit_contract.tax_ids.ids]
                else:
                    debit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_debit.tax_ids.ids]

                new_lines.append(debit_line)
            else:
                debit_line['debit'] += debit
                debit_line['credit'] += credit

        if credit_account_id:  # If the rule has a credit account.
            debit = -amount if amount < 0.0 else 0.0
            credit = amount if amount > 0.0 else 0.0
            credit_line = self._get_existing_lines(
                line_ids + new_lines, line, credit_account_id, debit, credit)

            if not credit_line:
                credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                if account_credit_contract:
                    credit_line['tax_ids'] = [(4, tax_id) for tax_id in account_credit_contract.tax_ids.ids]
                else:
                    credit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_credit.tax_ids.ids]

                new_lines.append(credit_line)
            else:
                credit_line['debit'] += debit
                credit_line['credit'] += credit
    return new_lines


setattr(HrPayslip, "_prepare_slip_lines", _prepare_slip_lines)
