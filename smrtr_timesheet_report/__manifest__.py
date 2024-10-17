# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{

    'name': "smarter Employee Timesheet Report",
    'version': '18.0.0.0',
    'category': 'Human Resources',
    'summary': "Print Employee timesheet report for employee",
    'description': ''' 
      Employee Timesheet Report helps you print PDF reports of employee timesheets for a specific time period.
       Users can choose to print timesheet reports for single or multiple employees within a particular date range as per their needs.
    ''',
    'author': 'SMARTR Teknoloji',
    'website': 'https://www.smartr.dev',
    'depends': ['project_timesheet_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/time_sheet_select_wizard_view.xml',
        'wizard/save_ex_report_wizard_view.xml',
        'views/timesheet.xml',
        'report/ir.timesheet_report_template.xml',
        'report/ir.timesheet_reoprt.xml',

    ],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/Employee-Timesheet-Excel-and-PDF-Report-Banner.gif'],
}
