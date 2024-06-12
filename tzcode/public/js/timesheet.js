// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
    function refresh(frm) {
        _render_summary_table(frm);
    }

    function _render_key(key, details) {
        if (key.startsWith("ISS-")) { // then it's a link
            const { subject, workflow_state, estimated_points } = details[key];
            return `<a href="/app/issue/${key}">${key}: ${subject} [${workflow_state}${cint(estimated_points) > 0 ? " | "  + cstr(estimated_points) + " pts ": ""}]</a>`;
        }

        return key;
    }

    function _get_details(doc) {
        const { __onload: details } = doc;

        if (!details) {
            return {};
        }

        return details.issue_details;
    }

    function _render_summary_table(frm) {
        const { doc } = frm;

        if (!doc.time_logs) {
            return jQuery(frm.fields_dict.summary.wrapper).html("");
        }

        const details = _get_details(doc);

        const logs = {};

        for (const timesheet_detail of doc.time_logs) {
            const key = timesheet_detail.issue || timesheet_detail.activity_type;

            if (!logs[key]) {
                logs[key] = [0, 0];
            }

            logs[key][0] += 1;
            logs[key][1] += timesheet_detail.hours;
        }

        const summary = `
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Issue</th>
                        <th>Sessions</th>
                        <th>Total Hours</th>
                    </tr>
                </thead>
                <tbody>
                    ${
                        Object.keys(logs)
                            .map(
                                    (key) => (`
                                    <tr>
                                        <td>
                                            ${_render_key(key, details)}
                                        </td>
                                        <td>${logs[key][0]}</td>
                                        <td>${flt(logs[key][1], 2)} Hrs</td>
                                    </tr>
                                `)
                            ).join("")
                    }
                </tbody>
            </table>
        `;

        // jQuery(frm.fields_dict.summary.wrapper).html(summary);
        jQuery(`div[data-fieldtype="HTML"][data-fieldname="summary"]`)
            .html(summary)
            .css({
                "margin-top": "15px",
                "padding": "15px",
                "border": "1px solid #ccc",
                "border-radius": "5px",
            });
    }

    frappe.ui.form.on("Timesheet", {
        refresh,
    });
}