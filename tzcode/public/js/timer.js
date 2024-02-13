frappe.provide("tzcode.issue");

tzcode.issue.timer = function(row, timestamp=0) {
	let dialog = new frappe.ui.Dialog({
		title: __("Timer"),
		fields:
		[
			{"fieldtype": "Link", "label": __("Activity Type"), "fieldname": "activity_type","reqd": 1, "options": "Activity Type"},
			{"fieldtype": "Link", "label": __("Issue"), "fieldname": "issue", "options": "Issue", "hidden": 1},
            {"fieldtype": "Column Break"},
			{"fieldtype": "Float", "label": __("Expected Hrs"), "fieldname": "expected_hours"},            
			{"fieldtype": "Link", "label": __("Timesheet"), "fieldname": "timesheet", "options": "Timesheet", "hidden": 1},
			{"fieldtype": "Data", "label": __("Log Name"), "fieldname": "log_name", "hidden": 1},
			{"fieldtype": "Section Break"},
			{"fieldtype": "HTML", "fieldname": "timer_html"}
		]
	});

    if (row) {
		dialog.set_values({
			'activity_type': row.activity_type,
			'expected_hours': row.expected_hours,
			'issue': row.issue,
			'timesheet': row.timesheet,
			'log_name': row.log_name,
            
		});
	}
    else { 
        dialog.set_value("issue", cur_frm.docname);
    }

	dialog.get_field("timer_html").$wrapper.append(get_timer_html());
	function get_timer_html() {
		return `
			<div class="stopwatch">
				<span class="hours">00</span>
				<span class="colon">:</span>
				<span class="minutes">00</span>
				<span class="colon">:</span>
				<span class="seconds">00</span>
			</div>
			<div class="playpause text-center">
				<button class= "btn btn-primary btn-start"> ${ __("Start") } </button>
				<button class= "btn btn-primary btn-complete"> ${ __("Complete") } </button>
			</div>
		`;
	}
	tzcode.issue.control_timer(dialog, row, timestamp);
	dialog.show();
};

tzcode.issue.control_timer = function(dialog, row, timestamp=0) {
	var $btn_start = dialog.$wrapper.find(".playpause .btn-start");
	var $btn_complete = dialog.$wrapper.find(".playpause .btn-complete");
	var interval = null;
	var currentIncrement = timestamp;
	var initialized = row ? true : false;
	var clicked = false;
	var flag = true; // Alert only once
	// If row with not completed status, initialize timer with the time elapsed on click of 'Start Timer'.
	if (row) {
		initialized = true;
		$btn_start.hide();
		$btn_complete.show();
		initializeTimer();
	}

	if (!initialized) {
		$btn_complete.hide();
	}

	$btn_start.click(function(e) {
		if (!initialized) {
			// New activity if no activities found
			var data = dialog.get_values();
			if(!data)
                return;
			
            const method = "tzcode.controllers.overrides.issue.issue.create_timelogs";
            const { activity_type, expected_hours, issue } = data;

            frappe.call({ method, args: { activity_type, expected_hours, issue } }).then( response => {
                reset();
                dialog.hide();
                frappe.utils.play_sound("submit");
                frappe.show_alert({ message: __("Time logged successfully"), indicator: "green" });
                cur_frm.refresh();
            });
			
		}

		if (clicked) {
			e.preventDefault();
			return false;
		}

		if (!initialized) {
			initialized = true;
			$btn_start.hide();
			$btn_complete.show();
			initializeTimer();
		}
	});

	// Stop the timer and update the time logged by the timer on click of 'Complete' button
	$btn_complete.click(function() {
        let method = "tzcode.controllers.overrides.issue.issue.complete_timelogs";
        let args = {
            "timesheet": dialog.get_value("timesheet"),
            "log_name": dialog.get_value("log_name"),
        }
		frappe.call({ method, args }).then( response => {
            reset();
		    dialog.hide();
            frappe.utils.play_sound("submit");
            frappe.show_alert({ message: __("Time logged successfully"), indicator: "green" });
            cur_frm.refresh();
        });
	});

	function initializeTimer() {
		interval = setInterval(function() {
			var current = setCurrentIncrement();
			updateStopwatch(current);
		}, 1000);
	}

	function updateStopwatch(increment) {
		var hours = Math.floor(increment / 3600);
		var minutes = Math.floor((increment - (hours * 3600)) / 60);
		var seconds = increment - (hours * 3600) - (minutes * 60);

		// If modal is closed by clicking anywhere outside, reset the timer
		if (!$('.modal-dialog').is(':visible')) {
			reset();
		}
		if(hours > 99999)
			reset();
		if(cur_dialog && cur_dialog.get_value('expected_hours') > 0) {
			if(flag && (currentIncrement >= (cur_dialog.get_value('expected_hours') * 3600))) {
				frappe.utils.play_sound("alert");
				frappe.msgprint(__("Timer exceeded the given hours."));
				flag = false;
			}
		}
		$(".hours").text(hours < 10 ? ("0" + hours.toString()) : hours.toString());
		$(".minutes").text(minutes < 10 ? ("0" + minutes.toString()) : minutes.toString());
		$(".seconds").text(seconds < 10 ? ("0" + seconds.toString()) : seconds.toString());
	}

	function setCurrentIncrement() {
		currentIncrement += 1;
		return currentIncrement;
	}

	function reset() {
		currentIncrement = 0;
		initialized = false;
		clearInterval(interval);
		$(".hours").text("00");
		$(".minutes").text("00");
		$(".seconds").text("00");
		$btn_complete.hide();
		$btn_start.show();
	}
};
