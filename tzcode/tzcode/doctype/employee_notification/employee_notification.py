# Copyright (c) 2024, Yefri Tavarez and contributors
# For license information, please see license.txt

import functools

import frappe
from frappe.model.document import Document

class EmployeeNotification(Document):
	def before_insert(self):
		self.render_template()

	def after_insert(self):
		self.set_title()

	@frappe.whitelist()
	def render_template(self, from_template=False):
		context = {
			"notification": self,
			"template": self.get_template(self.notification_template),
			"employee": self.get_employee(self.employee),
			"owner": self.get_user(self.owner),
		}

		if from_template:
			template = self.get_template(self.notification_template)
			self.content = template.template

		self.content = frappe.render_template(
			self.content, context
		)

	def get_employee(self, name):
		doctype = "Employee"
		return frappe.get_doc(doctype, name)

	def get_user(self, name):
		doctype = "User"
		return frappe.get_doc(doctype, name)

	@functools.lru_cache(maxsize=1)
	def get_template(self, name):
		doctype = "Employee Notification Template"
		return frappe.get_doc(doctype, name)

	def set_title(self):
		title = f"EMP-NOTIF-{self.name:04d}"
		self.db_set("title", title)
