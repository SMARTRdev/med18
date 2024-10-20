# -*- coding: utf-8 -*-
{
    'name': "Sign & Print Template",

    'summary': """Sign & Print Template""",

    'description': """
        Sign & Print Template
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sign',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['assgin_contact_sign'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/sign_print_template_views.xml'
    ]
}
