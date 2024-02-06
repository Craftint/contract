# Copyright (c) 2024, Craft and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PaymentCertificate(Document):
	def on_submit(self):
		proj = frappe.get_doc("Project",doc.project)
		frappe.db.set_value("Project",doc.project,"custom_pc_raised",doc.work_done_this_payment)
		# frappe.db.set_value("Project",doc.project,"custom_completed_value",doc.work_done_to_date)

		if doc.custom_tasks:
		    for row in doc.custom_tasks:
		        task = row.task
		        for rec in proj.custom_tasks:
		            if rec.task == task:
		                frappe.db.set_value("Task Summary",rec.name,'pc_raised',row.current_amount)

		if doc.work_done_this_payment > 0:
		    gl1 = frappe.new_doc("GL Entry")
		    gl1.posting_date = doc.date
		    gl1.account = frappe.db.get_value("Company", doc.company, "default_receivable_account")
		    gl1.credit = doc.work_done_this_payment
		    gl1.credit_in_account_currency = doc.work_done_this_payment
		    gl1.against = frappe.db.get_value("Company", doc.company, "custom_default_provisional_income_account")
		    gl1.voucher_type = 'Payment Certificate'
		    gl1.voucher_no = doc.name
		    gl1.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
		    gl1.company = doc.company
		    gl1.flags.ignore_permissions = 1
		    gl1.project = doc.project
		    gl1.party_type = "Customer"
		    gl1.party = proj.customer
		    gl1.save()
		    gl1.submit()
		    
		    gl2 = frappe.new_doc("GL Entry")
		    gl2.posting_date = doc.date
		    gl2.account = frappe.db.get_value("Company", doc.company, "custom_default_provisional_income_account")
		    gl2.debit = doc.work_done_this_payment
		    gl2.debit_in_account_currency = doc.work_done_this_payment
		    gl2.against = proj.customer
		    gl2.voucher_type = 'Payment Certificate'
		    gl2.voucher_no = doc.name
		    gl2.cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
		    gl2.company = doc.company
		    gl2.flags.ignore_permissions = 1
		    gl2.project = doc.project
		    gl2.save()
		    gl2.submit()
