frappe.ui.form.on('Sales Invoice', {
	onload: function (frm) {
		if (frm.is_new() && frm.doc.custom_payment_application) {
			// $.each(frm.doc.items, function(i, d) {
			// 	frappe.db.get_value("Payment Application Item", d.custom_pa_item, "rate", function(r){     
   //               	frappe.model.set_value(d.doctype,d.name,"rate",r.rate)
   //            	})
			// });
		}
	},
});