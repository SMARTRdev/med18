# -*- coding: utf-8 -*-
{
    'name': "Sign & Print Timesheet Report",

    'summary': """Sign & Print Timesheet Report""",

    'description': """
        Sign & Print Timesheet Report
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Recruitment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['smrtr_timesheet_report', 'assign_contact_sign'],
    # always loaded
    'data': [
        'wizard/time_sheet_select_wizard_views.xml',
        'views/sign_template_views.xml'
    ]
}
