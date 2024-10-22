/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
//import ajax from 'web.ajax';

publicWidget.registry.omniPortalAttendance = publicWidget.Widget.extend({
    selector: '.o_portal',
    events: {
        "click .omni_hr_attendance_sign_in_out_icon": "_checker",
        "click .list_view_js": "_list",
    },

    _checker: async function (event){
        event.preventDefault();
        await rpc('/omni/my/attendance/update',{});
        window.location.reload();

    },

    _list: async function (event){
        event.preventDefault();
        window.location.href = '/omni/my/attendance/list_view';

    }
});