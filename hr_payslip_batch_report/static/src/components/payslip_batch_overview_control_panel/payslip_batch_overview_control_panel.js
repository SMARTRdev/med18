/** @odoo-module **/

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { PayslipBatchOverviewDisplayFilter } from "../payslip_batch_overview_display_filter/payslip_batch_overview_display_filter";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Component } from "@odoo/owl";

export class PayslipBatchOverviewControlPanel extends Component {
    setup() {
        this.controlPanelDisplay = {};
    }
}

PayslipBatchOverviewControlPanel.template = "hr_payslip_batch_report.PayslipBatchOverviewControlPanel";
PayslipBatchOverviewControlPanel.components = {
    Dropdown,
    DropdownItem,
    ControlPanel,
    PayslipBatchOverviewDisplayFilter
};
PayslipBatchOverviewControlPanel.props = {
    showOptions: Object,
    displayOptions: Object,
    changeDisplay: Function,
    print: Function
};