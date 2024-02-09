
// render
frappe.listview_settings['Payment Application'] = {
	get_indicator: function(doc) {
		const status_colors = {
			"Draft": "grey",
			"Invoiced": "green",
			"To Invoice": "orange"
		};
		return [__(doc.status), status_colors[doc.status], "status,=,"+doc.status];
	}
};
