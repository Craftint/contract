import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cstr, flt, nowdate, nowtime, today, comma_or
from contract.events.project import calculate_this


def validate_qty(doc,method=None):
	if doc.custom_actual_qty_completed > doc.custom_total_qty:
		frappe.throw("You can not complete more than actual quantity!")

def update_progress(doc,method=None):
	task_exists = frappe.db.exists('Task', doc.name)
	if task_exists:
		old_task = frappe.get_doc('Task', doc.name)
		if old_task.progress != doc.progress:
			prev_amnt = round(frappe.utils.flt((old_task.custom_total_billable_amount*old_task.progress))/100,3)
			curr_amnt = round(frappe.utils.flt((doc.custom_total_billable_amount*doc.progress))/100,3)
			doc.append('custom_task_history',{
				'date':frappe.utils.nowdate(),
				'previous_per':old_task.progress,
				'current_per':doc.progress,
				'this_per':doc.progress - old_task.progress,
				'prev_qty':old_task.custom_actual_qty_completed,
				'current_qty':doc.custom_actual_qty_completed,
				'this_qty':doc.custom_actual_qty_completed - old_task.custom_actual_qty_completed,
				'previous_amount': prev_amnt,
				'current_amount': curr_amnt,
				'this_amount': curr_amnt - prev_amnt
			})
			project = frappe.db.exists("Project",doc.project)
			if project:
				project = frappe.get_doc("Project",doc.project)
				tasks = frappe.db.get_all("Task Summary",{'parent':project.name,'task':doc.name,'parenttype':"Project"},['name','pc_raised','pc_this'])
				if tasks:
					# frappe.db.set_value("Task Summary",tasks[0].name,"previous_amount",tasks[0].current_amount)
					# frappe.db.set_value("Task Summary",tasks[0].name,"current_amount",curr_amnt)
					frappe.db.set_value("Task Summary",tasks[0].name,"pc_current",curr_amnt)
					frappe.db.set_value("Task Summary",tasks[0].name,"date",frappe.utils.nowdate())
					frappe.db.set_value("Task Summary",tasks[0].name,"qty",doc.custom_actual_qty_completed)
					frappe.db.set_value("Task Summary",tasks[0].name,"pc_this",curr_amnt - tasks[0].pc_raised)
					# completed = project.custom_completed_value + curr_amnt
					# frappe.db.set_value("Project",doc.project,"custom_completed_value",completed)
					# calculate_this(project)
					frappe.db.set_value("Project",doc.project,"custom_this_payment",((curr_amnt - tasks[0].pc_raised)-tasks[0].pc_this) + project.custom_this_payment)