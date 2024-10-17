# -*- coding: utf-8 -*-
{
    'name': "Assign Contact Sign",

    'summary': """Assign contact to sign role""",

    'description': """
        Assign contact to sign role
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sign',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sign'],
    # always loaded
    'data': [
        'views/sign_item_role_views.xml'
    ]
}
