# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lewin Villar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

class PMVisit(Document):
	def validate(self):
		self.set_default_date()
	
	def set_default_date(self):
		if "System Manager" in frappe.get_roles():
			return
		self.date = nowdate()
