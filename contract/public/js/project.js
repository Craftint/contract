frappe.ui.form.on('Project', {
	refresh(frm) {
		if(frm.doc.is_active && frm.doc.percent_complete <100 && !frm.is_new() && frm.doc.status != "Completed"){
			frm.add_custom_button(__('Advance Payment Application'), () => {
	            frappe.model.open_mapped_doc({
	              method: "contract.events.project.create_advance_pa",
	              frm: frm
	            })
	          }, __('Create'));
			frm.add_custom_button(__('Payment Application'), () => {
	            frappe.model.open_mapped_doc({
	              method: "contract.events.project.create_pa",
	              frm: frm
	            })
	          }, __('Create'));
		}
	},
	onload(frm){
	    if(frm.doc.total_sales_amount && frm.doc.custom_order_value != frm.doc.total_sales_amount){
	        frm.set_value("custom_order_value",frm.doc.total_sales_amount)
	    }
	    frm.refresh_field("custom_tasks")
	},
	custom_advance_per(frm){
	    frm.set_value("custom_advance_value",(frm.doc.custom_advance_per*frm.doc.custom_order_value)/100)
	}
})