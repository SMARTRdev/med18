from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

SCORECARD_QUESTIONS = [
    {
        "title": "what is the interviewer name",
        "question_type": "char_box",
        "answer_score": 0.0,
        "sequence": 1
    },
    {
        "title": "what is the email of the candidate?",
        "question_type": "char_box",
        "validation_email": True,
        "save_as_email": True,
        "constr_mandatory": True,
        "answer_score": 0.0,
        "sequence": 2
    },
    {
        "title": "Education/Bachelors",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 3
    },
    {
        "title": "Education/Masters",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 4
    },
    {
        "title": "Education/Certificates",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 5
    },
    {
        "title": "Personal/Enthusiasm",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 6
    },
    {
        "title": "Personal/Flexibility",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 7
    },
    {
        "title": "Personal/Drive",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 8
    },
    {
        "title": "Personal/Organization",
        "question_type": "simple_choice",
        "answer_score": 5.0,
        "sequence": 9
    },
    {
        "title": "Salary Exception in USD",
        "question_type": "numerical_box",
        "answer_score": 0.0,
        "sequence": 99
    },
    {
        "title": "Start Date",
        "question_type": "date",
        "answer_score": 0.0,
        "sequence": 100
    },
    {
        "title": "Comments",
        "question_type": "text_box",
        "answer_score": 0.0,
        "sequence": 101
    }
]

SCORECARD_CHOICES = [
    {
        'value': "Not Applicable",
        'answer_score': 0.0,
        'is_correct': True
    },
    {
        'value': "Unsatisfactory",
        'answer_score': 1.0,
        'is_correct': True
    },
    {
        'value': "Below Expectation",
        'answer_score': 2.0,
        'is_correct': True
    },
    {
        'value': "Meets Expectation",
        'answer_score': 3.0,
        'is_correct': True
    },
    {
        'value': "Above Expectation",
        'answer_score': 4.0,
        'is_correct': True
    },
    {
        'value': "Exceptional",
        'answer_score': 5.0,
        'is_correct': True
    }
]


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    manager_id = fields.Many2one('hr.employee', required=True)


class HrJob(models.Model):
    _inherit = 'hr.job'

    interview_scorecard_id = fields.Many2one('survey.survey',
                                             domain='[("survey_type", "=", "interview_scorecard")]')
    no_of_recruitment = fields.Integer(readonly=True, default=0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    approved_scale = fields.Many2one('approved.grading.scale', 'Approved Scale')

    def action_new_interview_scorecard(self):
        self.ensure_one()
        survey = self.env['survey.survey'].create({
            'title': _("Interview Score Card Form For: %s", self.name),
            'survey_type': 'interview_scorecard',
            'scoring_type': 'interview_scoring',
            'job_id': self.id
        })
        self.write({'interview_scorecard_id': survey.id})

        for question in SCORECARD_QUESTIONS:
            survey_question = self.env['survey.question'].create(question)
            survey_question.write({
                "survey_id": survey.id
            })
            if survey_question.question_type == 'simple_choice':
                for choice in SCORECARD_CHOICES:
                    question_choice = self.env['survey.question.answer'].create(choice)
                    question_choice.write({
                        "question_id": survey_question.id
                    })
        action = {
                'name': _('Interview Score Card'),
                'view_mode': 'form,list',
                'res_model': 'survey.survey',
                'type': 'ir.actions.act_window',
                'res_id': survey.id,
            }

        return action

    def action_new_survey(self):
        self.ensure_one()
        survey = self.env['survey.survey'].create({
            'title': _("Technical Interview Form For: %s", self.name),
            'survey_type': 'interview',
            'scoring_type': 'interview_scoring',
            'job_id': self.id
        })
        self.write({'survey_id': survey.id})

        action = {
                'name': _('Survey'),
                'view_mode': 'form,list',
                'res_model': 'survey.survey',
                'type': 'ir.actions.act_window',
                'res_id': survey.id,
            }

        return action


class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    stage_type = fields.Selection([('none', 'Initial'),
                                   ('before_short_list', 'Before Short List Stage'),
                                   ('short_list', 'Short List Stage'),
                                   ('hired', 'Hired Stage')], default='none')

    @api.onchange('stage_type')
    def onchange_stage_type(self):
        for rec in self:
            if rec.stage_type == 'hired':
                rec.hired_stage = True
            else:
                rec.hired_stage = False