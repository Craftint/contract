app_name = "contract"
app_title = "Contract"
app_publisher = "Craft"
app_description = "Contracting"
app_email = "info@craftinteractive.ae"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/contract/css/contract.css"
# app_include_js = "/assets/contract/js/contract.js"

# include js, css files in header of web template
# web_include_css = "/assets/contract/css/contract.css"
# web_include_js = "/assets/contract/js/contract.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "contract/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Project" : "public/js/project.js",
	"Task": "public/js/task.js",
	"Sales Invoice": "public/js/sales_invoice.js"
	}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "contract.utils.jinja_methods",
# 	"filters": "contract.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "contract.install.before_install"
# after_install = "contract.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "contract.uninstall.before_uninstall"
# after_uninstall = "contract.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "contract.utils.before_app_install"
# after_app_install = "contract.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "contract.utils.before_app_uninstall"
# after_app_uninstall = "contract.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "contract.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"on_submit": "contract.events.sales_invoice.make_gl_entries",
	},
	"Task": {
		"before_save": "contract.events.task.update_progress",
		"validate": "contract.events.task.validate_qty",
	},
	"Project": {
		"after_insert": "contract.events.project.create_task",
		"before_insert": "contract.events.project.update_task_summary",
		"validate": "contract.events.project.calculate_this",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"contract.tasks.all"
# 	],
# 	"daily": [
# 		"contract.tasks.daily"
# 	],
# 	"hourly": [
# 		"contract.tasks.hourly"
# 	],
# 	"weekly": [
# 		"contract.tasks.weekly"
# 	],
# 	"monthly": [
# 		"contract.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "contract.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "contract.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "contract.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["contract.utils.before_request"]
# after_request = ["contract.utils.after_request"]

# Job Events
# ----------
# before_job = ["contract.utils.before_job"]
# after_job = ["contract.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"contract.auth.validate"
# ]
