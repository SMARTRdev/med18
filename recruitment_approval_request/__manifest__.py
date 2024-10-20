# -*- coding: utf-8 -*-
{
    'name': "Recruitment Approval Request",

    'summary': "Addon to extend approval request types and add recruitment approval type",

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
    'depends': ['add_department_to_approval', 'hr_recruitment'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        "views/approval_request.xml",
        "views/approval_job_skill.xml",
        "views/approval_job_line.xml"
    ]
}

