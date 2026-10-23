frappe.listview_settings["Upwork Job Posting"] = {
	get_indicator(doc) {
		const colors = {
			New: "blue",
			Reviewed: "orange",
			"Proposal Drafted": "purple",
			Applied: "green",
			Skipped: "gray",
		};
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
