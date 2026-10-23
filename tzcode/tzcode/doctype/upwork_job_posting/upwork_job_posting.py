# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document

# Fields holding Upwork-authored content. These are cleared when the retention
# window closes; everything else on the doctype is either our own data or a
# pointer back to Upwork.
UPWORK_CONTENT_FIELDS = (
	"title",
	"description",
	"skills",
	"job_type",
	"hourly_min",
	"hourly_max",
	"budget_min",
	"budget_max",
	"client_country",
	"client_total_spend",
	"client_payment_verified",
	"posted_date",
)

# Statuses where the user has acted on the posting, so the record is kept as a
# record of their own activity, with the Upwork content stripped out.
ACTED_ON_STATUSES = ("Proposal Drafted", "Applied")


class UpworkJobPosting(Document):
	def purge_content(self):
		"""Strip Upwork-authored content but keep our own workflow data."""
		for field in UPWORK_CONTENT_FIELDS:
			self.set(field, None)

		self.content_purged = 1
		self.purged_at = frappe.utils.now_datetime()
		self.save(ignore_permissions=True)
