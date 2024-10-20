# -*- coding: utf-8 -*-
{
    'name': "Sign & Print Recruitment",

    'summary': """Sign & Print Recruitment""",

    'description': """
        Sign & Print Recruitment
    """,

    'author': "SMARTR Teknoloji",
    'website': "info@smartr.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Recruitment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment', 'sign_print_template'],
    # always loaded
    'data': [
        'views/hr_applicant_views.xml'
    ]
}
