# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "tzcode"
app_title = "TZCode"
app_publisher = "Lewin Villar"
app_description = "Customization app for TZCode"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "lewinvillar@tzcode.tech"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tzcode/css/tzcode.css"
# app_include_js = "/assets/tzcode/js/tzcode.js"

# include js, css files in header of web template
# web_include_css = "/assets/tzcode/css/tzcode.css"
# web_include_js = "/assets/tzcode/js/tzcode.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tzcode/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Payroll Entry": "public/js/payroll_entry.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
    "ToDo": "public/js/todo.js",
    "Contact": "public/js/contact.js",
    "Issue": "public/js/issue.js",
    "User": "public/js/user.js",
    "Task": "public/js/task.js",
}
doctype_list_js = {
    "Customer": "public/js/customer_list.js",
    "Issue": "public/js/issue_list.js",
    "Payroll Entry": "public/js/payroll_entry.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

app_logo_url = "/assets/tzcode/images/blue_logo.svg"

website_context = {
    "favicon": 	"/assets/tzcode/images/favicon.png",
    "splash_image": "/assets/tzcode/images/blue_logo.svg"
}

# Fixtures
# ----------

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": {
            "name": (
                "in", (
                    "Sales Invoice-tipo_de_factura"
                    "ToDo-resolution_details"
                    "Customer-monthly_bill",
                    "Customer-base_monthly_bill",
                )
            )
        }
    },
    {
        "doctype": "Property Setter",
        "filters": {
            "name": (
                "in", (
                    "Issue-main-set_only_once",
                    "Issue-status-options",
                    "Issue-customer-in_standard_filter",
                    "Issue-status-read_only",
                    "ToDo-status-options",
                    "Supplier-main-search_fields",
                    "Sales Invoice-remarks-allow_on_submit",
                    "Sales Invoice-naming_series-options",
                    "Sales Invoice Item-price_list_rate-read_only",
                    "Sales Invoice-main-default_print_format",
                    "Sales Order-main-default_print_format",
                    "Sales Order Item-description-allow_on_submit",
                    "Salary Slip-main-default_print_format",
                    "Payroll Entry-department-default",
                    "Payroll Entry-bank_account-default",
                    "Payroll Entry-payment_account-default",
                    "Payroll Entry-payroll_frequency-default",
                )
            )
        }
    },
    {
        "doctype": "Print Format",
        "filters": {
            "name": (
                "in", (
                    "Factura de Venta",
                    "Orden de Venta",
                    "Salary Slip",
                    "Quotation",
                    "Apertura de Cuenta Popular",
                    "Recibo de Ingreso JV",
                    "Carta de Retención",
                    "Proveedor de Servicios",
                    "Contrato de Trabajo",
                    "Orden de Venta Local",
                )
            )
        }
    },
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tzcode.install.before_install"
# after_install = "tzcode.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tzcode.notifications.get_notification_config"

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
    "Issue": "tzcode.controllers.overrides.issue.Issue"
}


# Jinja
# ---------------

jenv = {
    "methods": ["get_employee_salary:tzcode.jinja.methods.get_employee_salary"]
}
# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        "validate": "tzcode.hook.user.validate",
    },
    "Task": {
        "validate": "tzcode.hook.task.validate",
    },
    "Sales Invoice": {
        "before_insert": "tzcode.hook.sales_invoice.before_insert",
        "on_submit": "tzcode.hook.sales_invoice.on_submit",
        "on_cancel": "tzcode.hook.sales_invoice.on_cancel",
        "on_trash": "tzcode.hook.sales_invoice.on_trash",
    },
    "Sales Order": {
        "validate": "tzcode.hook.sales_order.validate",
    },
    "Purchase Invoice": {
        "on_cancel": "tzcode.hook.purchase_invoice.on_cancel",
        "on_trash": "tzcode.hook.purchase_invoice.on_trash",
    },
    "Journal Entry": {
        "on_cancel": "tzcode.hook.journal_entry.on_cancel",
        "on_trash": "tzcode.hook.journal_entry.on_trash",
    },
    "Issue": {
        "on_update": "tzcode.hook.issue.on_update",
    },
    "Customer": {
        "on_update": "tzcode.hook.customer.on_update",
    },
    "Auto Repeat": {
        "validate": "tzcode.hook.auto_repeat.validate",
    },
    "ToDo": {
        "on_update": "tzcode.hook.todo.on_update",
        "validate": "tzcode.hook.todo.validate",
        "after_insert": "tzcode.hook.todo.after_insert",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tzcode.tasks.all"
# 	],
# 	"daily": [
# 		"tzcode.tasks.daily"
# 	],
# 	"hourly": [
# 		"tzcode.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tzcode.tasks.weekly"
# 	]
# 	"monthly": [
# 		"tzcode.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "tzcode.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
    "validate_token": "tzcode.client.validate_token"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tzcode.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

after_migrate = "tzcode.utils.migrate.after_migrate"

# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {
        "doctype": "{doctype_4}"
    }
]

default_mail_footer = """
	<span>
		Sent via
		<a class="text-muted" href="https://tzcode.tech" target="_blank">
			TZCode
		</a>
	</span>
"""
