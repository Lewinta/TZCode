{
    frappe.provide("itops");
    frappe.require("/assets/tzcode/js/timer.js");

    function setup(frm) {
        add_custom_css();
        hide_erpnext_buttons();
        add_copy_reference_btn(frm);
    }
    
    function onload_post_render(frm) {
        setup_estimated_points_display(frm);
    }

    function refresh(frm) {
        // not sure if anyone else wants this functionality
        setup_user_preferences(frm);

        const users = [
            "yefritavarez@tzcode.tech",
            "lewinvillar@tzcode.tech",
        ];

        if (
            users.includes(frappe.session.user)
        ) {
            toggle_sidebar_if_needed(frm);
        }
        add_custom_buttons(frm);
        add_privileged_custom_buttons(frm);
        // add_goto_issue_listview_button(frm);
        render_go_to_client_system_btn(frm);
        add_timesheet_btn(frm);
        notify_of_duplicates_presence(frm);
        render_elapsed_time(frm);
        disable_fields(frm);

        frm.toggle_reqd("customer", true);
    }

    function after_save(frm) {
        frm.derive_prompt = null;
    }

    let reject_prompt = null;
    function before_workflow_action(frm) {
        const { doc, selected_workflow_action } = frm;
    
        return new Promise((resolve, reject) => {
            if (selected_workflow_action === "Reject") {
                frappe.dom.unfreeze();

                ask_for_rejection_reason(frm, resolve, reject);
            } else if (
                [
                    "Mark as Reviewed", "Change to Code Reviewed"
                ].includes(selected_workflow_action)
            ) {
                frappe.dom.unfreeze();

                ask_for_not_approved_reason(frm, resolve, reject);
            } else if (selected_workflow_action === "Put On Hold") {
                frappe.dom.unfreeze();
                
                ask_for_holding_reason(frm, resolve, reject);
            } else if (
                "Set Back to Open" === selected_workflow_action
                && ["Closed", "Completed"].includes(doc.workflow_state)
            ) {
                frappe.dom.unfreeze();
                ask_for_reopen_reason_reason(frm, resolve, reject);
            } else if (selected_workflow_action === "Deliver for QA") {
                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, "Ready for QA", resolve, reject);
            } else if (selected_workflow_action === "Set Back to Open") {
                const next_state = {
                    "Ready for Development": "Ack",
                    "Duplicated": "Ack",
                    "Forgotten": "Ack",
                    "Completed": "Ack",
                    "On Hold": frappe.user.has_role(["Support Manager"])? "Ready for Development": "Working",
                }[doc.workflow_state];
                
                if (!next_state) {
                    resolve();
                    return;
                } else {
                    frappe.dom.unfreeze();
                }

                ask_for_confirmation_transition(frm, next_state, resolve, reject);
            } else if (selected_workflow_action === "Ask for Help") {
                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, "Help Requested", function() {
                    frappe.prompt_minizable([{
                        "fieldname": "helper_user",
                        "fieldtype": "Link",
                        "options": "User",
                        "label": __("User"),
                        "get_query": function() {
                            return {
                                "filters": {
                                    "name": ["!=", frappe.session.user],
                                    "user_type": "System User",
                                    "enabled": 1,
                                },
                            }
                        },
                        "description": `Leave empty to ask for help to the next available user.`,
                    },
                    {
                        "fieldname": "helper_notes",
                        "fieldtype": "Text Editor",
                        "label": __("What do you need help with?"),
                        "reqd": 1,
                    }], ({ helper_user, helper_notes }) => {
                        frappe.db.set_value("Issue", doc.name, {
                            "helper_user": helper_user,
                            "helper_notes": helper_notes,
                        }, null, function({ message: docs }) {
                            if (docs) {
                                frappe.model.sync([docs]);
                            } else {
                                // reject();
                            }
                            resolve();
                        });
                    }, __("Ask for Help"), __("Ask"));
                }, reject);
            } else if (selected_workflow_action === "Cancel Help") {
                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, "Working", function() {
                    frappe.db.set_value("Issue", doc.name, {
                        "helper_user": null,
                        "helper_notes": null,
                    }, null, function({ message: docs }) {
                        if (docs) {
                            frappe.model.sync([docs]);
                        } else {
                            // reject();
                        }
                        resolve();
                    });
                }, reject);
            // } else if (selected_workflow_action === "") {
            //     frappe.dom.unfreeze();
            //     ask_for_confirmation_transition(frm, "Code Quality Passed", resolve, reject);
            } else if (selected_workflow_action === "Approve") {
                let next_state = "Code Quality Passed";
                if (doc.workflow_state === "Code Quality Passed") {
                    next_state = "Acceptance Criteria Met";
                }

                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, next_state, resolve, reject);
            } else if (selected_workflow_action === "Mark as Duplicate") {
                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, "Duplicated", resolve, reject);
            } else if (selected_workflow_action === "Complete") {
                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, "Completed", resolve, reject);
            } else if (selected_workflow_action === "Skip Production Deployment") {
                frappe.dom.unfreeze();
                ask_for_confirmation_transition(frm, "Completed", resolve, reject);
            } else {
                resolve();
            }
        });

    }

    function add_custom_css() {
        const style = `
            <style type="text/css">
                div[id="page-Issue"]
                .page-title .title-area .title-text {
                    max-width: 50% !important;
                }
            </style>
        `;

        jQuery(style)
            .appendTo(document.head)
        ;
    }

    function hide_erpnext_buttons() {
        const style = document.createElement("style")
        style.innerHTML = `
            #page-Issue div[data-label=${__("Create")}],
            #page-Issue button[data-label=${__("Close")}],
            #page-Issue button[data-label=${__("Reopen")}]
            { display: none; }
        `
        document.head.appendChild(style)
    }
    
    function add_custom_buttons(frm) {
        const { doc }  = frm;

        if (!doc.customer) {
            return ; // no customer, no buttons
        }

        frappe.db.get_list("Customer Database", {
            filters: {
                "enabled": 1,
                "customer": doc.customer,
            },
            fields: ["name", "development_site"],
        }).then(sites => {
            if (!sites) {
                return ; // no customer database
            }

            for (const { name: url, development_site } of sites) {
                const label = `${development_site? "Dev": "Prod"} - ${url}`
                frm.add_custom_button(
                    label, function() {
                        // open in new tab each site
                        window.open(`https://${url}/login`, "_blank");
                    }, "Open Site"
                );
            }
        });
    }
    
    function add_privileged_custom_buttons(frm) {
        // this is only for Support Manager... for now!
        const privileged_roles = [
            "Support Manager",
            "System Manager",
        ]

        // temporary enable all users to view these buttons
        add_create_child_issue_from_epic(frm)
        add_view_child_issues_from_epic(frm)
        add_view_epic_button(frm)
        
        if (!frappe.user.has_role(privileged_roles)) {
            return "Not a privileged user"
        }

        // add_remove_remote_reference_btn(frm)
        // add_toggle_preview_btn(frm)
    }
    
    function add_goto_issue_listview_button(frm) {
        if (
            !frappe.utils.is_xs()
        ) {
            return; // add the button only for SM
        }

        const route_str = frappe.get_route_str();
        const label = "Goto Issue List";
        function action() {
            frappe.set_route("List", "Issue");
        }

        if (
            route_str === "List/Issue/List"
        ) {
            
        } else {
            itops.floating_menu.add(label, action);
        }
    }
    
    function setup_user_preferences(frm) {
        // 
        const storageKey = "hide_sidebar";
        const userPreference = sessionStorage.getItem(storageKey); 
       
        if (
            userPreference === null
        ) {
            // let's set it to 1, this is default
            sessionStorage.setItem(storageKey, 1);
        }

        jQuery("div[id=page-Issue] span[class=sidebar-toggle-btn]")
            .off("click")
            .click(async function(_) {
                // await frappe.timeout(1); // let's wait 1 sec for the rendering to take place
                const is_visible = frm.page.sidebar.is(":visible");
                toggle_sidebar({ frm, display: cint(is_visible) });

                sessionStorage.setItem(storageKey, cint(is_visible));
            })
        ;
    }
    
    // let's not wait for this function
    async function toggle_sidebar_if_needed(frm) {
        const storageKey = "hide_sidebar";
        const hide = sessionStorage.getItem(storageKey);

        toggle_sidebar({ frm, display: !cint(hide) });
    }
    
    function toggle_sidebar({ frm, display = false }) {
        const { wrapper } = frm.page;

        wrapper
            .find("div.layout-side-section")
            .toggle(display)
        ;
    }
    
    function render_go_to_client_system_btn(frm) {
        const { doc, fields_dict } = frm

        if (doc.host_url) {
            const { wrapper } = fields_dict.host_url
            jQuery(wrapper).find("button.btn-default").remove()
            jQuery("<button class='btn btn-default btn-xs'>Go to Client System</button>")
                .click(() => {
                    window.open(`${doc.host_url}/login`, "_blank")
                })
                .appendTo(wrapper)
        }
    }
    function add_timesheet_btn(frm) {
        if (frm.is_new())
            return;
        
        const { doc } = frm;
        const method = "tzcode.controllers.overrides.issue.issue.get_open_timers";
        const args = { issue_name: doc.name, user: frappe.session.user };
        
        frappe.call({ method, args}).then( response => {
            frm.timer = response.message;
            let button = !response.message || response.message.length == 0 ? 'Start Timer' : 'Stop Timer';
            let timer_btn = frm.add_custom_button(__(button), function() {
                if (button === 'Start Timer')
                    tzcode.issue.timer();
                
                else {
                    let row = frm.timer[0];
                    if(row.from_time > frappe.datetime.now_datetime())
                        frappe.throw(__("The timer was started in the future. Please check the timelogs."));
                    else {
                        let timestamp = moment(frappe.datetime.now_datetime()).diff(moment(row.from_time),"seconds");
                        tzcode.issue.timer(row, timestamp);
                    }
                }
            });
            timer_btn.removeClass('btn-default');
            timer_btn.addClass(button === 'Start Timer'? "btn-success": "btn-danger");
        });
        

		// 	frm.add_custom_button(__(button), function() {
		// 		var flag = true;
		// 		$.each(frm.doc.time_logs || [], function(i, row) {
		// 			// Fetch the row for which from_time is not present
		// 			if (flag && row.activity_type && !row.from_time){
		// 				erpnext.timesheet.timer(frm, row);
		// 				row.from_time = frappe.datetime.now_datetime();
		// 				frm.refresh_fields("time_logs");
		// 				frm.save();
		// 				flag = false;
		// 			}
		// 			// Fetch the row for timer where activity is not completed and from_time is before now_time
		// 			if (flag && row.from_time <= frappe.datetime.now_datetime() && !row.completed) {
		// 				let timestamp = moment(frappe.datetime.now_datetime()).diff(moment(row.from_time),"seconds");
		// 				erpnext.timesheet.timer(frm, row, timestamp);
		// 				flag = false;
		// 			}
		// 		});
		// 		// If no activities found to start a timer, create new
		// 		if (flag) {
		// 			erpnext.timesheet.timer(frm);
		// 		}
		// 	}).addClass("btn-primary");
    }

    function notify_of_duplicates_presence(frm) {
        const { __onload: data } = frm.doc;
        if (!data) {
            return; // no data, no duplicates
        }

        if (data.duplicates.length === 0) {
            return; // no duplicates
        }

        let heading = `
            <h3>🚨 Looks like this ticket is duplicated with: </h3>
        `;

        let message = ``;

        if (data.duplicates.length === 1) {
            const [duplicate] = data.duplicates;
            const link = `<a href="/app/issue/${duplicate.name}" target="_blank">${duplicate.name}</a>`;
            
            message = `
                ▷ ${link}
            `;
        } else {
            message = `
                <ul>
                    ${data.duplicates.map(duplicate => {
                        const link = `<a href="/app/issue/${duplicate.name}" target="_blank">${duplicate.name}</a>`;
                        return `<li>${link}</li>`;
                    }).join("")}
                </ul>
            `;  
        }

        frm.set_intro(
            `${heading} ${message}`, `red`
        );
    }

    function render_elapsed_time(frm) {
        const field = frm.get_field("due_date");
        const { $wrapper: wrapper } = field;

        const { __onload: data } = frm.doc;

        if (!data) {
            wrapper.find("#elapsed_time").remove();
            return ; // no data, no timers
        }

        const { timers } = data;

        const docfield = {
            fieldtype: "Duration",
        };

        wrapper.find("#elapsed_time").remove();

        // sessions
        // employees
        // timesheets
        // total_seconds

        const [d] = timers;
        const content = wrapper.prepend(`
            <div id="elapsed_time" class="row" style="padding: 10px">
                <h4>Elapsed Time</h4>
                <table class="table table-condensed">
                    <tbody>
                        <tr>
                            <td style="width: 35%">Sessions</td>
                            <td style="width: 65%">${d.sessions}</td>
                        </tr>
                        <tr>
                            <td style="width: 35%">Timesheets</td>
                            <td style="width: 65%">
                                <a
                                    data-doctype="Timesheet"
                                    href="/app/timesheet/view/list"
                                >
                                    ${
                                        d.timesheets.length > 1? 
                                        d.timesheets.length: d.timesheets[0] || 0
                                    } (click to view)
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td style="width: 35%">Developers</td>
                            <td style="width: 65%" id="developers-av"></td>
                        </tr>
                        ${
                            d.users.length > 1?
                            Object.keys(d.details).map(key => {
                                const detail = d.details[key];
                                return `
                                    <tr>
                                        <td style="width: 35%">${detail.full_name}</td>
                                        <td style="width: 65%">
                                            Sessions: ${detail.sessions}<br>
                                            Duration: ${frappe.format(detail.seconds, docfield)}
                                        </td>
                                    </tr>
                                `;
                            }).join(""): ""
                        }
                        <tr>
                            <td style="width: 35%">First Log</td>
                            <td style="width: 65%">${frappe.format(d.oldest_log, {fieldtype: "Datetime"})}</td>
                        </tr>
                        <tr>
                            <td style="width: 35%">Last Log</td>
                            <td style="width: 65%">${d.newest_log !=  "Now"? 
                                frappe.format(d.newest_log, {fieldtype: "Datetime"})
                                : "<span class=\"indicator orange\">On Going</span>"
                            }</td>
                        </tr>
                        <tr>
                            <td style="width: 35%">Total Duration</td>
                            <td style="width: 65%">${frappe.format(d.total_seconds, docfield)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `);

        // content.css({
        //     "margin-top": "15px",
        //     "padding": "15px",
        //     "border": "1px solid #ccc",
        //     "border-radius": "5px",
        // });
        
        content.find("a[data-doctype=Timesheet]").click(function(e) {
            e.preventDefault();

            // ?name=${encodeURIComponent(JSON.stringify({"name": ["in", d.timesheets]}))}
            if (d.timesheets.length === 0) {
                frappe.show_alert({
                    message: __("This issue has no timesheets yet."),
                    indicator: "red",
                });

                return ; // no timesheets
            }

            if (d.timesheets.length === 1) {
                frappe.set_route("Form", "Timesheet", d.timesheets[0]);
            } else {
                frappe.route_options = {
                    name: ["in", d.timesheets],
                };

                frappe.set_route("List", "Timesheet");
            }
        });

        content.find("#developers-av")
            .prepend(frappe.avatar_group(d.users, 4))
    }

    function disable_fields(frm) {
        const fields = [
            // "naming_series",
            "subject",
            "customer",
            // "remote_reference",
            // "host_url",
            // "raised_by",
            "resolver",
            // "delivered_for_qa",
            // "assignation_date",
            "approver",
            // "closed_by",
            // "due_date",
            "status",
            "priority",
            "issue_type",
            "issue_domain",
            // "issue_split_from",
            "relates_to",
            "helper_user",
            // "helpers_name",
            "helper_notes",
            "description",
            "add_additional_criteria",
            "acceptance_criteria",
            // "service_level_agreement",
            // "response_by",
            // "agreement_status",
            // "resolution_by",
            // "service_level_agreement_creation",
            // "on_hold_since",
            // "total_hold_time",
            // "first_response_time",
            // "first_responded_on",
            // "avg_response_time",
            // "modified",
            "video_does_not_apply",
            "resolution_video",
            "image_does_not_apply",
            "resolution_image",
            "resolution_details",
            "custom_screen_capture_of_code",
            "custom_screen_capture_of_local_repo",
            // "captura_de_pantalla_del_repositorio_local__prod",
            "custom_superiors_satisfaction",
            "custom_unsatisfaction_notes",
            // "last_contact_date",
            // "next_contact_date",
            "notes",
            // "opening_date",
            // "opening_time",
            // "assigned_to",
            // "resolution_date",
            // "resolution_time",
            // "user_resolution_time",
            // "lead",
            // "contact",
            // "email_account",
            // "customer_name",
            // "project",
            // "company",
            // "via_customer_portal",
            // "attachment",
            // "content_type",
            // "reject_reason",
            // "hold_reason",
            // "reopen_reason",
            // "other_reasons"
        ];

        const { doc } = frm;

        let disabled = !frappe.user.has_role(
            ["Support Manager", "System Manager"]
        ) && ["Deploying in Production"].includes(doc.workflow_state);

        fields.forEach(field => {
            if (doc.workflow_state === "Working") {
                disabled = false;
            }

            frm.set_df_property(field, "read_only", disabled);
        });
    }

    function ask_for_rejection_reason(frm, resolve, reject) {
        const { doc } = frm;

        if (reject_prompt) {
            reject_prompt.show();
            return ; // don't show it again
        }

        reject_prompt = frappe.prompt_minizable([
            {
                fieldname: "reason",
                label: __("Reason"),
                fieldtype: "Text Editor",
                reqd: 1,
            },
        ], data => {
            frappe.dom.freeze();

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "Issue",
                    name: frm.doc.name,
                    fieldname: "reject_reason",
                    value: `
                        ${doc.reject_reason || ""}
                        <br>
                        <p class="text-muted">
                            ${frappe.user.full_name()} says
                        </p>
                        <p>${data.reason}</p>
                        <p>🔴 Rejected by ${frappe.user.full_name()}</p>
                        <p>🔴 Rejected on ${frappe.datetime.get_datetime_as_string()}</p>
                    `,
                },
                callback() {
                    reject_prompt = null;
                    resolve();
                },
            });

            // frm.set_value("reject_reason", data.reason);
            // resolve();
        }, 
        __("What is the reason for rejecting this issue?"),
        __("Reject"));

var fieldname = "reason";
var method = "itops.client.autocomplete_suggest";
var domain = "Issue Evaluation";
window.GhostAutocomplete.setupForDialog(reject_prompt, {
	fieldname,               // fieldname of the Text Editor control
	method,                  // dotted path to your whitelisted method
	domain,                  // string or function(frm) => string
	minChars: 3,
	debounceMs: 160,
	maxSuggestionChars: 120,
	styles: { color: '#999', opacity: 0.8, fontStyle: 'italic' }
})
    }

    function ask_for_not_approved_reason(frm, resolve, reject) {
        const { doc } = frm;

        frappe.prompt_minizable([
            {
                fieldname: "reason",
                label: __("Reason"),
                fieldtype: "Text Editor",
                reqd: 1,
            },
        ], data => {
            frappe.dom.freeze();

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "Issue",
                    name: frm.doc.name,
                    fieldname: "other_reasons",
                    value: `
                        ${doc.other_reasons || ""}
                        <br>
                        <h3>Reason why this is not Approved</h3>
                        <p class="text-muted">
                            ${frappe.user.full_name()} says:
                        </p>
                        <p>${data.reason}</p>
                        <p> 🙅🏻‍♂️ By ${frappe.user.full_name()}</p>
                        <p> 🗓️ On ${frappe.datetime.get_datetime_as_string()}</p>
                    `,
                },
                callback() {
                    resolve();
                },
            });

            // frm.set_value("reject_reason", data.reason);
            // resolve();
        }, 
        __("Specify why this is not Approved"),
        __("Mark as Reviewed"));
    }

    function ask_for_holding_reason(frm, resolve, reject) {
        const { doc } = frm;

        frappe.prompt_minizable([
            {
                fieldname: "reason",
                label: __("Reason"),
                fieldtype: "Text Editor",
                reqd: 1,
            },
        ], data => {
            frappe.dom.freeze();

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "Issue",
                    name: frm.doc.name,
                    fieldname: "hold_reason",
                    value: `
                        ${doc.hold_reason || ""}
                        <br>
                        <p class="text-muted">
                            ${frappe.user.full_name()} says:
                        </p>
                        <p>${data.reason}</p>
                    `,
                },
                callback() {
                    resolve();
                },
            });

            // frm.set_value("hold_reason", data.reason);
            // resolve();
        }, 
        __("What is the reason for holding this issue?"),
        __("Put On Hold"));
    }

    function ask_for_reopen_reason_reason(frm, resolve, reject) {
        const { doc } = frm;

        frappe.prompt_minizable([
            {
                fieldname: "reason",
                label: __("Reason"),
                fieldtype: "Text Editor",
                reqd: 1,
            },
        ], data => {
            frappe.dom.freeze();

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "Issue",
                    name: frm.doc.name,
                    fieldname: "reopen_reason",
                    value: `
                        ${doc.reopen_reason || ""}
                        <br>
                        <p class="text-muted">
                            ${frappe.user.full_name()} says:
                        </p>
                        <p>${data.reason}</p>
                    `,
                },
                callback() {
                    resolve();
                },
            });

            // frm.set_value("hold_reason", data.reason);
            // resolve();
        }, 
        __("What is the reason for reopening this issue?"),
        __("Set Back to Open"));
    }

    function ask_for_confirmation_transition(frm, state, resolve, reject) {
        frappe.confirm(
            `Are you sure you want to transition to "${state}"?`,
            () => {
                resolve();
            },
            () => {
                reject();
            }
        );
    }

    function unset_rejection_reason(frm, resolve, reject) {
        const { doc } = frm;

        if (!doc.reject_reason) {
            return resolve();
        }

        frappe.call({
            method: "frappe.client.set_value",
            args: {
                doctype: "Issue",
                name: frm.doc.name,
                fieldname: "reject_reason",
                value: "",
            },
            callback: resolve,
        });
    }

    function unset_holding_reason(frm, resolve, reject) {
        const { doc } = frm;

        if (!doc.hold_reason) {
            return resolve();
        }

        frappe.call({
            method: "frappe.client.set_value",
            args: {
                doctype: "Issue",
                name: frm.doc.name,
                fieldname: "hold_reason",
                value: "",
            },
            callback: resolve,
        });
    }

    cur_frm.derive_prompt = null;
    function add_create_child_issue_from_epic(frm) {
        const { doc } = frm;


        if (doc.issue_type !== "Epic") {
            return; // only for epics
        }

        const label = "Create";
        const action = () => {
            if (cur_frm.derive_prompt) {
                cur_frm.derive_prompt.show();
                return; // don't show it again
            }

            frm.derive_prompt = frappe.prompt([
                {
                    fieldname: "issue_type",
                    fieldtype: "Select",
                    label: __("Issue Type"),
                    options: [
                        "",
                        "Bug",
                        "New Feature",
                        "Task",
                        "Documentation",
                    ],
                    default: "New Feature",
                    reqd: 1,
                },
                {
                    fieldname: "subject",
                    fieldtype: "Data",
                    label: __("Subject"),
                    reqd: 1,
                },
                {
                    fieldname: "description",
                    fieldtype: "Text Editor",
                    label: __("Description"),
                    reqd: 1,
                },
            ], data => {
                frappe.new_doc("Issue", {
                    "relates_to": doc.name,
                    "customer": doc.customer,
                    "issue_domain": doc.issue_domain,
                    "host_url": doc.host_url,
                    "issue_type": data.issue_type,
                    "subject": `${data.subject} | ${doc.subject}`,
                }).then(function() {
                    cur_frm.set_value("description", data.description);
                });
            }, __("Create a Child Issue"), __("Open Issue"));
        };

        frm.add_custom_button(label, action, "Child Issues");
    }

    function add_view_child_issues_from_epic(frm) {
        const { doc } = frm;

        if (doc.issue_type !== "Epic") {
            return; // only for epics
        }

        const label = "View All";
        const action = () => {
            frappe.set_route("List", "Issue", {
                "relates_to": doc.name,
            });
        };

        frm.add_custom_button(label, action, "Child Issues");
    }

    function add_view_epic_button(frm) {
        const { doc } = frm;
        
        if (!doc.relates_to) {
            return; // no relates_to
        }

        const { __onload: { relates_to_details } } = doc;

        if (!relates_to_details) {
            return; // no details
        }

        const label = "View Epic";
        const action = () => {
            frappe.set_route(`/app/issue/${doc.relates_to}`);
        };

        frm.add_custom_button(label, action);
    }

    function add_remove_remote_reference_btn(frm) {
        const { doc } = frm

        const allowed_states = [
            "Pending",
            "Ack",
            "Ready for Development",
            "Working",
            "Duplicated",
            "Closed",
            "Forgotten",
        ]

        if (
            doc.remote_reference
            && allowed_states.includes(doc.workflow_state)
        ) {
            const label = "RRR"
            const action = on_remove_remote_reference.bind(null, frm)
            // frm.add_custom_button(label, action)
            itops.floating_menu.add(label, action);
        }
    }

    function on_remove_remote_reference(frm) {
        const { doc } = frm

        frappe.confirm(
            __("Are you sure you want to remove the remote reference?"),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Issue",
                        name: doc.name,
                        fieldname: "remote_reference",
                        value: "",
                    },
                    callback: () => {
                        frm.reload_doc()
                    },
                })
            }
        )
    }

    function add_toggle_preview_btn(frm) {

        const ctrl_label = frappe.utils.is_mac() ? '⌘' : 'Ctrl';
        const label = `Preview (${ctrl_label}+P)`
        const action = on_toggle_preview.bind(null, frm)
        // frm.add_custom_button(label, action);
        itops.floating_menu.add(label, action);



        frappe.ui.keys.add_shortcut({
            shortcut: "ctrl+p",
            action,
            condition: _ => true,
            description: __("Preview the current document"),
            ignore_inputs: true,
            page: cur_page.page.page
        });
    }



    function add_copy_reference_btn(frm) {
        const { doc } = frm
        if (!doc.remote_reference) {
            return; // the field might be hidden and empty
        }

        const { wrapper } = frm.fields_dict.remote_reference;
        const parent = jQuery(wrapper)
            .find("div.form-group > div.clearfix")
        ;

        jQuery(`
            <button class="btn btn-link btn-xs" title="Copy Text">
                <svg class="icon icon-sm">
                    <use
                        style="color: var(--text-color) !important;" 
                        href="#icon-duplicate"
                        class="like-icon"
                        data-original-title=""
                        title=""
                    ></use>
                </svg>
            </button>
            <br>
        `).click(function() {
            frappe.utils.copy_to_clipboard(cur_frm.doc.remote_reference);
        }).appendTo(parent);


    }

    function setup_estimated_points_display(frm) {
        const { doc } = frm;
        frm.set_df_property("estimated_points", "options", [
            {"label": "-", "value": "" },
            {"label": "1", "value": "1" },
            {"label": "3", "value": "3" }, 
            {"label": "5", "value": "5" }, 
            {"label": "8", "value": "8" }, 
            {"label": "13", "value": "13" }
        ]);

        if (
            !["", "1", "3", "5", "8", "13"].includes(
                cstr(doc.estimated_points)
            )
        ) {
            frm.set_df_property("estimated_points", "label", `Estimated Points (Invalid = [${doc.estimated_points}])`);
        }
    }

    function on_toggle_preview(frm) {
        const { doc } = frm;
        doc.docstatus = cint(doc.docstatus === 0);
        frm.refresh_fields();
    }

    frappe.ui.form.on("Issue", {
        setup,
        refresh,
        after_save,
        onload_post_render,
        before_workflow_action,
    })
}