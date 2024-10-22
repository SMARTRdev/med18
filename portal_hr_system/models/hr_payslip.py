# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class HRPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip','portal.mixin']
    
    def _compute_access_url(self):
        super(HRPayslip, self)._compute_access_url()
        for payslip in self:
            payslip.access_url = '/my/payslip/%s' % (payslip.id)
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('Payslip'), self.number)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
