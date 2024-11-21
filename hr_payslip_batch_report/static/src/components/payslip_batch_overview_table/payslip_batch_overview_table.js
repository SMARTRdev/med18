/** @odoo-module **/

import { PayslipOverview } from "../payslip_overview/payslip_overview";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { formatMonetary } from "@web/views/fields/formatters";
import { _t } from "@web/core/l10n/translation";

export class PayslipBatchOverviewTable extends Component {
    static template = "hr_payslip_batch_report.PayslipBatchOverviewTable";
    static components = {
        PayslipOverview,
    };
    static props = {
        showOptions: Object,
        reportColumns: Object,
        totalReportColumns: Object,
        payslips: Object,
        batchNumber: { type: String, optional: true },
        batchDate: { type: String, optional: true },
        batchID: { type: Number, optional: true },
        currencyID: Number
    };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.formatMonetary = (val,currency_id) => formatMonetary(val, { currencyId: currency_id || this.props.currencyID });
    }

    get batchNumber() {
        return this.props.batchNumber;
    }

    get batchDate() {
        return this.props.batchDate;
    }

    get payslips() {
        return this.props.payslips;
    }

    showReportColumn(reportColumnID) {
        if(this.props.showOptions.hasOwnProperty(reportColumnID)) {
            return this.props.showOptions[reportColumnID];
        }
        return true;
    }

    async goToPayslipBatch() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.payslip.run",
            res_id: this.props.batchID,
            views: [[false, "form"]],
            target: "current",
            context: {
                active_id: this.props.batchID,
            },
        });
    }

    async goToTimesheets() {
        const sign_request_ids = await this.orm.call(
            "hr.payslip.run",
            "action_get_sign_request_ids",
            [this.props.batchID]
        );
        return this.actionService.doAction({
            name: _t("Signature Requests"),
            type: "ir.actions.act_window",
            res_model: "sign.request",
            domain: [["id","in",sign_request_ids]],
            views: [[false, "kanban"],[false, "list"]],
            view_mode: "kanban,list",
            target: "current"
        });
    }
}