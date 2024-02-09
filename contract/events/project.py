import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cstr, flt, nowdate, nowtime, today, comma_or
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.accounts_controller import get_taxes_and_charges

@frappe.whitelist()
def create_advance_pa(source_name, target_doc=None, args=None):
    def update_details(source_doc, target_doc, source_parent):
        target_doc.is_advance = 1
        target_doc.cost_center = source_doc.cost_center or frappe.db.get_value("Company", source_doc.company, "cost_center")
        taxes_and_charges = frappe.db.get_value("Company", source_doc.company, "custom_default_provisional_taxes_template")
        target_doc.taxes_and_charges = taxes_and_charges
        if not target_doc.get("taxes"):
            taxes = get_taxes_and_charges("Sales Taxes and Charges Template", taxes_and_charges)
            for tax in taxes:
                target_doc.append("taxes", tax)

        item = frappe.get_doc("Item",{'item_code':'Contract Advance'})
        target_doc.append('items',{
                'item_code':item.item_code,
                'item_name':item.item_name,
                'description':item.description,
                'uom': item.stock_uom,
                'qty': 1,
                'rate':flt(source_doc.custom_advance_value),
                'cost_center':source_doc.cost_center or frappe.db.get_value("Company", source_doc.company, "cost_center"),
                'income_account':frappe.db.get_value("Company", source_doc.company, "custom_default_provisional_advance_account")
            })

    target_doc = get_mapped_doc(
        "Project",
        source_name,
        {
            "Project": {
                "doctype":"Payment Application",
                "field_map": {
                    "name": "project"
                },
                "postprocess": update_details,
                "condition":lambda doc: doc.custom_advance_value > 0
            }
        },
        target_doc,
    )
    return target_doc


@frappe.whitelist()
def create_pa(source_name, target_doc=None, args=None):
    def update_details(source_doc, target_doc, source_parent):
        from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
        # target_doc.total = source_doc.custom_previous_completed - source_doc.custom_completed_value
        target_doc.cost_center = frappe.db.get_value("Company", source_doc.company, "cost_center")
        taxes_and_charges = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=source_doc.company)
        if taxes_and_charges.get('taxes'):
            target_doc.update(taxes_and_charges)


    def update_item(source_doc, target_doc, source_parent):
        item = frappe.get_doc("Sales Order Item",source_doc.sales_order_item)
        target_doc.item_name = item.item_name
        target_doc.description = item.description
        target_doc.uom = item.uom
        target_doc.rate = flt(source_doc.pc_this) / flt(source_doc.qty)
        target_doc.income_account = frappe.db.get_value("Company", source_parent.company, "custom_default_provisional_income_account")

    target_doc = get_mapped_doc(
        "Project",
        source_name,
        {
            "Project": {
                "doctype":"Payment Application",
                "field_map": {
                    "name": "project",
                    "custom_total_advance_deducted":"adv_previous",
                    "custom_total_retention":"ret_previous",
                    "custom_completed_value":"work_done_previous"
                },
                "postprocess": update_details
            },
            "Task Summary": {
                "doctype": "Payment Application Item",
                "field_map": {
                    "name":"task_summary",
                    "item": "item_code",
                    "sales_order_item":"so_detail",
                    "pc_this":"amount"
                },
                "postprocess": update_item,
                "condition": lambda doc: abs(doc.pc_this) > 0
            },
        },
        target_doc,
    )
    return target_doc

def calculate_this(doc,method=None):
    this = 0
    if doc.custom_tasks:
        for row in doc.custom_tasks:
            if row.pc_this:
                this += row.pc_this
    doc.custom_this_payment = this

def create_task(doc,method):

    so = frappe.get_doc("Sales Order",doc.sales_order)

    for item in so.items:
        subject = item.item_code + " "+ doc.name
        if not frappe.db.exists("Task", subject):
            task = frappe.new_doc("Task")
            task.subject = subject
            task.status = "Open"
            task.exp_start_date = nowdate()
            task.exp_end_date = nowdate()
            task.project = doc.name
            task.custom_actual_qty_completed = 0.0
            task.custom_total_qty = item.qty
            task.custom_total_billable_amount = item.amount
            task.save()
            ts = frappe.db.get_value("Task Summary",{'parent':doc.name,'parenttype':'Project','sales_order_item':item.name,'item':item.item_code},'name')
            if ts:
                frappe.db.set_value("Task Summary",ts,"task",task.name)
            doc.reload()

def update_task_summary(doc,method):
    so = frappe.get_doc("Sales Order",doc.sales_order)
    doc.percent_complete_method = "Manual"
    for item in so.items:
        doc.append("custom_tasks",{
                   'item':item.item_code,
                   'sales_order_item':item.name,
                   'total':item.amount,
                   'total_qty':item.qty
               })