frappe.ui.form.on('Task', {
	before_save:function(frm){
		if(!frm.is_new() && frm.doc.docstatus == 1){
			frappe.call({
	            method: 'contact.events.task.update_progress',
	            args: {
	                'task': frm.doc.name,
	                'custom_total_billable_amount':frm.doc.custom_total_billable_amount
	            },
	            callback: function(r) {
	                frm.refresh_field("custom_tasks");
	            }
	        });
		}
	},
	custom_actual_qty_completed: function(frm) {
		if(frm.doc.custom_actual_qty_completed > frm.doc.custom_total_qty){
			frappe.throw("You can not complete more than actual quantity!")
		}
		else{
			frm.set_value("progress",(frm.doc.custom_actual_qty_completed/frm.doc.custom_total_qty*100))	
		}
	}
});