
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { handleCheckIdentity } from "@portal/js/portal_security";

publicWidget.registry.RemoveLeave = publicWidget.Widget.extend({
    selector: '.fa.fa-trash.text-danger',
    events: {
        click: '_onClick'
    },

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
        this.dialog = this.bindService("dialog");
    },

    async _onClick(e) {
        e.preventDefault();
        //        await handleCheckIdentity(
        //            this.proxy('_rpc'),
        //            this._rpc({
        //                model: 'hr.leave',
        //                method: 'unlink',
        //                args: [parseInt(this.target.id)]
        //            })
        //        );
        await handleCheckIdentity(
            this.orm.call("hr.leave", "unlink", [parseInt(this.target.id)]),
            this.orm,
            this.dialog
        );
        window.location = window.location;
    }
});