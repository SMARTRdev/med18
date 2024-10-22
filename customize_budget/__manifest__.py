# -*- coding: utf-8 -*-
{
    'name': "Customize Budget",

    'summary': "Addon to customize crossoverd budget",

    'description': """
Long description of module's purpose
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant', 'account_budget'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/account_budget_views.xml'
    ]
}

