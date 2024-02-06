import frappe
from frappe.model.document import Document
import copy


def make_gl_entries(doc,method):
	if doc.custom_payment_application:
		pa = frappe.get_doc("Payment Application",doc.custom_payment_application)
		if pa.is_advance:
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
			# gl2 = frappe.new_doc("GL Entry")
			# gl2.posting_date = doc.posting_date
			# gl2.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_receivable_account")
			# gl2.credit = doc.grand_total
			# gl2.credit_in_account_currency = doc.grand_total
			# gl2.against = doc.customer
			# gl2.voucher_type = 'Sales Invoice'
			# gl2.voucher_no = doc.name
			# gl2.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
			# gl2.company = doc.company
			# gl2.flags.ignore_permissions = 1
			# gl2.project = doc.project
			# gl2.party_type = "Customer"
			# gl2.party = doc.customer
			# gl2.save()
			# gl2.submit()
			
			# gl1 = frappe.new_doc("GL Entry")
			# gl1.posting_date = doc.posting_date
			# gl1.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_advance_account")
			# gl1.debit = doc.net_total
			# gl1.debit_in_account_currency = doc.net_total
			# gl1.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_receivable_account")
			# gl1.voucher_type = 'Sales Invoice'
			# gl1.voucher_no = doc.name
			# gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
			# gl1.company = doc.company
			# gl1.flags.ignore_permissions = 1
			# gl1.project = doc.project
			# gl1.save()
			# gl1.submit()

			# gl1 = frappe.new_doc("GL Entry")
			# gl1.posting_date = doc.posting_date
			# gl1.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_tax_account")
			# gl1.debit = doc.total_taxes_and_charges
			# gl1.debit_in_account_currency = doc.total_taxes_and_charges
			# gl1.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_receivable_account")
			# gl1.voucher_type = 'Sales Invoice'
			# gl1.voucher_no = doc.name
			# gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
			# gl1.company = doc.company
			# gl1.flags.ignore_permissions = 1
			# gl1.project = doc.project
			# gl1.save()
			# gl1.submit()
		else:

			gl1 = frappe.new_doc("GL Entry")
			gl1.posting_date = doc.posting_date
			gl1.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_income_account")
			gl1.debit = doc.net_total
			gl1.debit_in_account_currency = doc.net_total
			gl1.against = doc.customer
			gl1.voucher_type = 'Sales Invoice'
			gl1.voucher_no = doc.name
			gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
			gl1.company = doc.company
			gl1.flags.ignore_permissions = 1
			gl1.project = doc.project
			gl1.save()
			gl1.submit()	

			# Tax
			gl1 = frappe.new_doc("GL Entry")
			gl1.posting_date = doc.posting_date
			gl1.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_tax_account")
			gl1.debit = doc.total_taxes_and_charges
			gl1.debit_in_account_currency = doc.total_taxes_and_charges
			gl1.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_receivable_account")
			gl1.voucher_type = 'Sales Invoice'
			gl1.voucher_no = doc.name
			gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
			gl1.company = doc.company
			gl1.flags.ignore_permissions = 1
			gl1.project = doc.project
			gl1.save()
			gl1.submit()

			debtor = doc.grand_total
			proj = frappe.get_doc("Project",doc.project)

			# Retention
			retention = (doc.grand_total*proj.custom_retention_per)/100
			gl2 = frappe.new_doc("GL Entry")
			gl2.posting_date = doc.posting_date
			gl2.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_retention_account")
			gl2.credit = retention
			gl2.credit_in_account_currency = retention
			gl2.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_income_account")
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

			# Advance
			adv = (proj.custom_advance_value*proj.custom_advance_per)/100
			if proj.custom_advance_remaining >= adv:
				gl2 = frappe.new_doc("GL Entry")
				gl2.posting_date = doc.posting_date
				gl2.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_advance_account")
				gl2.credit = adv
				gl2.credit_in_account_currency = doc.grand_total
				gl2.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_income_account")
				gl2.voucher_type = 'Sales Invoice'
				gl2.voucher_no = doc.name
				gl2.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
				gl2.company = doc.company
				gl2.flags.ignore_permissions = 1
				gl2.project = doc.project
				gl2.save()
				gl2.submit()

				# frappe.db.set_value("Project",doc.project,"custom_advance_remaining",proj.custom_advance_remaining+adv)
				debtor = doc.grand_total - adv

			gl2 = frappe.new_doc("GL Entry")
			gl2.posting_date = doc.posting_date
			gl2.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_receivable_account")
			gl2.credit = debtor - retention
			gl2.credit_in_account_currency = debtor - retention
			gl2.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_income_account")
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

def update_project(doc,method):
	if doc.custom_payment_application:
		pa = frappe.get_doc("Payment Application",doc.custom_payment_application)
		if not pa.is_advance:
			proj = frappe.get_doc("Project",doc.project)
			adv = (proj.custom_advance_value*proj.custom_advance_per)/100
			frappe.db.set_value("Project",doc.project,"custom_advance_remaining",proj.custom_advance_remaining-adv)