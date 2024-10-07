# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    autofill_timesheet_month = fields.Date(string="Autofill Timesheet Month", readonly=True, copy=False)
