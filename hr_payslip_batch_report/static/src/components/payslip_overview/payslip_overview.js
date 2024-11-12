/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";
import { Component } from "@odoo/owl";

export class PayslipOverview extends Component {
    static template = "hr_payslip_batch_report.PayslipOverview";
    static props = {
        showOptions: Object,
        reportColumns: Object,
        payslip: Object
    };

    setup() {
        this.actionService = useService("action");
        this.ormService = useService("orm");
        this.formatMonetary = (val,currency_id) => formatMonetary(val, { currencyId: currency_id || this.payslip.currency_id });
    }

    get payslip() {
        return this.props.payslip;
    }

    showReportColumn(reportColumnID) {
        if(this.props.showOptions.hasOwnProperty(reportColumnID)) {
            return this.props.showOptions[reportColumnID];
        }
        return true;
    }

    async goToAction(id, model) {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id: id,
            views: [[false, "form"]],
            target: "current",
            context: {
                active_id: id,
            },
        });
    }
}