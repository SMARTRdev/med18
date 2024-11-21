# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, api


class timesheet_report(models.AbstractModel):
    _name = 'report.smrtr_timesheet_report.timesheet_select_report'
    _description = 'timesheet report'

    def get_timesheets_list(self, docs):
        if docs.start_date and docs.end_date:

            record = self.env['account.analytic.line'].search(
                [('employee_id', 'in', docs.employee_ids.ids), ('date', '>=', docs.start_date),
                 ('date', '<=', docs.end_date)])
        else:
            record = self.env['account.analytic.line'].search(
                [('employee_id', 'in', docs.employee_ids.ids)])

        records = []

        grouped_records = {}
        for rec in record:
            employee_id = rec['employee_id']
            if employee_id in grouped_records:
                grouped_records[employee_id].append(rec)
            else:
                grouped_records[employee_id] = [rec]

        for employee_id, employee_records in grouped_records.items():
            allocate_timesheet_line = self.env["allocate.timesheet.line"].sudo().search(
                [("allocate_timesheet_id.date", ">=", docs.start_date),
                 ("allocate_timesheet_id.date", "<=", docs.end_date),
                 ("employee_id", "=", employee_id.id)], limit=1)

            total = 0
            for rec in employee_records:
                is_leave = False
                if rec.holiday_id:
                    is_leave = True

                percentage_allocate = (rec.hours_percentage_month_project * 100)
                if rec.company_id.percentage_timesheet_report == "allocation":
                    percentage_allocate = 0
                    if rec.project_id.account_id and allocate_timesheet_line:
                        project_account_id = rec.project_id.account_id.id
                        for account_id, distribution in allocate_timesheet_line.analytic_distribution.items():
                            if int(account_id) == project_account_id:
                                percentage_allocate = distribution
                                break

                vals = {
                    'project': rec.project_id.name,
                    'employee': rec.employee_id,
                    'duration': rec.unit_amount,
                    'date': rec.date,
                    'description': rec.name,
                    'task': rec.task_id.name,
                    'total': total,
                    'percentage_allocate': percentage_allocate,
                    'is_leave': is_leave
                }
                records.append(vals)

        return [records]

    @api.model
    def _get_report_values(self, docids, data=None):
        if docids:
            docs = self.env['timesheet.select'].browse(docids)
        else:
            docs = self.env['timesheet.select'].browse(self.env.context.get('active_id'))

        timesheets = self.get_timesheets_list(docs)

        time_gap = None
        if docs.start_date and docs.end_date:
            time_gap = "From " + str(docs.start_date) + " To " + str(docs.end_date)

        return {
            'doc_ids': self.ids,
            'docs': docs,
            'timesheets': timesheets[0],
            'employees': docs.employee_ids,
            'time_gap': time_gap
        }
