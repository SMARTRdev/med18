/** @odoo-module **/

import { PayslipOverview } from "../payslip_overview/payslip_overview";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { formatMonetary } from "@web/views/fields/formatters";

export class PayslipBatchOverviewTable extends Component {
    setup() {
        this.actionService = useService("action");
        this.formatMonetary = (val) => formatMonetary(val, { currencyId: this.props.currencyID });
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
}

PayslipBatchOverviewTable.template = "hr_payslip_batch_report.PayslipBatchOverviewTable";
PayslipBatchOverviewTable.components = {
    PayslipOverview
};

PayslipBatchOverviewTable.props = {
    showOptions: Object,
    reportColumns: Object,
    totalReportColumns: Object,
    payslips: Object,
    batchNumber: { type: String, optional: true },
    batchDate: { type: String, optional: true },
    batchID: { type: Number, optional: true },
    currencyID: Number
};
