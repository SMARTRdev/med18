/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { PayslipBatchOverviewControlPanel } from "../payslip_batch_overview_control_panel/payslip_batch_overview_control_panel";
import { PayslipBatchOverviewTable } from "../payslip_batch_overview_table/payslip_batch_overview_table";
import { Component, EventBus, onWillStart, useSubEnv, useState } from "@odoo/owl";

export class PayslipBatchOverviewComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");

        this.batchNumber = "";
        this.batchDate = "";

        this.state = useState({
            showOptions: {},
            displayOptions: {},
            reportColumns: {},
            totalReportColumns: {},
            payslipBatchData: {}
        });

        useSubEnv({
            overviewBus: new EventBus(),
        });

        onWillStart(async () => {
            await this.initPayslipBatchData();
        });
    }

    async initPayslipBatchData() {
        const payslipBatchData = await this.getPayslipBatchData();
        this.state.reportColumns = payslipBatchData["report_columns"];
        this.state.totalReportColumns = payslipBatchData["total_report_columns"];
        this.state.showOptions = payslipBatchData["option_columns"]
        this.state.displayOptions = payslipBatchData["display_option_columns"]
        this.batchNumber = payslipBatchData["batch_number"];
        this.batchDate = payslipBatchData["batch_date"];
        this.currencyID = payslipBatchData["currency_id"];
    }

    get activeId() {
        return this.props.action.context.active_id;
    }

    async getPayslipBatchData() {
        const args = [
            this.activeId
        ];

        const context = this.state.currentWarehouse ? { warehouse: this.state.currentWarehouse.id } : {};
        const payslipBatchData = await this.orm.call(
            "report.hr_payslip_batch_report.report_payslip_batch",
            "get_html",args,{}
        );
        this.state.payslipBatchData = payslipBatchData["payslips"];
        return payslipBatchData;
    }

    onChangeDisplay(displayInfo) {
        this.state.showOptions[displayInfo] = !this.state.showOptions[displayInfo];
    }

    async onClickPrint() {
        return this.actionService.doAction({
            type: "ir.actions.report",
            report_type: "qweb-pdf",
            report_name: this.getReportName(),
            report_file: "hr_payslip_batch_report.report_payslip_batch",
        });
    }

    getReportName() {
        let reportName = "hr_payslip_batch_report.report_payslip_batch?docids=" + this.activeId


        for(const showOption in this.state.showOptions){
           reportName += `&${showOption}=${this.state.showOptions[showOption]}`
        }

        return reportName;
    }
}


PayslipBatchOverviewComponent.template = "hr_payslip_batch_report.PayslipBatchOverviewComponent";
PayslipBatchOverviewComponent.components = {
    PayslipBatchOverviewControlPanel,
    PayslipBatchOverviewTable,
};

registry.category("actions").add("report_payslip_batch", PayslipBatchOverviewComponent);