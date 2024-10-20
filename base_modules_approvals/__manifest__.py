# -*- coding: utf-8 -*-
{
    'name': "Base Modules Approvals",

    'summary': """Base Modules Approvals""",

    'description': """
        Base Modules Approvals 
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Approvals',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['approvals'],
    # always loaded
    'data': [
        'views/approval_category_views.xml'
    ]
}
