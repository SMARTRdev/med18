# -*- coding: utf-8 -*-
{
    'name': "Change Job Target Approval",

    'summary': "Addon to add new approval request of type (Change job target employee)",

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
    'depends': ['recruitment_approval_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/approval_request.xml',
        'views/hr_job.xml'
    ]
}

