frappe.listview_settings["Lead"] = {
	get_indicator: function (doc) {
		const colors = {
			"Lead":           "blue",
			"Open":           "orange",
			"Replied":        "yellow",
			"Opportunity":    "cyan",
			"Quotation":      "purple",
			"Interested":     "light-blue",
			"Converted":      "green",
			"Lost Quotation": "red",
			"Do Not Contact": "darkgrey",
		};
		const color = colors[doc.status] || "gray";
		return [__(doc.status), color, "status,=," + doc.status];
	},
};
