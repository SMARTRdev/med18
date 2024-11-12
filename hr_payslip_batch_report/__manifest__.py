# -*- coding: utf-8 -*-
{
    'name': "Sign & Print Payslip Batch Report",

    'summary': """Sign & Print Payslip Batch Report""",

    'description': """
        Sign & Print Payslip Batch Report
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['autofill_timesheet', 'sign_print_template', 'approval_route_payslip_batch'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/report_payslip_batch.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_batch_report_column_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_payslip_views.xml',
        'views/menus.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'hr_payslip_batch_report/static/src/**/*'
        ]
    },
}
