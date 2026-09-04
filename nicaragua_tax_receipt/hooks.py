app_name = "nicaragua_tax_receipt"
app_title = "Nicaragua Tax Receipt"
app_publisher = "Inversiones BEL"
app_description = "Control de comprobantes oficiales para retenciones en ERPNext"
app_email = "soporte@inversionesbel.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "nicaragua_tax_receipt",
# 		"logo": "/assets/nicaragua_tax_receipt/logo.png",
# 		"title": "Nicaragua Tax Receipt",
# 		"route": "/nicaragua_tax_receipt",
# 		"has_permission": "nicaragua_tax_receipt.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nicaragua_tax_receipt/css/nicaragua_tax_receipt.css"
# app_include_js = "/assets/nicaragua_tax_receipt/js/nicaragua_tax_receipt.js"

# include js, css files in header of web template
# web_include_css = "/assets/nicaragua_tax_receipt/css/nicaragua_tax_receipt.css"
# web_include_js = "/assets/nicaragua_tax_receipt/js/nicaragua_tax_receipt.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "nicaragua_tax_receipt/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Payment Entry": "public/js/payment_entry.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "nicaragua_tax_receipt/public/icons.svg"

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
# 	"methods": "nicaragua_tax_receipt.utils.jinja_methods",
# 	"filters": "nicaragua_tax_receipt.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "nicaragua_tax_receipt.install.before_install"
after_install = "nicaragua_tax_receipt.install.after_install"
after_migrate = ["nicaragua_tax_receipt.maintenance.after_migrate"]

# Uninstallation
# ------------

# before_uninstall = "nicaragua_tax_receipt.uninstall.before_uninstall"
# after_uninstall = "nicaragua_tax_receipt.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "nicaragua_tax_receipt.utils.before_app_install"
# after_app_install = "nicaragua_tax_receipt.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "nicaragua_tax_receipt.utils.before_app_uninstall"
# after_app_uninstall = "nicaragua_tax_receipt.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nicaragua_tax_receipt.notifications.get_notification_config"

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

override_doctype_class = {
	"Payment Entry": "nicaragua_tax_receipt.overrides.payment_entry.PaymentEntry"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Payment Entry": {
		"validate": "nicaragua_tax_receipt.tax_receipt.validate_payment_entry",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"nicaragua_tax_receipt.tasks.all"
# 	],
# 	"daily": [
# 		"nicaragua_tax_receipt.tasks.daily"
# 	],
# 	"hourly": [
# 		"nicaragua_tax_receipt.tasks.hourly"
# 	],
# 	"weekly": [
# 		"nicaragua_tax_receipt.tasks.weekly"
# 	],
# 	"monthly": [
# 		"nicaragua_tax_receipt.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "nicaragua_tax_receipt.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "nicaragua_tax_receipt.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "nicaragua_tax_receipt.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["nicaragua_tax_receipt.utils.before_request"]
# after_request = ["nicaragua_tax_receipt.utils.after_request"]

# Job Events
# ----------
# before_job = ["nicaragua_tax_receipt.utils.before_job"]
# after_job = ["nicaragua_tax_receipt.utils.after_job"]

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
# 	"nicaragua_tax_receipt.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
