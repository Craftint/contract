# Copyright (c) 2024, Craft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.general_ledger import make_reverse_gl_entries


class PaymentApplication(Document):
	def on_submit(self):
		proj = frappe.get_doc("Project",self.project)
		if self.is_advance:
			if self.grand_total > 0:
				gl2 = frappe.new_doc("GL Entry")
				gl2.posting_date = self.posting_date
				gl2.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_receivable_account")
				gl2.debit = self.grand_total
				gl2.debit_in_account_currency = self.grand_total
				gl2.against = proj.customer
				gl2.voucher_type = 'Payment Application'
				gl2.voucher_no = self.name
				gl2.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl2.company = self.company
				gl2.flags.ignore_permissions = 1
				gl2.project = self.project
				gl2.party_type = "Customer"
				gl2.party = proj.customer
				gl2.save()
				gl2.submit()
				
				gl1 = frappe.new_doc("GL Entry")
				gl1.posting_date = self.posting_date
				gl1.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_advance_account")
				gl1.credit = self.net_total
				gl1.credit_in_account_currency = self.net_total
				gl1.against = frappe.db.get_value("Company", self.company, "custom_default_provisional_receivable_account")
				gl1.voucher_type = 'Payment Application'
				gl1.voucher_no = self.name
				gl1.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl1.company = self.company
				gl1.flags.ignore_permissions = 1
				gl1.project = self.project
				gl1.save()
				gl1.submit()

				gl1 = frappe.new_doc("GL Entry")
				gl1.posting_date = self.posting_date
				gl1.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_tax_account")
				gl1.credit = self.total_taxes_and_charges
				gl1.credit_in_account_currency = self.total_taxes_and_charges
				gl1.against = frappe.db.get_value("Company", self.company, "custom_default_provisional_receivable_account")
				gl1.voucher_type = 'Payment Application'
				gl1.voucher_no = self.name
				gl1.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl1.company = self.company
				gl1.flags.ignore_permissions = 1
				gl1.project = self.project
				gl1.save()
				gl1.submit()
				
		else:
			for row in self.items:
				pc_raised = frappe.get_cached_value("Task Summary", row.task_summary, "pc_current") or 0
				frappe.db.set_value("Task Summary", row.task_summary, "pc_raised", flt(pc_raised))
				frappe.db.set_value("Task Summary", row.task_summary, "pc_current", flt(pc_raised) + row.amount)

			
			frappe.db.set_value("Project",self.project,"custom_previous_completed",proj.custom_completed_value)
			frappe.db.set_value("Project",self.project,"custom_completed_value",proj.custom_completed_value + self.net_total)


			if self.grand_total > 0:
				gl1 = frappe.new_doc("GL Entry")
				gl1.posting_date = self.posting_date
				gl1.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_income_account")
				gl1.credit = self.net_total
				gl1.credit_in_account_currency = self.net_total
				gl1.against = self.customer
				gl1.voucher_type = 'Payment Application'
				gl1.voucher_no = self.name
				gl1.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl1.company = self.company
				gl1.flags.ignore_permissions = 1
				gl1.project = self.project
				gl1.save()
				gl1.submit()

				# Tax
				gl1 = frappe.new_doc("GL Entry")
				gl1.posting_date = self.posting_date
				gl1.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_tax_account")
				gl1.credit = self.total_taxes_and_charges
				gl1.credit_in_account_currency = self.total_taxes_and_charges
				gl1.against = frappe.db.get_value("Company", self.company, "custom_default_provisional_receivable_account")
				gl1.voucher_type = 'Payment Application'
				gl1.voucher_no = self.name
				gl1.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl1.company = self.company
				gl1.flags.ignore_permissions = 1
				gl1.project = self.project
				gl1.save()
				gl1.submit()

				debtor = self.grand_total

				# Retention
				retention = (self.grand_total*proj.custom_retention_per)/100
				gl2 = frappe.new_doc("GL Entry")
				gl2.posting_date = self.posting_date
				gl2.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_retention_account")
				gl2.debit = retention
				gl2.debit_in_account_currency = retention
				gl2.against = frappe.db.get_value("Company", self.company, "custom_default_provisional_income_account")
				gl2.voucher_type = 'Payment Application'
				gl2.voucher_no = self.name
				gl2.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl2.company = self.company
				gl2.flags.ignore_permissions = 1
				gl2.project = self.project
				gl2.party_type = "Customer"
				gl2.party = proj.customer
				gl2.save()
				gl2.submit()

				# Advance
				adv = (proj.custom_advance_value*proj.custom_advance_per)/100
				if proj.custom_advance_remaining >= adv:
					gl2 = frappe.new_doc("GL Entry")
					gl2.posting_date = self.posting_date
					gl2.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_advance_account")
					gl2.debit = adv
					gl2.debit_in_account_currency = self.grand_total
					gl2.against = frappe.db.get_value("Company", self.company, "custom_default_provisional_income_account")
					gl2.voucher_type = 'Payment Application'
					gl2.voucher_no = self.name
					gl2.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
					gl2.company = self.company
					gl2.flags.ignore_permissions = 1
					gl2.project = self.project
					gl2.save()
					gl2.submit()

					frappe.db.set_value("Project",self.project,"custom_advance_remaining",proj.custom_advance_remaining+adv)
					debtor = self.grand_total - adv

				gl2 = frappe.new_doc("GL Entry")
				gl2.posting_date = self.posting_date
				gl2.account = frappe.db.get_value("Company", self.company, "custom_default_provisional_receivable_account")
				gl2.debit = debtor - retention
				gl2.debit_in_account_currency = debtor - retention
				gl2.against = frappe.db.get_value("Company", self.company, "custom_default_provisional_income_account")
				gl2.voucher_type = 'Payment Application'
				gl2.voucher_no = self.name
				gl2.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
				gl2.company = self.company
				gl2.flags.ignore_permissions = 1
				gl2.project = self.project
				gl2.party_type = "Customer"
				gl2.party = proj.customer
				gl2.save()
				gl2.submit()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)


@frappe.whitelist()
def create_invoice(source_name, target_doc=None, args=None):
	def update_details(source_doc, target_doc, source_parent):
		target_doc.total = source_doc.custom_previous_completed - source_doc.custom_completed_value

	def update_item(source_doc, target_doc, source_parent):
		if source_parent.is_advance:
			target_doc.income_account = frappe.db.get_value("Company", source_parent.company, "custom_default_advance_account")
		else:
			target_doc.income_account = frappe.db.get_value("Company", source_parent.company, "default_income_account")

	target_doc = get_mapped_doc(
		"Payment Application",
		source_name,
		{
			"Payment Application": {
				"doctype":"Sales Invoice",
				"field_map": {
					"name": "custom_payment_application"
				},
				# "postprocess": update_details
			},
			"Payment Application Item": {
				"doctype": "Sales Invoice Item",
				# "field_map": {
				#     "name":"task_summary",
				#     "item": "item_code",
				#     "sales_order_item":"so_detail",
				#     "pc_this":"amount"
				# },
				"postprocess": update_item,
				# "condition": lambda doc: abs(doc.pc_this) > 0
			}
		},
		target_doc,
	)
	return target_doc