# -*- coding: utf-8 -*-
{
    'name': "Add Budget To Approval",

    'summary': "An Addon to add budget and budget line to approval request",

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
    'depends': ['approvals', 'account_budget'],

    # always loaded
    'data': [
        'views/approval_category_approver_views.xml',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
    ]
}

