# -*- coding: utf-8 -*-
"""Upwork marketplace job ingest for bo.tzcode.tech.

Whitelisted entry points live here so that the OAuth callback resolves at
tzcode.upwork.oauth_callback, which is the Callback URL registered on the
Upwork API key. Do not move or rename it without updating the key.
"""

import frappe
from frappe import _


@frappe.whitelist()
def start_authorization():
	"""Return the Upwork consent URL. Visit it once to link the account."""
	frappe.only_for("System Manager")

	from tzcode.upwork import oauth

	return oauth.build_authorize_url()


@frappe.whitelist()
def oauth_callback(code=None, state=None, **kwargs):
	"""Upwork redirects here after the user grants access."""
	frappe.only_for("System Manager")

	from tzcode.upwork import oauth

	if not code:
		frappe.throw(_("Upwork did not return an authorization code."))

	oauth.verify_state(state)
	oauth.exchange_code_for_token(code)

	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = "/app/upwork-settings"


@frappe.whitelist()
def test_connection():
	"""Run one live search and report what came back, without storing anything.

	Use this first once Upwork approves the key, to confirm the GraphQL
	selection set in client.py matches the live schema.
	"""
	frappe.only_for("System Manager")

	from tzcode.upwork import client, oauth

	settings = frappe.get_single("Upwork Settings")
	access_token = oauth.get_valid_access_token(settings)
	nodes = client.search_jobs(settings, access_token)

	return {
		"returned": len(nodes),
		"sample_fields": sorted((nodes[0] or {}).keys()) if nodes else [],
	}


@frappe.whitelist()
def run_poll_now():
	"""Manually trigger the ingest."""
	frappe.only_for("System Manager")

	from tzcode.upwork import sync

	return sync.poll()


@frappe.whitelist()
def run_purge_now():
	"""Manually enforce the retention cap."""
	frappe.only_for("System Manager")

	from tzcode.upwork import sync

	return sync.purge_expired()


# Scheduler targets.
def scheduled_poll():
	from tzcode.upwork import sync

	sync.poll()


def scheduled_purge():
	from tzcode.upwork import sync

	sync.purge_expired()
