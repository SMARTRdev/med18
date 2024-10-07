# -*- coding: utf-8 -*-
{
    'name': "Autofill Timesheets",

    'summary': """Autofill timesheets""",

    'description': """
        Autofill timesheets
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Timesheets',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project_timesheet_holidays', 'hr_payroll_account', 'hr_work_entry_contract', 'timesheet_grid'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/allocate_timesheet_views.xml',
        'views/autofill_timesheet_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_timesheet_views.xml',
        'views/project_task_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml'
    ]
}
