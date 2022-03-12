# Copyright (c) 2022, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CloudServer(Document):
	def validate(self):
		self.count_customers()
		self.calculate_total()

	def count_customers(self):
		self.total_customers = len(self.customers)

	def calculate_total(self):
		self.total_income = sum([
			c.monthly_bill if not c.disabled else 0 for c in self.customers
		])
		self.profit = flt(self.total_income) - flt(self.monthly_bill)