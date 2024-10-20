# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
{
    'name': "Approval Payslip Batch",

    'summary': """Dynamic and flexible approval module for Payslip Batch Report""",

    'description': """
        Dynamic and flexible approval module for Payslip Batch Report
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll_account', 'xf_approval_route_base'],
    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/hr_payslip_run_views.xml'
    ],

}
