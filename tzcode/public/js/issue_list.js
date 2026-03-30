{
	const focus_lst = [];
	let focus_on = false;
	let btn_added = false;
	const filters = [
		[
			"Issue",
			"workflow_state",
			"in", [
				"Pending",
				"Ack",
				"Working",
				"On Going",
				"Help Requested",
				"Help Provided",
				"On Hold",
				"Ready for QA",
				"Testing",
				"Ready for Development",
				"Code Quality Passed",
				"Viewed But Yikes",
				"No code to Review",
				"Code Quality Rejected",
				"Awaiting Customer",
				"Acceptance Criteria Met",
				"Acceptance Criteria not Met",
				"Deploying in Production",
				// "Completed",
			]
		],
		[
			"Issue",
			"customer",
			"not in", [
				"HELADOM SRL",
			]
		],
	]

	if (!frappe.user.has_role("Support Manager")) {
		filters.push(["Issue", "_assign", "like", `%${frappe.session.user}%`])
	}

	function refresh(listview) {
		// not sure if anyone else want this functionality
		if (frappe.session.user === "yefritavarez@tzcode.tech") {
			hide_sidebar(listview)
		}

		add_skip_completed_btn(listview);
		if (!focus_on && focus_lst.length > 0 && !btn_added) {
			btn_added = true;
			listview.page.add_button("⌚︎ Focus", function() {
				this.remove();
				focus_on = true;
				btn_added = false;
				listview.filter_area.clear()
				listview.filter_area.set([
					[
						"Issue", "name", "in", focus_lst,
					]
				]);
			});
		}

		if (focus_on && focus_lst.length > 0 && !btn_added) {
			btn_added = true;
			listview.page.add_button("Reset Filtrs", function(event) {
				this.remove();
				focus_on = false;
				btn_added = false;
				listview.filter_area.clear()
				listview.filter_area.set(filters)
			});
		}
		itops.floating_menu.add(
			"Reset Filtrs", function(event) {
				listview.filter_area.clear()
				listview.filter_area.set(filters)
			}
		);


		setTimeout(() => {
			if (
				frappe.session.user === "yefritavarez@tzcode.tech"
				&& hashesCount === 0
				&& holdCount !== 0
				&& !notified
			) {
				frappe.show_alert({
					message: __("You might want to check the issues on hold now that you don't have any pending issues"),
					indicator: "blue",
				});

				notified = true;
			}

			hashesCount = 0;
			holdCount = 0;
		}, 3200);
	}

	function add_skip_completed_btn(listview) {

		if (
			"toggle_completed" in listview.page.fields_dict
		) {
			return; // already added
		}

		// 
		// const skip_completed = eval(
		// 	frappe.get_cookie("skip_completed_like_issues")
		// );

		// if (skip_completed) {

		// }
	
		const skip_completed_btn = listview.page.add_field({
			fieldtype: "Button",
			fieldname: "toggle_completed",
			label: __("Non | Completed"),
			click(event) {
				const method = "tzcode.controllers.overrides.issue.toggle_skip_completed_like_issues";
				const args = null;

				frappe.xcall(method, args)
					.then(async _ => {
						frappe.show_alert({
							message: __("Filter toggled successfully!"),
							indicator: "green",
						});

						frappe.dom.freeze("Wait a moment...");
						await frappe.timeout(1);
						listview.refresh();
						frappe.dom.unfreeze();

						if (frappe.session.user === "yefritavarez@tzcode.tech") {
							const skip_completed = eval(
								frappe.get_cookie("skip_completed_like_issues")
							);

							let message = "You are now seeing all the issues";

							if (skip_completed) {
								message = "You are now skipping the completed issues";
							}

							frappe.show_alert({
								message: __(message),
								indicator: "blue",
							});
						}
					}, _ => {
						frappe.show_alert({
							message: __("An error occurred while trying to toggle the filter"),
							indicator: "red",
						});
					});
			}
		}, listview.filter_area.standard_filters_wrapper);

		const { $input: input, $wrapper: wrapper } = skip_completed_btn;

		wrapper.removeAttr("title")
		wrapper.removeAttr("data-original-title")
		;

		input
			.removeClass("btn-default")
			.addClass("btn-link")
			.attr("title", "Toggle Display Completed Monkeys") // add tooltip text
			.attr("data-toggle", "tooltip") // enable tooltip
			.attr("data-placement", "bottom") // place the tooltip on top of the item
			.tooltip()
		;
	}

	function onload(listview) {
		const { page } = listview

		const { workflow_state } = page.fields_dict

		if (!workflow_state) {
			return "Not a workflow state"
		}

		workflow_state.get_query = function () {
			// valid states
			const states = [
				"Pending",
				"Ack",
				"Ready for Development",
				"Working",
				"On Going",
				"Help Requested",
				"Help Provided",
				"On Hold",
				"Ready for QA",
				"Testing",
				"Code Quality Passed",
				"Viewed But Yikes",
				"No code to Review",
				"Code Quality Rejected",
				"Awaiting Customer",
				"Acceptance Criteria Met",
				"Acceptance Criteria not Met",
				"Duplicated",
				"Forgotten",
				"Deploying in Production",
			]

			if (frappe.user.has_role("Support Manager")) {
				states.push("Closed")
				states.push("Completed")
			}

			const filters = {
				name: ["in", states],
			}

			return { filters }
		};

/*
		if (
			frappe.utils.is_xs()
			|| frappe.utils.is_md()
		) {
			itops.floating_menu.add(
				"Reset Filtrs", function(event) {
					listview.filter_area.clear()
					listview.filter_area.set(filters)
				}
			);
		} else {
			listview.page.add_button("Reset", function(event) {
				listview.filter_area.clear()
				listview.filter_area.set(filters)
			}, {
				icon: "filter",
				btn_class: "btn-link",
			})
				.attr("title", "Resets all the filters") // add tooltip text
				.attr("data-toggle", "tooltip") // enable tooltip
				.attr("data-placement", "bottom") // place the tooltip on top of the item
				.tooltip()
			;
		}
*/
	}

	function on_update(listview) {
		console.log("Do something on update")
	}

	function hide_sidebar(listview) {
        const { wrapper } = listview.page;
        
        wrapper
            .find("div.layout-side-section")
            .hide()
        ;
    }


	function get_indicator(doc) {
		const is_delayed = doc.due_date && doc.due_date < frappe.datetime.now_date();

		// let's sort the colors:
		//
		// red -> real bad (delayed tickets)
		// pink -> something bad (pending, ack)
		// orange -> not so good (ready for development, on hold with a due date and not delayed, code quality rejected, acceptance criteria not met, working, ready for qa, deploying in production, ,)
		// yellow -> not so bad ()
		// purple -> neutral
		// blue -> good
		// cyan -> real good
		// green -> real good
		// darkgrey
		// grey

		const indicator = {
			"Pending": "pink",
			"Ack": "pink",
			"Ready for Development": is_delayed ? "red": "orange",
			"Working": is_delayed ? "red": "yellow",
			"Help Requested": is_delayed ? "red": "yellow",
			"Help Provided": is_delayed ? "red": "yellow",
			"Ready for QA": is_delayed ? "red": "purple",
			"Testing": is_delayed ? "blue": "blue",
			"On Hold": "grey",
			"Code Quality Passed": "cyan",
			"Viewed But Yikes": "orange",
			"No code to Review": "blue",
			"Acceptance Criteria Met": "green",
			"Code Quality Rejected": is_delayed ? "red": "orange",
			"Acceptance Criteria not Met": is_delayed ? "red": "orange",
			"Awaiting Customer": "blue",
			"Completed": "green",
			"Closed": "green",
			"Duplicated": "darkgrey",
			"Deploying in Production": is_delayed ? "red": "yellow",
			"Forgotten": "darkgrey",
		}[doc.workflow_state];

		let state = ": On Time"
		if (is_delayed) {
			state = ": Delayed"
		}

		const non_expirables = [
			"On Hold",
			"Forgotten",
			"Duplicated",
			// "Code Quality Passed",
			// "Viewed But Yikes",
			// "Acceptance Criteria Met",
			// "Deploying in Production",
			"Awaiting Customer",
			"Completed",
			"Closed",
		]

		let _state = doc.workflow_state;

		// let's get fancy here...
		// 💢💦💤💨💫🆘❇️🕢🈂️㊙️🍨
		if (doc.workflow_state === "Code Quality Passed") {
			_state = " 🤗 Code Quality Passed"
		} else if (doc.workflow_state === "Viewed But Yikes") {
			_state = "🤷‍♂️ Viewed But Yikes"
		} else if (doc.workflow_state === "No code to Review") {
			_state = "🍨 No code to Review"
		} else if (doc.workflow_state === "Acceptance Criteria Met") {
			_state = "👍 Acceptance Criteria Met"
		} else if (doc.workflow_state === "Code Quality Rejected") {
			_state = "💫 Code Quality Rejected"
		} else if (doc.workflow_state === "Acceptance Criteria not Met") {
			_state = "💫 Acceptance Criteria not Met"
		} else if (doc.workflow_state === "Awaiting Customer") {
			_state = "🕢 Awaiting Customer"
		} else if (doc.workflow_state === "Ready for QA") {
			_state = "🎉 Ready for QA"
		} else if (doc.workflow_state === "Testing") {
			_state = "🛂 Testing"
		} else if (doc.workflow_state === "Ready for Development") {
			_state = "✨ Ready for Development"
		} else if (doc.workflow_state === "On Hold") {
			_state = "🚫 On Hold"
		} else if (doc.workflow_state === "Working") {
			_state = "🪄 Working"
		} else if (doc.workflow_state === "Help Requested") {
			_state = "🆘 Help Requested"
		} else if (doc.workflow_state === "Help Provided") {
			_state = "🛟 Help Provided"
		} else if (doc.workflow_state === "Deploying in Production") {
			_state = "🔨 Deploying in Production"
		} else if (doc.workflow_state === "Ack") {
			_state = "📝 Ack"
		} else if (doc.workflow_state === "Pending") {
			_state = "🆕 Pending"
		} else if (doc.workflow_state === "Completed") {
			_state = "🏁 Completed"
		} else if (doc.workflow_state === "Closed") {
			_state = "✅ 🤷‍♂️ Closed"
		} else if (doc.workflow_state === "Duplicated") {
			_state = "💢 Duplicated"
		} else if (doc.workflow_state === "Forgotten") {
			_state = "💤 Forgotten"
		}

		if (
			!doc.due_date
			|| non_expirables.includes(doc.workflow_state)
		) {
			state = ""
		} else {
			if (is_delayed) {
				_state = `🕢 ${_state}`
			}
		}

		if (
			doc.issue_type === "Epic"
		) {
			if (doc.workflow_state !== "Completed") {
				return [`🧶 Epic: On Going`, "green", "workflow_state,=," + doc.workflow_state];
			} else {
				return [`🥂 Epic: ${_state}${state}`, "green", "workflow_state,=," + doc.workflow_state];
			}
		}

		return [`${_state}${state}`, indicator, "workflow_state,=," + doc.workflow_state]
	}

	function get_cleaned_name(name) {
		// ISS-YYYY-NNNNN
		// We only want to show the last 5 digits
		return name.split("-").slice(-1)[0]
	}

	function generate_hash({ length = 16 }) {
		// Generate random bytes of specified length
		const randomBytes = new Uint8Array(length);
		window.crypto.getRandomValues(randomBytes);
		
		// Convert bytes to hexadecimal string
		return randomBytes.reduce((acc, byte) => acc + byte.toString(16).padStart(2, '0'), '');
	}

	function animateByHash(hash) {
		let el;
		setTimeout(() => {
			el = jQuery(`#${hash}`)
				.parents("div.level.list-row")
				.get(0)
			;
			el.style.border = "2px dashed var(--brand-color)";
		}, 1000);

		// setInterval(() => {
		// 	// .find("div.level-left.ellipsis")
		// 	if (!el) {
		// 		el = jQuery(`#${hash}`)
		// 			.parents("div.level.list-row")
		// 			.get(0)
		// 		;
		// 	}

		// 	el.style.border = "2px dashed var(--brand-color)";
		// 	// el.style.boxShadow = "rgba(35, 40, 47, .15) 1px 1px 5px 4px";
			
		// 	setTimeout(() => {
		// 		el.style.border = "2px dashed transparent";
		// 		// el.style.boxShadow = "none";
		// 	}, 1000);
		// }, 2000);
	}

	let hashesCount = 0;
	let holdCount = 0;
	let notified = false;
	function customer_formatter(value, doc) {
		const indicator = [value, "", "customer,=," + doc.customer];
		const title = __("Customer: {0}", [value]);

		const hash = generate_hash({ length: 16 });

		if (doc.workflow_state === "On Hold") {
			holdCount++;
		}

		if (
			(
				frappe.session.user === "yefritavarez@tzcode.tech"
					&& (
						["Pending", "Ack", "Ready for QA"].includes(doc.workflow_state)
						&& doc.customer !== "HELADOM SRL"
					) || (
						["Help Requested"].includes(doc.workflow_state)
					) && (
						!doc.helper_user || doc.helper_user === "yefritavarez@tzcode.tech"
					)
			) || (
				frappe.session.user === "yefritavarez@tzcode.tech"
					&& ["Code Quality Passed", "Viewed But Yikes", "No code to Review"].includes(doc.workflow_state)
					&& !doc.approver
			) || (
				frappe.session.user === "brenorramirez@tzcode.tech"
					&& ["Code Quality Passed", "Viewed But Yikes", "No code to Review"].includes(doc.workflow_state)
					&& doc.approver === frappe.session.user
			) || (
				frappe.session.user === "lewinvillar@tzcode.tech"
					&& ["Code Quality Passed", "Viewed But Yikes", "No code to Review"].includes(doc.workflow_state)
					&& doc.approver === frappe.session.user
			) || (
				["miguel.higuera@tzcode.tech", "rainierpolanco@tzcode.tech", "reyferreras@tzcode.tech", "brenorramirez@tzcode.tech", "lewinvillar@tzcode.tech", "yefritavarez@tzcode.tech"].includes(frappe.session.user)
					&& ["Ready for Development", "Code Quality Rejected", "Acceptance Criteria not Met", "Acceptance Criteria Met"].includes(doc.workflow_state)
					&& doc.resolver === frappe.session.user
			)
		) {
			animateByHash(hash);
			focus_lst.push(doc.name);
			hashesCount++;
		}
		
		return `
			<span
				id="${hash}"
				class="indicator-pill ${indicator[1]} filterable ellipsis"
				data-filter="${indicator[2]}"
				title="${title}"
				style="
					background: var(--brand-color);
					background: linear-gradient(10deg, var(--bg-purple) 0%, var(--bg-pink) 100%);
					color: var(--fg-on-pink);
				"
			>
				<span class="ellipsis"> ${__(indicator[0])}</span>
			</span>
		`;
	}

	frappe.listview_settings["Issue"] = {
		refresh,
		onload,
		on_update,
		filters,
		get_indicator,
		formatters: {
			customer(value, df, doc) {
				if (
					frappe.session.user === "yefritavarez@tzcode.tech"
				) {
					if (
						doc.remote_reference
					) {
						return customer_formatter(
							`${doc.remote_reference} - ${doc.customer || doc.raised_by}`, doc
						);
					}

					return customer_formatter(
						`${doc.customer || doc.raised_by}`, doc
					);
				}

				return customer_formatter(
					doc.customer || doc.raised_by, doc
				);
			},
			subject(value, df, doc) {
				const name = get_cleaned_name(doc.name);
				const points = doc.estimated_points? cint(doc.estimated_points): "?";
				const subject = doc.subject;
				const workflow_state = doc.workflow_state;

				if (
					frappe.utils.is_xs()
					|| frappe.utils.is_sm()
				) {
					return `
						${name} [${points}] ${workflow_state} | ${subject}
					`;
				}

				return `
					${name} [${points}] ${subject}
				`;
			},
			status(value, df, doc) {
				console.log("Do something with status")
			},
			workflow_state(value, df, doc) {
				return "ehlo";
			}
		},
		hide_name_column: 1,
		colwidths: { "subject": 6 },
		add_fields: ["priority", "issue_type", "customer", "approver", "resolver", "workflow_state", "due_date", "estimated_points", "remote_reference", "helper_user", "raised_by"],
	}
}