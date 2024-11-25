# -*- coding: utf-8 -*-

import base64

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class TimesheetSelect(models.TransientModel):
    _inherit = "timesheet.select"

    sign_print = fields.Boolean(string="Sign & Print")
    sign_template_id = fields.Many2one("sign.template", string="Sign Template",
                                       domain=[("use_as_sign_print_timesheet_report", "=", True)])

    def generate_pdf_report(self):
        if self.sign_print and self.sign_template_id:
            employees = self.employee_ids
            ir_attachment_obj = self.env["ir.attachment"]
            sign_request_obj = self.env["sign.request"]
            sign_send_request_obj = self.env["sign.send.request"]
            timesheet_report = self.env.ref("smrtr_timesheet_report.timesheet_report_id")

            sign_request_ids = []
            for employee in employees:
                if not employee.parent_id:
                    raise ValidationError(_("Employee %s has no manager assigned." % employee.display_name))

                self.employee_ids = employee

                sign_template = self.sign_template_id.copy({"use_as_sign_print_timesheet_report": False})

                data_dict = {'id': self.id, 'start_date': self.start_date, 'end_date': self.end_date,
                             'employee_ids': self.employee_ids}
                report = timesheet_report.sudo()._render_qweb_pdf(timesheet_report.id,
                                                                  res_ids=self.ids, data=data_dict)

                attachment_name = f"{timesheet_report.name} - {employee.display_name} - {self.start_date.strftime('%Y-%b')}"
                sign_request_count = sign_request_obj.search_count([("timesheet_report_employee_id", "=", employee.id),
                                                                    ("timesheet_report_date", ">=", self.start_date),
                                                                    ("timesheet_report_date", "<=", self.end_date)])
                if sign_request_count > 0:
                    attachment_name += f"({sign_request_count})"

                attachment = ir_attachment_obj.create({
                    "name": attachment_name + ".pdf",
                    "type": "binary",
                    "datas": base64.b64encode(report[0]),
                    "res_model": sign_template._name,
                    "res_id": sign_template.id,
                    "mimetype": 'application/pdf'
                })

                sign_template.write({"attachment_id": attachment.id})

                roles = sign_template.sign_item_ids.responsible_id.sorted()
                signers_count = len(roles)

                signer_ids = []
                for default_signing_order, role in enumerate(roles):
                    partner_id = False
                    if role.contact_type == "employee":
                        partner_id = employee.work_contact_id.id
                    elif role.contact_type == "employee_manager":
                        partner_id = employee.parent_id.work_contact_id.id
                    elif role.assign_contact_id:
                        partner_id = role.assign_contact_id.id

                    signer_ids.append((0, 0, {
                        "role_id": role.id,
                        "partner_id": partner_id or self.env.user.partner_id.id,
                        "mail_sent_order": default_signing_order + 1
                    }))

                sign_send_request = (
                    sign_send_request_obj.with_context(active_id=sign_template.id,
                                                       sign_directly_without_mail=False).create(
                        {
                            "template_id": sign_template.id,
                            "filename": sign_template.display_name,
                            "subject": _("Signature Request - %(file_name)s",
                                         file_name=sign_template.attachment_id.name),
                            "set_sign_order": True,
                            "signers_count": signers_count,
                            "signer_ids": signer_ids
                        }))
                res = sign_send_request.with_context(sign_all=True).sign_directly()
                sign_request_id = res["context"]["id"]
                sign_request = sign_request_obj.browse(sign_request_id)
                sign_request.write({
                    "timesheet_report_employee_id": employee.id,
                    "timesheet_report_date": self.date
                })
                sign_request_ids.append(sign_request_id)

            if sign_request_ids:
                if len(sign_request_ids) == 1:
                    return sign_request_obj.browse(sign_request_ids[0]).go_to_document()

                return {
                    "type": "ir.actions.act_window",
                    "name": "Signature Requests",
                    "view_mode": "kanban,list",
                    "res_model": "sign.request",
                    "domain": [("id", "in", sign_request_ids)]
                }
        else:
            return super().generate_pdf_report()
