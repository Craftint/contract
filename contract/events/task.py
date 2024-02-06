import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cstr, flt, nowdate, nowtime, today, comma_or


def validate_qty(doc,method=None):
	if doc.custom_actual_qty_completed > doc.custom_total_qty:
		frappe.throw("You can not complete more than actual quantity!")

def update_progress(doc,method=None):
	task_exists = frappe.db.exists('Task', doc.name)
	if task_exists:
		old_task = frappe.get_doc('Task', doc.name)
		# prev_progress = frappe.get_cached_value("Task", doc.name, "progress")
		if old_task.progress != doc.progress:
			# project = frappe.get_doc('Project',doc.project)
			prev_amnt = round(frappe.utils.flt((old_task.custom_total_billable_amount*old_task.progress))/100,3)
			curr_amnt = round(frappe.utils.flt((doc.custom_total_billable_amount*doc.progress))/100,3)
			# completed = project.custom_completed_value + (curr_amnt - prev_amnt)
			# frappe.db.set_value("Project",project.name,'custom_previous_completed',project.custom_completed_value)
			# frappe.db.set_value("Project",project.name,'custom_completed_value',completed)
			# frappe.db.set_value("Project",project.name,'percent_complete_method',"Manual")
			# frappe.db.set_value("Project",project.name,'percent_complete',(completed / project.total_sales_amount)* 100)

			doc.append('custom_task_history',{
				'date':frappe.utils.nowdate(),
				'previous_per':old_task.progress,
				'current_per':doc.progress,
				'previous_amount': prev_amnt,
				'current_amount': curr_amnt
			})
			project = frappe.db.exists("Project",doc.project)
			if project:
				project = frappe.get_doc("Project",doc.project)
				tasks = frappe.db.get_all("Task Summary",{'parent':project.name,'task':doc.name,'parenttype':"Project"},['name','current_amount'])
				if tasks:
					frappe.db.set_value("Task Summary",tasks[0].name,"previous_amount",tasks[0].current_amount)
					frappe.db.set_value("Task Summary",tasks[0].name,"current_amount",curr_amnt)
					frappe.db.set_value("Task Summary",tasks[0].name,"date",frappe.utils.nowdate())
				else:
				   project.append("custom_tasks",{
					   'task':doc.name,
					   'date':frappe.utils.nowdate(),
					   'previous_amount':0.0,
					   'current_amount':curr_amnt
				   })
				   project.save()