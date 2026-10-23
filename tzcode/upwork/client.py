# -*- coding: utf-8 -*-
"""Thin GraphQL client for the Upwork marketplace job search."""

import frappe
import requests
from frappe import _

GRAPHQL_URL = "https://api.upwork.com/graphql"
REQUEST_TIMEOUT = 45

# marketplaceJobPostingsSearch is the authenticated search. The deprecated
# marketplaceJobPostings is deliberately not used.
#
# NOTE: this selection set is written from Upwork's published schema but has not
# been executed against a live key yet - the API key is still Disabled pending
# Upwork review. Run tzcode.upwork.test_connection() once it is approved; if a
# field name is rejected, adjust it here. Everything downstream reads the
# response defensively, so a missing field degrades rather than crashes.
SEARCH_QUERY = """
query marketplaceJobPostingsSearch(
  $marketPlaceJobFilter: MarketplaceJobPostingsSearchFilter,
  $searchType: MarketplaceJobPostingSearchType,
  $sortAttributes: [MarketplaceJobPostingSearchSortAttribute]
) {
  marketplaceJobPostingsSearch(
    marketPlaceJobFilter: $marketPlaceJobFilter,
    searchType: $searchType,
    sortAttributes: $sortAttributes
  ) {
    totalCount
    edges {
      node {
        id
        title
        description
        ciphertext
        duration
        engagement
        createdDateTime
        publishedDateTime
        amount { rawValue currency }
        hourlyBudgetMin { rawValue currency }
        hourlyBudgetMax { rawValue currency }
        skills { name }
        client {
          totalHires
          totalSpent { rawValue currency }
          verificationStatus
          location { country }
        }
      }
    }
  }
}
"""


def execute(query, variables, access_token):
	response = requests.post(
		GRAPHQL_URL,
		json={"query": query, "variables": variables},
		headers={
			"Authorization": "Bearer {0}".format(access_token),
			"Content-Type": "application/json",
		},
		timeout=REQUEST_TIMEOUT,
	)

	# 300 requests/minute per IP. A 30 minute poll is nowhere near it, but a
	# misconfigured cron could be, so surface it clearly rather than retrying.
	if response.status_code == 429:
		frappe.throw(_("Upwork rate limit hit (HTTP 429). Back off before retrying."))

	if response.status_code != 200:
		frappe.throw(
			_("Upwork API returned HTTP {0}: {1}").format(
				response.status_code, response.text[:500]
			)
		)

	payload = response.json()

	if payload.get("errors"):
		messages = "; ".join(
			e.get("message", "unknown") for e in payload.get("errors") or []
		)
		frappe.throw(_("Upwork GraphQL error: {0}").format(messages))

	return payload.get("data") or {}


def get_search_queries(settings):
	"""One search per non-empty line of search_query."""
	lines = (settings.search_query or "").splitlines()
	return [line.strip() for line in lines if line.strip()] or ["ERPNext OR Frappe"]


def search_jobs(settings, access_token):
	"""Run one narrow, filtered search per configured query and return the raw nodes.

	Deliberately a single page per query. Paginating through the marketplace is
	exactly what the API & MCP Terms define as Bulk Access.
	"""
	first = min(int(settings.max_results_per_poll or 50), 100)

	nodes = []
	seen = set()

	for query in get_search_queries(settings):
		variables = {
			"marketPlaceJobFilter": {
				"searchExpression_eq": query,
				"pagination_eq": {"after": "0", "first": first},
			},
			"searchType": "USER_JOBS_SEARCH",
			"sortAttributes": [{"field": "RECENCY"}],
		}

		data = execute(SEARCH_QUERY, variables, access_token)
		search = (data or {}).get("marketplaceJobPostingsSearch") or {}

		for edge in search.get("edges") or []:
			node = (edge or {}).get("node")
			if node and node.get("id") not in seen:
				seen.add(node.get("id"))
				nodes.append(node)

	return nodes
