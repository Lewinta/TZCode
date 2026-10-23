# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document

# Upwork API Terms of Use s7 and API & MCP Terms of Use s8.3 both cap caching of
# Upwork Content at 24 hours. This is a hard ceiling, not a preference.
MAX_RETENTION_HOURS = 24


class UpworkSettings(Document):
	def validate(self):
		self.validate_retention()
		self.validate_poll_ceiling()

	def validate_retention(self):
		if not self.retention_hours or self.retention_hours < 1:
			self.retention_hours = MAX_RETENTION_HOURS

		if self.retention_hours > MAX_RETENTION_HOURS:
			frappe.throw(
				_("Retention Hours cannot exceed {0}. Upwork's API Terms of Use (section 7) and "
				  "API & MCP Terms of Use (section 8.3) require Upwork Content to be permanently "
				  "deleted after 24 hours.").format(MAX_RETENTION_HOURS)
			)

	def validate_poll_ceiling(self):
		if not self.max_results_per_poll or self.max_results_per_poll < 1:
			self.max_results_per_poll = 50

		if self.max_results_per_poll > 100:
			frappe.throw(
				_("Max Results Per Poll cannot exceed 100. Upwork's API & MCP Terms of Use "
				  "prohibit Bulk Access, which covers repeated or paginated retrieval of all or "
				  "substantially all job postings. Keep the search narrow.")
			)

	def get_skill_list(self):
		return [s.strip().lower() for s in (self.skills or "").split(",") if s.strip()]
