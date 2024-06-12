// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt

{
    function refresh(frm) {
        set_queries(frm);
    }

    async function set_queries(frm) {
        const issue_workflow_states = await get_issue_workflow_states(frm);

        frm.set_query("allow_timesheets_against_states", function() {
            const filters = {
                "name": ["in", issue_workflow_states],
            };

            return { filters };
        });
    
    }

    async function get_issue_workflow_states(frm) {
        const response = await frm.call("get_issue_workflow_states");

        if (!response.message) {
            frappe.throw("No states found!");
        }

        return response.message;
    }

    frappe.ui.form.on("Tz Settings", {
        refresh,
    });	
}
