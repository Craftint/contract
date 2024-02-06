// Copyright (c) 2024, Craft and contributors
// For license information, please see license.txt

{% include 'erpnext/selling/sales_common.js' %};
frappe.provide("contract.contract");

frappe.ui.form.on('Payment Application', {
	onload: function (frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Sales Invoice'), () => frm.events.make_sales_invoice(frm), __('Create'));
		}
	},

	make_sales_invoice: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
			frm: frm
		});
	},
	refresh:function (frm) {
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

		frm.add_custom_button(__('Sales Invoice'), () => {
            frappe.model.open_mapped_doc({
              method: "contract.contract.doctype.payment_application.payment_application.create_invoice",
              frm: frm
            })
          }, __('Create'));
	}
});

frappe.ui.form.on('Payment Application Item',{
	setup:function(frm){
		frm.add_fetch("item_code", "item_name", "item_name")
		frm.add_fetch("item_code", "description", "description")
		frm.add_fetch("item_code", "item_group", "item_group")
		frm.add_fetch("item_code", "brand", "brand")
	}
})



contract.contract.PAController = class PAController extends erpnext.selling.SellingController {
	company() {
		erpnext.accounts.dimensions.update_dimension(this.frm, this.frm.doctype);

		let me = this;
		if (this.frm.doc.company) {
			frappe.call({
				method:
					"erpnext.accounts.party.get_party_account",
				args: {
					party_type: 'Customer',
					party: this.frm.doc.customer,
					company: this.frm.doc.company
				},
				callback: (response) => {
					if (response) me.frm.set_value("debit_to", response.message);
				},
			});
		}
	}
	onload() {
		var me = this;
		super.onload();

		this.frm.ignore_doctypes_on_cancel_all = ['POS Invoice', 'Timesheet', 'POS Invoice Merge Log',
							  'POS Closing Entry', 'Journal Entry', 'Payment Entry', "Repost Payment Ledger", "Repost Accounting Ledger", "Unreconcile Payment", "Unreconcile Payment Entries"];

		erpnext.queries.setup_queries(this.frm, "Warehouse", function() {
			return erpnext.queries.warehouse(me.frm.doc);
		});

		erpnext.queries.setup_warehouse_query(this.frm);
	}

	refresh(doc, dt, dn) {
		this.show_general_ledger();
	}

	tc_name() {
		this.get_terms();
	}
	customer() {
		var me = this;
		if(this.frm.updating_party_details) return;

		if (this.frm.doc.__onload && this.frm.doc.__onload.load_after_mapping) return;

		erpnext.utils.get_party_details(this.frm,
			"erpnext.accounts.party.get_party_details", {
				posting_date: this.frm.doc.posting_date,
				party: this.frm.doc.customer,
				party_type: "Customer",
				account: this.frm.doc.debit_to,
				price_list: this.frm.doc.selling_price_list
			}, function() {
				me.apply_pricing_rule();
			});
	}

	debit_to() {
		var me = this;
		if(this.frm.doc.debit_to) {
			me.frm.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Account",
					fieldname: "account_currency",
					filters: { name: me.frm.doc.debit_to },
				},
				callback: function(r, rt) {
					if(r.message) {
						me.frm.set_value("party_account_currency", r.message.account_currency);
						me.set_dynamic_labels();
					}
				}
			});
		}
	}
}

extend_cscript(cur_frm.cscript, new contract.contract.PAController({frm: cur_frm}));

cur_frm.fields_dict["items"].grid.get_field("cost_center").get_query = function(doc) {
	return {
		filters: {
			'company': doc.company,
			"is_group": 0
		}
	}
}

cur_frm.cscript.income_account = function(doc, cdt, cdn) {
	erpnext.utils.copy_value_in_all_rows(doc, cdt, cdn, "items", "income_account");
}

cur_frm.cscript.expense_account = function(doc, cdt, cdn) {
	erpnext.utils.copy_value_in_all_rows(doc, cdt, cdn, "items", "expense_account");
}

cur_frm.cscript.cost_center = function(doc, cdt, cdn) {
	erpnext.utils.copy_value_in_all_rows(doc, cdt, cdn, "items", "cost_center");
}

cur_frm.set_query("debit_to", function(doc) {
	return {
		filters: {
			'account_type': 'Receivable',
			'is_group': 0,
			'company': doc.company
		}
	}
});
