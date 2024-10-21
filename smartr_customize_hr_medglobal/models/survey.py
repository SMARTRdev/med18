from odoo import models, fields, api, _
from markupsafe import Markup
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    # is_reference_check = fields.Boolean(readonly=True, related="survey_id.is_reference_check")
    survey_type = fields.Selection(related="survey_id.survey_type", readonly=True)

    def _mark_done(self):
        res = super()._mark_done()
        for user_input in self:
            odoobot = self.env.ref('base.partner_root')
            if user_input.email and user_input.survey_type in ['interview', 'ref_check', 'pre_screen', 'interview_scorecard']:
                application = self.env['hr.applicant'].search([('email_from', '=', user_input.email)])
                if application:
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    rec_url = base_url + '/web#id=%d&view_type=form&model=%s' % (application.id, application._name)

                    if user_input.survey_type == 'interview':
                        message = _('The applicant "%s" has finished the technical test.', application.partner_name)
                    else:
                        message = _('The application for "%s" received a new reference check', application.partner_name)

                    message_html = ("<div>"
                                    "<p>{message}</p><br>"
                                    "<a href='{rec_link}' class='btn btn-primary' target='_blank'>Check Application</a>"
                                    "</div>").format(message=message, rec_link=rec_url)
                    message_with_button = Markup(message_html)
                    for user in application.interviewer_ids:
                        ch = self.env['discuss.channel'].with_user(odoobot).channel_get([user.partner_id.id])
                        ch.sudo().message_post(body=message_with_button,
                                               author_id=odoobot.id,
                                               message_type="comment",
                                               subtype_xmlid="mail.mt_comment")
                else:
                    raise ValidationError("Incorrect Applicant email, "
                                          "please check again or refer "
                                          "back to our hr manager to get right email address")

        return res

    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id',
                 'predefined_question_ids.answer_score')
    def _compute_scoring_values(self):
        for user_input in self:
            if user_input.survey_id.scoring_type == "interview_scoring":
                scoring_total = 0
                total_weight = 0
                for question in user_input.predefined_question_ids:
                    total_weight += question.answer_score
                for line in user_input.user_input_line_ids:
                    scoring_total += line.answer_score

                user_input.scoring_percentage = (scoring_total/total_weight) * 100
                user_input.scoring_total = scoring_total
            else:
                # sum(multi-choice question scores) + sum(simple answer_type scores)
                total_possible_score = 0
                for question in user_input.predefined_question_ids:
                    if question.question_type == 'simple_choice':
                        total_possible_score += max(
                            [score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0],
                            default=0)
                    elif question.question_type == 'multiple_choice':
                        total_possible_score += sum(
                            score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0)
                    elif question.is_scored_question:
                        total_possible_score += question.answer_score

                if total_possible_score == 0:
                    user_input.scoring_percentage = 0
                    user_input.scoring_total = 0
                else:
                    score_total = sum(user_input.user_input_line_ids.mapped('answer_score'))
                    user_input.scoring_total = score_total
                    score_percentage = (score_total / total_possible_score) * 100
                    user_input.scoring_percentage = round(score_percentage, 2) if score_percentage > 0 else 0


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    mark_weight = fields.Float(required=True, related="question_id.answer_score")


class Survey(models.Model):
    _inherit = 'survey.survey'

    job_id = fields.Many2one('hr.job')
    scoring_type = fields.Selection(selection_add=[('interview_scoring', 'Interview Scoring')],
                                    ondelete={'interview_scoring': 'cascade'})
    is_reference_check = fields.Boolean(default=False)

    survey_type = fields.Selection(selection_add=[
        ('pre_screen', 'Pre-screen Questionnaire'),
        ('interview_scorecard', 'Interview Score Card'),
        ('interview', 'Technical Test'),
        ('ref_check', 'Reference Check')],
        ondelete={'interview': 'cascade',
                  'ref_check': 'cascade',
                  'pre_screen': 'cascade',
                  'interview_scorecard': 'cascade'})

    def create(self, vals_list):
        res = super(Survey, self).create(vals_list)
        if vals_list['survey_type'] in ['interview', 'ref_check', 'pre_screen']:
            email_question_title = "what is your email?"
            if vals_list['survey_type'] == 'ref_check':
                email_question_title = "what is the email of the candidate?"

            email_q = self.env['survey.question'].create({
                "title": email_question_title,
                "question_type": "char_box",
                "validation_email": True,
                "save_as_email": True,
                "constr_mandatory": True,
                "survey_id": res.id
            })

        return res


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    # mark_weight = fields.Integer(required=True, default=0)
