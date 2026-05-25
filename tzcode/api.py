# tzcode/api.py
# Whitelisted endpoints used by Client Scripts and external integrations.
# Has full Python access (NOT inside RestrictedPython sandbox).

import frappe
import requests


@frappe.whitelist()
def recheck_ecf_status(rnc):
    """
    Re-check Alanube e-CF directory for a given RNC and update the
    RNC Directory record with the result. Uses frappe.db.set_value()
    to bypass optimistic locking (no TimestampMismatchError on rapid clicks).
    """
    if not rnc:
        frappe.throw("RNC is required")
    if not frappe.db.exists("RNC Directory", rnc):
        frappe.throw(f"RNC {rnc} not found in directory")

    token = frappe.db.get_single_value("Alanube Settings", "token")
    if not token:
        frappe.throw("Alanube token not configured in Alanube Settings")

    url = "https://api.alanube.co/dom/v1/check-directory"

    # Default update payload (overwritten based on response)
    update = {
        "ecf_status": "Error",
        "ecf_url_recepcion": "",
        "ecf_company_id": "",
        "ecf_check_response_raw": "",
        "ecf_checked_at": frappe.utils.now_datetime(),
    }

    try:
        r = requests.get(
            url,
            params={"rnc": rnc},
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        raw = r.text[:500]

        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("rnc"):
                    d = data[0]
                    update["ecf_status"] = "Active"
                    update["ecf_url_recepcion"] = d.get("urlRecepcion", "")
                    update["ecf_company_id"] = d.get("urlRecepcion", "").rsplit("/", 1)[-1]
                elif isinstance(data, list) and data and data[0] == "":
                    update["ecf_status"] = "Not Active"
                else:
                    update["ecf_status"] = "Error"
                    raw = f"unexpected_body: {raw}"
            except ValueError as je:
                raw = f"json_parse_error: {je}; body: {raw}"
        else:
            raw = f"http_{r.status_code}: {raw}"

        update["ecf_check_response_raw"] = raw
    except Exception as e:
        update["ecf_check_response_raw"] = f"{type(e).__name__}: {str(e)[:400]}"

    # Bypass optimistic locking — directly write to DB
    frappe.db.set_value("RNC Directory", rnc, update, update_modified=True)
    frappe.db.commit()

    return {
        "ecf_status": update["ecf_status"],
        "ecf_url_recepcion": update["ecf_url_recepcion"],
        "checked_at": str(update["ecf_checked_at"]),
    }
