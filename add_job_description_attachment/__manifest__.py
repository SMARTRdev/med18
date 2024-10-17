# -*- coding: utf-8 -*-
{
    'name': "Add Job Description Attachment",

    'summary': "Addon to allow attaching job description file to the job position",

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
    'depends': ['hr', 'hr_recruitment', 'documents_approvals'],

    # always loaded
    'data': [
        "data/documents_folder_data.xml",
        "data/res_company_data.xml",
        'views/documents.xml',
        'views/hr_job.xml',
        'views/res_config_settings_views.xml'
    ]
}

