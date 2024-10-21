/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Component } from "@odoo/owl";

export class PayslipBatchOverviewDisplayFilter extends Component {
    get displayableOptions() {
        return Object.keys(this.props.displayOptions);
    }
}

PayslipBatchOverviewDisplayFilter.template = "hr_payslip_batch_report.PayslipBatchOverviewDisplayFilter";
PayslipBatchOverviewDisplayFilter.components = {
    Dropdown,
    DropdownItem,
}
PayslipBatchOverviewDisplayFilter.props = {
    showOptions: Object,
    displayOptions: Object,
    changeDisplay: Function,
};
