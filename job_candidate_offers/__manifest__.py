# -*- coding: utf-8 -*-
{
    'name': "Job Candidate Offers",

    'summary': "Addon to add action report for job position applicants",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment', 'utm', 'sign_print_hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/report_hrapplicant_offers.xml',
        'report/hr_applicant_report_views.xml',
        'views/hr_applicant.xml',
        'views/hr_contract_views.xml',
        'views/hr_job_views.xml',
        'views/views.xml'
    ]
}

