# -*- coding: utf-8 -*-
{
    'name': "Add Department to approvals",

    'summary': "Add department for approval category in approval requests",

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
    'depends': ['approvals', 'hr'],

    # always loaded
    'data': [
        # "security/ir.model.access.csv",
        "views/approval_request.xml",
        "views/approval_category_approver.xml",
    ]
}
