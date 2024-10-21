/** @odoo-module **/

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { PayslipBatchOverviewDisplayFilter } from "../payslip_batch_overview_display_filter/payslip_batch_overview_display_filter";
import { Component } from "@odoo/owl";

export class PayslipBatchOverviewControlPanel extends Component {
    static template = "hr_payslip_batch_report.PayslipBatchOverviewControlPanel";
    static components = {
        ControlPanel,
        PayslipBatchOverviewDisplayFilter
    };
    static props = {
        showOptions: Object,
        displayOptions: Object,
        changeDisplay: Function,
        print: Function
    };

    setup() {
        this.controlPanelDisplay = {};
    }
}