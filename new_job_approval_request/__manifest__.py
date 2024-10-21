# -*- coding: utf-8 -*-
{
    'name': "New Job Approval Request",

    'summary': "Add new type of approvals to approvals module",

    'description': """ Long description of module's purpose """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['change_job_target_approval', 'smarter_org_chart_job_position'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/approval_request.xml'
    ]
}
