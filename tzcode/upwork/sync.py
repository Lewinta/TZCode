# -*- coding: utf-8 -*-
"""Scheduled ingest and retention enforcement for Upwork job postings."""

import frappe
from frappe.utils import add_to_date, cint, flt, get_datetime, now_datetime

from tzcode.tzcode.doctype.upwork_job_posting.upwork_job_posting import (
	ACTED_ON_STATUSES,
)

# Guard against a misconfigured cron or a manual re-trigger loop hammering the API.
MIN_SECONDS_BETWEEN_POLLS = 300


def poll():
	"""Scheduled entry point. Fetch, filter, and store new matches."""
	settings = frappe.get_single("Upwork Settings")

	if not settings.enabled:
		return

	if _polled_too_recently(settings):
		return

	from tzcode.upwork import client, oauth

	try:
		access_token = oauth.get_valid_access_token(settings)
		nodes = client.search_jobs(settings, access_token)
	except Exception:
		_record_error(settings)
		frappe.log_error(
			title="Upwork poll failed", message=frappe.get_traceback()
		)
		return

	created = []
	for node in nodes:
		parsed = _parse_node(node)
		if not parsed:
			continue
		if not _matches_filters(parsed, settings):
			continue
		if frappe.db.exists("Upwork Job Posting", parsed["upwork_job_id"]):
			continue

		doc = frappe.get_doc(dict(doctype="Upwork Job Posting", **parsed))
		doc.insert(ignore_permissions=True)
		created.append(doc)

	settings.db_set("last_poll_at", now_datetime(), update_modified=False)
	settings.db_set("last_error", None, update_modified=False)
	frappe.db.commit()

	if created and settings.notify_telegram:
		_notify(created)

	return len(created)


def _polled_too_recently(settings):
	if not settings.last_poll_at:
		return False
	elapsed = (now_datetime() - get_datetime(settings.last_poll_at)).total_seconds()
	return elapsed < MIN_SECONDS_BETWEEN_POLLS


def _record_error(settings):
	message = str(frappe.get_traceback()).strip().splitlines()
	settings.db_set(
		"last_error", message[-1][:500] if message else "Unknown error",
		update_modified=False,
	)
	frappe.db.commit()


def _parse_node(node):
	"""Map a GraphQL node onto our fields, tolerating missing keys."""
	job_id = node.get("id") or node.get("ciphertext")
	if not job_id:
		return None

	ciphertext = node.get("ciphertext") or ""
	amount = node.get("amount") or {}
	hourly_min = node.get("hourlyBudgetMin") or {}
	hourly_max = node.get("hourlyBudgetMax") or {}
	client_data = node.get("client") or {}
	location = client_data.get("location") or {}
	total_spent = client_data.get("totalSpent") or {}

	is_hourly = bool(hourly_min.get("rawValue") or hourly_max.get("rawValue"))

	skills = ", ".join(
		s.get("name") for s in (node.get("skills") or []) if s and s.get("name")
	)

	verification = (client_data.get("verificationStatus") or "").upper()

	return {
		"upwork_job_id": str(job_id),
		"title": node.get("title"),
		"description": node.get("description"),
		"job_url": (
			"https://www.upwork.com/jobs/{0}".format(ciphertext)
			if ciphertext else None
		),
		"job_type": "Hourly" if is_hourly else "Fixed",
		"hourly_min": flt(hourly_min.get("rawValue")),
		"hourly_max": flt(hourly_max.get("rawValue")),
		"budget_min": flt(amount.get("rawValue")) if not is_hourly else 0,
		"budget_max": flt(amount.get("rawValue")) if not is_hourly else 0,
		"skills": skills,
		"client_country": location.get("country"),
		"client_total_spend": flt(total_spent.get("rawValue")),
		"client_payment_verified": 1 if verification == "VERIFIED" else 0,
		"posted_date": node.get("publishedDateTime") or node.get("createdDateTime"),
		"fetched_at": now_datetime(),
		"status": "New",
	}


def _matches_filters(parsed, settings):
	"""Budget floor plus at least one skill hit.

	This is the compliance boundary as much as a quality filter - a narrow,
	targeted search is what keeps this clear of the Bulk Access prohibition.
	"""
	if parsed["job_type"] == "Hourly":
		ceiling = flt(parsed.get("hourly_max")) or flt(parsed.get("hourly_min"))
		if ceiling and ceiling < flt(settings.min_hourly_rate):
			return False
	else:
		budget = flt(parsed.get("budget_max")) or flt(parsed.get("budget_min"))
		if budget and budget < flt(settings.min_fixed_budget):
			return False

	wanted = settings.get_skill_list()
	if not wanted:
		return True

	haystack = " ".join(
		filter(None, [parsed.get("title"), parsed.get("skills"), parsed.get("description")])
	).lower()

	return any(skill in haystack for skill in wanted)


def _notify(docs):
	"""Reuse the Telegram bot already configured in Tz Settings."""
	try:
		from tzcode.rss_monitor import send_telegram_message

		tz_settings = frappe.get_doc("Tz Settings")
		for doc in docs:
			text = "<b>{0}</b>\n{1}".format(doc.title or "Upwork job", doc.job_url or "")
			send_telegram_message(text, tz_settings)
	except Exception:
		frappe.log_error(
			title="Upwork Telegram notify failed", message=frappe.get_traceback()
		)


def purge_expired():
	"""Enforce the 24 hour retention cap.

	Upwork API Terms of Use s7 forbids storing Upwork Content or any information
	representing it, and permits caching for no more than 24 hours. The API & MCP
	Terms of Use s8.3 repeats the cap and adds that the timer may not be restarted
	by re-fetching. Postings the user never acted on are deleted outright;
	postings they acted on keep only their own notes, status and the job link.
	"""
	settings = frappe.get_single("Upwork Settings")
	retention_hours = min(cint(settings.retention_hours) or 24, 24)
	cutoff = add_to_date(now_datetime(), hours=-retention_hours)

	rows = frappe.get_all(
		"Upwork Job Posting",
		filters={"fetched_at": ["<", cutoff], "content_purged": 0},
		fields=["name", "status"],
	)

	deleted = purged = 0

	for row in rows:
		try:
			if row.status in ACTED_ON_STATUSES:
				frappe.get_doc("Upwork Job Posting", row.name).purge_content()
				purged += 1
			else:
				frappe.delete_doc(
					"Upwork Job Posting", row.name,
					ignore_permissions=True, force=True, delete_permanently=True,
				)
				deleted += 1
		except Exception:
			frappe.log_error(
				title="Upwork purge failed for {0}".format(row.name),
				message=frappe.get_traceback(),
			)

	frappe.db.commit()
	return {"deleted": deleted, "purged": purged}
