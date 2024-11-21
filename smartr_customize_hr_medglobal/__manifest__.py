# -*- coding: utf-8 -*-
{
    'name': "Smartr Customize Hr MedGlobal",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

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
    'depends': ['ent_hr_reward_warning', 'hr_recruitment_survey',
                'new_job_approval_request', 'add_job_description_attachment', 'hr_payroll_holidays',
                'hr_payroll_account', 'shortlisting_approval_request', 'set_approvers_for_approval_request',
                'job_candidate_offers', 'hr_payslip_batch_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/announcement_category.xml',
        'views/announcement.xml',
        'views/hr_applicant.xml',
        'views/hr_contract_views.xml',
        'views/hr_department_function_views.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_views.xml',
        'views/survey.xml',
        'views/survey_question.xml',
        'views/hr_recruitment.xml',
        'views/survey_templates.xml',
        'views/hr_job.xml',
        'views/hr_leave_views.xml',
        'views/hr_leave_type_views.xml',
        'views/approval_job_line.xml',
        'views/approval_category.xml',
        'views/res_users_views.xml',
        'views/res_company_views.xml',
        'views/menus.xml'
    ]
}
