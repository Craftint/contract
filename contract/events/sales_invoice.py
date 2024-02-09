import frappe
from frappe.model.document import Document
import copy


def make_gl_entries(doc,method):
	if doc.custom_payment_application:
		pa = frappe.get_doc("Payment Application",doc.custom_payment_application)
		pa.db_set("status","Invoiced")
		gl_entry = frappe.qb.DocType("GL Entry")
		gl_entries = (
			frappe.qb.from_(gl_entry)
			.select("*")
			.where(gl_entry.voucher_type == 'Payment Application')
			.where(gl_entry.voucher_no == doc.custom_payment_application)
			.where(gl_entry.is_cancelled == 0)
			.for_update()
		).run(as_dict=1)

		for entry in gl_entries:
			new_gle = copy.deepcopy(entry)
			new_gle["name"] = None
			if not pa.is_advance:
				adv = ret = 0
				if new_gle.get("account") == frappe.db.get_value("Company", doc.company, "custom_default_provisional_advance_account"):
					gl1 = frappe.new_doc("GL Entry")
					gl1.posting_date = doc.posting_date
					gl1.account = frappe.db.get_value("Company", doc.company, "custom_default_advance_account")
					gl1.debit = new_gle.get("debit", 0)
					gl1.debit_in_account_currency = new_gle.get("debit", 0)
					gl1.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_advance_account")
					gl1.voucher_type = 'Sales Invoice'
					gl1.voucher_no = doc.name
					gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
					gl1.company = doc.company
					gl1.flags.ignore_permissions = 1
					gl1.project = doc.project
					gl1.save()
					gl1.submit()
					adv = new_gle.get("debit", 0)

				if new_gle.get("account") == frappe.db.get_value("Company", doc.company, "custom_default_provisional_retention_account"):
					gl1 = frappe.new_doc("GL Entry")
					gl1.posting_date = doc.posting_date
					gl1.account = frappe.db.get_value("Company", doc.company, "custom_default_retention_account")
					gl1.debit = new_gle.get("debit", 0)
					gl1.debit_in_account_currency = new_gle.get("debit", 0)
					gl1.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_retention_account")
					gl1.voucher_type = 'Sales Invoice'
					gl1.voucher_no = doc.name
					gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
					gl1.company = doc.company
					gl1.flags.ignore_permissions = 1
					gl1.project = doc.project
					gl1.party_type = "Customer"
					gl1.party = doc.customer
					gl1.save()
					gl1.submit()
					ret = new_gle.get("debit", 0)

				if adv+ret > 0:
					gl2 = frappe.new_doc("GL Entry")
					gl2.posting_date = doc.posting_date
					gl2.account = frappe.db.get_value("Company", doc.company, "default_receivable_account")
					gl2.credit = adv + ret
					gl2.credit_in_account_currency = adv + ret
					gl2.against = frappe.db.get_value("Company", doc.company, "default_income_account")
					gl2.voucher_type = 'Sales Invoice'
					gl2.voucher_no = doc.name
					gl2.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
					gl2.company = doc.company
					gl2.flags.ignore_permissions = 1
					gl2.project = doc.project
					gl2.party_type = "Customer"
					gl2.party = doc.customer
					gl2.save()
					gl2.submit()

			debit = new_gle.get("credit", 0)
			credit = new_gle.get("debit", 0)

			debit_in_account_currency = new_gle.get("credit_in_account_currency", 0)
			credit_in_account_currency = new_gle.get("debit_in_account_currency", 0)

			new_gle["debit"] = debit
			new_gle["credit"] = credit
			new_gle["debit_in_account_currency"] = debit_in_account_currency
			new_gle["credit_in_account_currency"] = credit_in_account_currency

			new_gle["remarks"] = "Reversing the provisional entries for " + doc.custom_payment_application
			new_gle["is_cancelled"] = 0
			new_gle["voucher_type"] = "Sales Invoice"
			new_gle["voucher_no"] = doc.name

			if new_gle["debit"] or new_gle["credit"]:
				gle = frappe.new_doc("GL Entry")
				gle.update(new_gle)
				gle.flags.ignore_permissions = 1
				gle.flags.update_outstanding = "Yes"
				gle.flags.notify_update = False
				gle.save()
				gle.submit()
			
