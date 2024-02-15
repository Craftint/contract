# Copyright (c) 2024, Craft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt
from frappe.model.mapper import get_mapped_doc,map_child_doc
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.controllers.accounts_controller import get_taxes_and_charges



class PaymentApplication(Document):
	def validate(self):
		self.set_status()
		self.update_details()

	def before_insert(self):
		proj = frappe.get_doc("Project",self.project)
		if not self.is_advance:
			if self.grand_total > 0:
				retention = (self.grand_total*proj.custom_retention_per)/100
				self.ret_this_payment = retention
				self.ret_to_date = self.ret_this_payment + self.ret_previous

				adv = (self.grand_total*proj.custom_advance_per)/100
				self.adv_this_payment = adv
				self.adv_to_date = self.adv_this_payment + self.adv_previous
				self.work_done_this_payment = self.net_total
				self.work_done_to_date = self.net_total + self.work_done_previous

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
				pc_raised = frappe.get_cached_value("Task Summary", row.task_summary, "pc_raised") or 0
				pc_current = frappe.get_cached_value("Task Summary", row.task_summary, "pc_current") or 0
				frappe.db.set_value("Task Summary", row.task_summary, "pc_raised", pc_raised+row.amount)
				# frappe.db.set_value("Task Summary", row.task_summary, "pc_current", flt(pc_raised) + row.amount)
				frappe.db.set_value("Task Summary", row.task_summary, "pc_this", pc_current - (pc_raised+row.amount))

			completed = frappe.db.get_value("Project",self.project,"custom_completed_value")
			frappe.db.set_value("Project",self.project,"custom_previous_completed",completed)
			frappe.db.set_value("Project",self.project,"custom_completed_value",completed+ self.net_total)
			# frappe.db.set_value("Project",self.project,"custom_this_payment",self.net_total - completed)
			self.calculate_this()


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
				# self.ret_this_payment = retention
				# self.ret_to_date = self.ret_this_payment + self.ret_previous
				prev_ret = frappe.db.get_value("Project",self.project,"custom_total_retention")
				frappe.db.set_value("Project",self.project,"custom_total_retention",prev_ret+retention)

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
				adv = (self.grand_total*proj.custom_advance_per)/100
				# if proj.custom_advance_remaining <= adv:
					# self.advance = adv
				prev_adv = frappe.db.get_value("Project",self.project,"custom_total_advance_deducted")
				frappe.db.set_value("Project",self.project,"custom_total_advance_deducted",prev_adv+adv)
				# self.adv_this_payment = adv
				# self.adv_to_date = self.adv_this_payment + self.adv_previous

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

				frappe.db.set_value("Project",self.project,"custom_advance_remaining",proj.custom_advance_remaining-adv)
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
		if not self.is_advance:
			proj = frappe.get_doc("Project",self.project)
			adv = (proj.custom_advance_value*proj.custom_advance_per)/100
			frappe.db.set_value("Project",self.project,"custom_advance_remaining",proj.custom_advance_remaining+adv)
			for row in self.items:
				pc_raised = frappe.get_cached_value("Task Summary", row.task_summary, "pc_raised") or 0
				pc_current = frappe.get_cached_value("Task Summary", row.task_summary, "pc_current") or 0
				frappe.db.set_value("Task Summary", row.task_summary, "pc_raised", pc_raised-row.amount)
				frappe.db.set_value("Task Summary", row.task_summary, "pc_this", pc_current + (pc_raised-row.amount))

			completed = frappe.db.get_value("Project",self.project,"custom_completed_value")
			frappe.db.set_value("Project",self.project,"custom_completed_value",completed - self.net_total)
			self.calculate_this()

	def set_status(self):
		if self.is_new():
			if self.get("amended_from"):
				self.status = "Draft"
			return

		if self.docstatus == 2:
			status = "Cancelled"
		elif self.docstatus == 1:
			invoices = frappe.db.count("Sales Invoice",{'docstatus':1,'custom_payment_application':self.name})
			if invoices > 0:
				self.status = "Invoiced"
			else:
				self.status = "To Invoice"

	def calculate_this(self):
		proj = frappe.get_doc("Project",self.project)
		this = 0
		if proj.custom_tasks:
			for row in proj.custom_tasks:
				this += row.pc_this
		frappe.db.set_value("Project",self.project,'custom_this_payment',this)

	def update_details(self):
		self.total_due_to_date = self.work_done_to_date + self.material_to_date
		self.total_due_previous = self.work_done_previous + self.material_previous
		self.total_due_this_payment = self.work_done_this_payment + flt(self.material_this_payment)

		self.td_this_date = self.adv_to_date + self.ret_to_date + self.rm_to_date + self.od_to_date
		self.td_previous = self.adv_previous + self.ret_previous + self.rm_previous +self.od_previous
		self.td_this_payment = self.adv_this_payment + self.ret_this_payment + self.rm_this_payment + self.od_this_payment

		self.np_to_date = self.total_due_to_date - self.td_this_date
		self.np_previous = self.total_due_previous - self.td_previous
		self.np_this_payment = self.total_due_this_payment - self.td_this_payment

@frappe.whitelist()
def create_invoice(source_name, target_doc=None, args=None):
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
		taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=source.company)
		if taxes:
			target.set("taxes",[])
			target.taxes_and_charges = taxes.get('taxes_and_charges')
			for tax in taxes.get('taxes'):
				target.append("taxes", tax)

	# def update_details(source_doc, target_doc, source_parent):
	# 	from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
	# 	taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=source_doc.company)
	# 	if taxes:
	# 		target_doc.taxes_and_charges = taxes.get('taxes_and_charges')
	# 		for tax in taxes.get('taxes'):
	# 			target_doc.append("taxes", tax)

	def update_item(source_doc, target_doc, source_parent):
		if source_parent.is_advance:
			target_doc.income_account = frappe.db.get_value("Company", source_parent.company, "custom_default_advance_account")
		else:
			target_doc.income_account = frappe.db.get_value("Company", source_parent.company, "default_income_account")

		item_price = frappe.get_all("Item Price",filters={"item_code": source_doc.item_code, "price_list": "Standard Selling"})
		if item_price:
			frappe.db.set_value("Item Price", item_price[0], "price_list_rate", source_doc.rate)


	target_doc = get_mapped_doc(
		"Payment Application",
		source_name,
		{
			"Payment Application": {
				"doctype":"Sales Invoice",
				"field_no_map":["taxes_and_charges","sales_order"],
				"field_map": {
					"name": "custom_payment_application"
				},
				# "postprocess": update_details
			},
			"Payment Application Item": {
				"doctype": "Sales Invoice Item",
				"field_map": {
					"name":"custom_pa_item",
				},
				"field_no_map":["parent","sales_order"],
				"postprocess": update_item,
			}
		},
		target_doc, set_missing_values
	)
	return target_doc