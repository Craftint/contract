// Copyright (c) 2024, Craft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Certificate', {
    refresh:function(frm){
        if(frm.doc.docstatus === 1) {
			frm.add_custom_button('Ledger', ()=> {
				frappe.route_options = {
					"voucher_no": frm.doc.name,
					"from_date": frm.doc.date,
					"to_date": frm.doc.date,
					"company": frm.doc.company,
					"group_by": '',
				};
				frappe.set_route("query-report", "General Ledger");
			}, 'View');
			frm.add_custom_button('Sales Invoice', ()=> {
			    frappe.call(({
                    method:"erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
                    args:{source_name:frm.doc.sales_order},
                    callback:r=>{
                        let doc = r.message
                        doc.items.forEach((item)=>{
                            frm.doc.custom_tasks.forEach((task)=>{
                                if((item.item_code+" "+frm.doc.project)==task.subject){
                                    item.rate = task.current_amount - task.pc_rasied
                                }
                            })
                        })
                        doc.custom_payment_certificate = frm.doc.name
                        frappe.model.sync(doc)
                        frappe.set_route("Form", doc.doctype, doc.name);
                    }
                }))
			}, 'Create');
		}
    },
	// onload:function(frm) {
	//     frm.ignore_doctypes_on_cancel_all = ["GL Entry", "Payment Ledger Entry"]
	// 	if(frm.is_new() && frm.doc.project){
	// 	    frappe.db.get_doc("Project",frm.doc.project).then(doc => {
	// 	        frm.set_value("company",doc.company)
	// 	        frm.set_value("sales_order",doc.sales_order)
	// 	        frm.set_value("start_date",doc.actual_start_date)
	// 	        frm.set_value("contract_value",doc.total_sales_amount)
	// 	        frm.set_value("approved_variation",0.0)
	// 	        frm.set_value("total_approved_value",doc.total_sales_amount)
	// 	        frm.set_value("unapproved_variation",0.0)
	// 	        frm.set_value("total_value",doc.total_sales_amount)
	// 	        frm.set_value("work_done_to_date",doc.custom_completed_value)
	// 	        frm.set_value("work_done_previous",doc.custom_pc_raised)
	// 	        frm.set_value("work_done_this_payment",doc.custom_completed_value - doc.custom_pc_raised)
	// 	        frm.set_value("custom_tasks",doc.custom_tasks)
	// 	    })
	// 	    frm.doc.custom_tasks.forEach((row) =>{
	// 	        row.current_amount = row.current_amount - row.pc_raised
	// 	    })
	// 	}
	// },
	on_cancel:function(frm) {
	    frappe.call(({
            method:"erpnext.accounts.general_ledger.make_reverse_gl_entries",
            args:{
                voucher_type:frm.doc.doctype,
                voucher_no: frm.doc.name
            },
            callback:r=>{
            }
        }))
	}
})
