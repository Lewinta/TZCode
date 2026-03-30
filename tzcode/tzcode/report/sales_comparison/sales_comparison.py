# Copyright (c) 2025, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_months


def execute(filters=None):
    filters = filters or {}
    _validate(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def _validate(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required."))
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("From Date and To Date are required."))


def get_columns(filters):
    currency = frappe.get_cached_value("Company", filters["company"], "default_currency")
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 240},
        {"label": _("Avg. Billing"), "fieldname": "avg_billing", "fieldtype": "Currency", "options": currency, "width": 140},
        {"label": _("Last Month"), "fieldname": "last_month", "fieldtype": "Currency", "options": currency, "width": 130},
        {"label": _("Current Month"), "fieldname": "current_month", "fieldtype": "Currency", "options": currency, "width": 140},
        {"label": _("Paid Amount"), "fieldname": "paid_amount", "fieldtype": "Currency", "options": currency, "width": 140},
    ]


def _get_amount_field(filters):
    value_type = (filters.get("values") or "Gross Sales").strip()
    if value_type == "Net Sales":
        return "si.base_net_total"
    return "si.base_grand_total"


def _date_parts(filters):
    to_date = getdate(filters["to_date"])
    from_date = getdate(filters["from_date"])

    if from_date > to_date:
        frappe.throw(_("From Date cannot be after To Date."))

    current_start = getdate(f"{to_date.year}-{to_date.month:02d}-01")
    last_start = add_months(current_start, -1)

    months_elapsed = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month) + 1
    months_elapsed = max(months_elapsed, 1)

    return {
        "from_date": from_date,
        "to_date": to_date,
        "current_start": current_start,
        "last_start": last_start,
        "months_elapsed": months_elapsed,
    }


def get_data(filters):
    d = _date_parts(filters)
    amount_field = _get_amount_field(filters)

    params = {
        "company": filters["company"],
        "from_date": d["from_date"],
        "to_date": d["to_date"],
        "current_start": d["current_start"],
        "last_start": d["last_start"],
        "months_elapsed": d["months_elapsed"],
    }

    sql = f"""
        SELECT
            si.customer AS customer,

            ROUND(
                SUM(CASE
                        WHEN si.posting_date BETWEEN %(from_date)s AND %(to_date)s
                        THEN {amount_field} ELSE 0
                    END) / %(months_elapsed)s, 2
            ) AS avg_billing,

            ROUND(
                SUM(CASE
                        WHEN si.posting_date >= %(last_start)s
                         AND si.posting_date < %(current_start)s
                        THEN {amount_field} ELSE 0
                    END), 2
            ) AS last_month,

            ROUND(
                SUM(CASE
                        WHEN si.posting_date >= %(current_start)s
                         AND si.posting_date <= %(to_date)s
                        THEN {amount_field} ELSE 0
                    END), 2
            ) AS current_month,

            (
                SELECT SUM(pe.paid_amount)
                FROM `tabPayment Entry` pe
                WHERE
                    pe.payment_type = 'Receive'
                    AND pe.docstatus = 1
                    AND pe.posting_date BETWEEN %(current_start)s AND CURDATE()
                    AND pe.party = si.customer
            ) AS paid_amount

        FROM `tabSales Invoice` si
        WHERE
            si.docstatus = 1
            AND si.company = %(company)s
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY si.customer
        HAVING (avg_billing <> 0 OR last_month <> 0 OR current_month <> 0)
        ORDER BY avg_billing DESC
    """

    return frappe.db.sql(sql, params, as_dict=True)