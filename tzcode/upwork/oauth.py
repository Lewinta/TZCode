# -*- coding: utf-8 -*-
"""OAuth 2.0 handling for the Upwork API.

The API key registered for bo.tzcode.tech is an authorization-code key: the
"Client Credential key for Service Account" option is not offered in the
personal freelancer context. So the flow is a one-time manual authorization,
after which the stored refresh token keeps the scheduled poll running
unattended.
"""

import frappe
import requests
from frappe import _
from frappe.utils import add_to_date, get_datetime, now_datetime

AUTHORIZE_URL = "https://www.upwork.com/ab/account-security/oauth2/authorize"
TOKEN_URL = "https://www.upwork.com/api/v3/oauth2/token"

# Refresh a little early so a long-running poll never races the expiry.
EXPIRY_SKEW_SECONDS = 120
STATE_CACHE_KEY = "upwork_oauth_state"
REQUEST_TIMEOUT = 30


def get_settings():
	return frappe.get_single("Upwork Settings")


def build_authorize_url(settings=None):
	"""Return the URL the user visits once to grant access."""
	settings = settings or get_settings()

	if not settings.client_id:
		frappe.throw(_("Set the Client ID in Upwork Settings first."))

	state = frappe.generate_hash(length=32)
	frappe.cache().set_value(STATE_CACHE_KEY, state, expires_in_sec=900)

	params = {
		"response_type": "code",
		"client_id": settings.client_id,
		"redirect_uri": settings.redirect_uri,
		"state": state,
	}
	return "{0}?{1}".format(AUTHORIZE_URL, frappe.utils.urlencode(params))


def exchange_code_for_token(code, settings=None):
	settings = settings or get_settings()

	payload = {
		"grant_type": "authorization_code",
		"code": code,
		"client_id": settings.client_id,
		"client_secret": settings.get_password("client_secret"),
		"redirect_uri": settings.redirect_uri,
	}
	return _request_token(payload, settings)


def refresh_access_token(settings=None):
	settings = settings or get_settings()

	refresh_token = settings.get_password("refresh_token", raise_exception=False)
	if not refresh_token:
		frappe.throw(_("No refresh token stored. Re-authorize the Upwork connection."))

	payload = {
		"grant_type": "refresh_token",
		"refresh_token": refresh_token,
		"client_id": settings.client_id,
		"client_secret": settings.get_password("client_secret"),
	}
	return _request_token(payload, settings)


def _request_token(payload, settings):
	response = requests.post(
		TOKEN_URL,
		data=payload,
		headers={"Content-Type": "application/x-www-form-urlencoded"},
		timeout=REQUEST_TIMEOUT,
	)

	if response.status_code != 200:
		# Never let the secret or the code reach the error log.
		frappe.throw(
			_("Upwork token request failed ({0}): {1}").format(
				response.status_code, response.text[:500]
			)
		)

	data = response.json()
	_store_tokens(settings, data)
	return data


def _store_tokens(settings, data):
	access_token = data.get("access_token")
	if not access_token:
		frappe.throw(_("Upwork did not return an access token."))

	settings.access_token = access_token

	# Upwork rotates the refresh token on each use; keep the old one if absent.
	if data.get("refresh_token"):
		settings.refresh_token = data.get("refresh_token")

	expires_in = int(data.get("expires_in") or 0)
	if expires_in:
		settings.token_expires_at = add_to_date(
			now_datetime(), seconds=expires_in - EXPIRY_SKEW_SECONDS
		)

	settings.save(ignore_permissions=True)
	frappe.db.commit()


def get_valid_access_token(settings=None):
	"""Return a usable access token, refreshing it if it has expired."""
	settings = settings or get_settings()

	access_token = settings.get_password("access_token", raise_exception=False)
	expires_at = settings.token_expires_at

	if access_token and expires_at and get_datetime(expires_at) > now_datetime():
		return access_token

	refresh_access_token(settings)
	settings.reload()
	return settings.get_password("access_token")


def verify_state(state):
	expected = frappe.cache().get_value(STATE_CACHE_KEY)
	if not expected or state != expected:
		frappe.throw(_("OAuth state mismatch. Start the authorization again."))
	frappe.cache().delete_value(STATE_CACHE_KEY)
