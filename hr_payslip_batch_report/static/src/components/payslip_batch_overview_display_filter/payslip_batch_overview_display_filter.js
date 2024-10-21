/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { Component } from "@odoo/owl";

export class PayslipBatchOverviewDisplayFilter extends Component {
    static template = "hr_payslip_batch_report.PayslipBatchOverviewDisplayFilter";
    static components = {
        Dropdown
    };
    static props = {
        showOptions: Object,
        displayOptions: Object,
        changeDisplay: Function,
    };

    get displayableOptions() {
        return Object.keys(this.props.displayOptions).map(optionKey => ({
            id: optionKey,
            label: this.displayOptions[optionKey],
            onSelected: () => this.props.changeDisplay(optionKey),
            class: { o_menu_item: true, selected: this.props.showOptions[optionKey] },
            closingMode: "none",
        }));
    }
}
