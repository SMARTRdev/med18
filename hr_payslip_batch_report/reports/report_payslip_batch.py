# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReportPayslipBatch(models.AbstractModel):
    _name = "report.hr_payslip_batch_report.report_payslip_batch"
    _description = "Payslip Batch Overview Report"

    @api.model
    def get_html(self, payslip_batch_id):
        return self._get_report_data(payslip_batch_id)

    def get_payslip_batch_report_columns(self, batch, data):
        payslips = batch.slip_ids

        report_columns = []
        option_columns = {}
        display_option_columns = {}
        for payslip_batch_report_column in self.env["hr.payslip.batch.report.column"].search(
                [("rule_ids", "in", payslips.line_ids.salary_rule_id.ids), "|", ("company_ids", "=", False),
                 ("company_ids", "in", payslips.employee_id.company_id.ids)]):
            column_id = payslip_batch_report_column.name.lower().replace(" ", "") + (
                    "_%s" % payslip_batch_report_column.id)
            report_columns.append({
                "id": column_id,
                "label": payslip_batch_report_column.name,
                "net_salary": payslip_batch_report_column.net_salary,
                "rules": payslip_batch_report_column.rule_ids,
                "companies": payslip_batch_report_column.company_ids
            })

            if payslip_batch_report_column.optional_display:
                option_columns.update({column_id: data.get(column_id, 'false') == 'true' and True or False})

                display_option_columns.update({column_id: payslip_batch_report_column.name})

        return report_columns, option_columns, display_option_columns

    def get_payslips_data(self, batch, report_columns):
        payslips = []
        total_report_columns = {}
        for report_column in report_columns:
            total_report_columns.update({report_column["id"]: 0})

        index = 0
        for payslip in batch.slip_ids:
            index += 1
            contract = payslip.contract_id
            payslip_data = {
                "index": index,
                "id": payslip.id,
                "employee_id": payslip.employee_id.id,
                "name": payslip.employee_id.name,
                "title": payslip.employee_id.sudo().job_id.name or "",
                "contract_id": contract.id or "",
                "contract_start_date": contract.date_start and fields.Date.to_string(contract.date_start) or "",
                "contract_date_end": contract.date_end and fields.Date.to_string(contract.date_end) or "",
                "work_days": (payslip.date_to - payslip.date_from).days + 1,
                "payment_by_hq": payslip.payment_by_hq,
                "project_codes": payslip.get_allocate_timesheet_project_codes(),
                "comments": payslip.comments or "",
                "currency_id": payslip.currency_id.id
            }

            for report_column in report_columns:
                total = 0
                if report_column["companies"] in payslip.employee_id.company_id or not report_column["companies"]:
                    total = sum(line.total for line in
                                payslip.line_ids.filtered(lambda l: l.salary_rule_id in report_column["rules"]))

                payslip_data.update({report_column["id"]: total})
                total_report_columns[report_column["id"]] += total

            payslips.append(payslip_data)

        return payslips, total_report_columns

    @api.model
    def _get_report_data(self, payslip_batch_id, data={}):
        batch = self.env["hr.payslip.run"].browse(payslip_batch_id)

        report_columns, option_columns, display_option_columns = self.get_payslip_batch_report_columns(batch, data)

        payslips_data, total_report_columns = self.get_payslips_data(batch, report_columns)

        for report_column in report_columns:
            del report_column["rules"]
            del report_column["companies"]

        return {
            "payslips": payslips_data,
            "total_report_columns": total_report_columns,
            "report_columns": report_columns,
            "option_columns": option_columns,
            "display_option_columns": display_option_columns,
            "batch_number": batch.name,
            "batch_date": batch.date_end.strftime('%b-%y'),
            "currency": batch.currency_id,
            "currency_id": batch.currency_id.id,
            "company": batch.company_id
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        for batch_id in docids:
            docs.append(self._get_report_data(batch_id, data))

        return {
            "doc_ids": docids,
            "doc_model": "hr.payslip.run",
            "docs": docs,
        }
