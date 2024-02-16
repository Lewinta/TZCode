{
    frappe.require("/assets/tzcode/js/timer.js");

    function setup(_) {
        _hide_erpnext_buttons()
    }
    
    function refresh(frm) {
        // not sure if anyone else wants this functionality
        _setup_user_preferences(frm)
        if (["yefritavarez@tzcode.tech", "lewinvillar@tzcode.tech"].includes(frappe.session.user) ) {
            _toggle_sidebar_if_needed(frm);
        }
        _add_privileged_custom_buttons(frm);
        _render_go_to_client_system_btn(frm);
        _add_timesheet_btn(frm);
        _notify_of_duplicates_presence(frm);
    }

    function _hide_erpnext_buttons() {
        const style = document.createElement("style")
        style.innerHTML = `
            #page-Issue div[data-label=${__("Create")}],
            #page-Issue button[data-label=${__("Close")}],
            #page-Issue button[data-label=${__("Reopen")}]
            { display: none; }
        `
        document.head.appendChild(style)
    }
    
    function _add_privileged_custom_buttons(frm) {
        // this is only for Support Manager... for now!
        const privileged_roles = [
            "Support Manager",
            "System Manager",
        ]

        if (!frappe.user.has_role(privileged_roles)) {
            return "Not a privileged user"
        }

        _add_remove_remote_reference_btn(frm)
        _add_toggle_preview_btn(frm)
    }
    
    function _setup_user_preferences(frm) {
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
                _toggle_sidebar({ frm, display: cint(is_visible) });

                sessionStorage.setItem(storageKey, cint(is_visible));
            })
        ;
    }
    
    // let's not wait for this function
    async function _toggle_sidebar_if_needed(frm) {
        const storageKey = "hide_sidebar";
        const hide = sessionStorage.getItem(storageKey);

        _toggle_sidebar({ frm, display: !cint(hide) });
    }
    
    function _toggle_sidebar({ frm, display = false }) {
        const { wrapper } = frm.page;

        wrapper
            .find("div.layout-side-section")
            .toggle(display)
        ;
    }
    
    function _render_go_to_client_system_btn(frm) {
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
    function _add_timesheet_btn(frm) {
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

    function _notify_of_duplicates_presence(frm) {
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

    function _add_remove_remote_reference_btn(frm) {
        const { doc } = frm

        const allowed_states = [
            "Pending",
            "Ack",
            "Ready for Development",
        ]

        if (
            doc.remote_reference
            && allowed_states.includes(doc.workflow_state)
        ) {
            const label = "Remove Remote Reference"
            const action = _on_remove_remote_reference.bind(null, frm)
            frm.add_custom_button(label, action)
        }
    }

    function _on_remove_remote_reference(frm) {
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

    function _add_toggle_preview_btn(frm) {
        const label = "Toggle Preview"
        const action = _on_toggle_preview.bind(null, frm)
        frm.add_custom_button(label, action)
    }

    function _on_toggle_preview(frm) {
        const { doc } = frm
        doc.docstatus = doc.docstatus === 0? 1: 0
        frm.refresh_fields()
    }

    frappe.ui.form.on("Issue", {
        setup,
        refresh, 
    })
}