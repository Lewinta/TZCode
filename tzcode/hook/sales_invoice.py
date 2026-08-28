import frappe

from frappe import _
from frappe.core.doctype.communication.email import make as send_email
from frappe.utils import add_months, flt

BLANK_REMARKS = {"", "No Remarks", "No hay observaciones"}
MONTH_NAMES = {
    1: "Enero", 2: "Febrero",
    3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre",
    11: "Noviembre", 12: "Diciembre",
}
PERIOD_REMARK_MONTHS = set(MONTH_NAMES.values())
CONVERSION_RATE_PRECISION = 2


def before_validate(doc, method):
    set_conversion_rate_precision(doc)


def set_conversion_rate_precision(doc):
    # The conversion rate must always be kept at 2 decimals. Rounding here (before the
    # controller runs) makes ERPNext recalculate every base_* amount with the rounded rate.
    if not doc.conversion_rate:
        return
    doc.conversion_rate = flt(doc.conversion_rate, CONVERSION_RATE_PRECISION)


def validate(doc, method):
    set_cost_center(doc)


def before_update_after_submit(doc, method):
    # `validate` no corre en "update after submit"; sin esto el GL se repostea
    # con el centro de costo nuevo pero los items quedan con el viejo.
    set_cost_center(doc)


def set_cost_center(doc):
    # Cascade the parent cost_center to items and taxes so reporting stays consistent.
    if not doc.cost_center:
        return
    for row in (doc.items or []) + (doc.taxes or []):
        row.cost_center = doc.cost_center


@frappe.whitelist()
def update_cost_center(sales_invoice: str, cost_center: str):
    if not frappe.has_permission("Sales Invoice", "write"):
        frappe.throw(_("You do not have permission to update Sales Invoices."))

    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("Only System Managers can perform this action."))

    if not sales_invoice or not cost_center:
        frappe.throw(_("Sales Invoice and Cost Center are required."))

    if not frappe.db.exists("Sales Invoice", sales_invoice):
        frappe.throw(_("Sales Invoice not found."))

    if not frappe.db.exists("Cost Center", cost_center):
        frappe.throw(_("Invalid Cost Center."))

    si = frappe.get_doc("Sales Invoice", sales_invoice)

    if si.docstatus != 1:
        frappe.throw(_("Only submitted Sales Invoices can be updated."))

    if si.cost_center == cost_center:
        frappe.throw(_("New Cost Center is the same as the current one."))

    si.db_set("cost_center", cost_center, update_modified=False)

    for row in si.items + si.taxes:
        row.db_set("cost_center", cost_center, update_modified=False)

    gl_entries = frappe.db.get_all(
        "GL Entry",
        filters={
            "voucher_type": "Sales Invoice",
            "voucher_no": si.name,
            "is_cancelled": 0,
        },
        fields=["name", "cost_center"],
    )

    if not gl_entries:
        frappe.throw(_("No GL Entries found for this Sales Invoice."))

    for gle in gl_entries:
        if gle.cost_center != cost_center:
            frappe.db.set_value(
                "GL Entry",
                gle.name,
                "cost_center",
                cost_center,
                update_modified=False,
            )

    frappe.db.commit()

    return {
        "status": "success",
        "sales_invoice": si.name,
        "new_cost_center": cost_center,
    }


def before_insert(doc, method):
    # update exchange rate
    if not doc.dont_override_conversion_rate:
        doc.conversion_rate = flt(
            get_latest_exchange_rate(from_currency=doc.currency), CONVERSION_RATE_PRECISION
        )

    set_recurring_period_remarks(doc)


def set_recurring_period_remarks(doc):
    if not should_set_recurring_period_remarks(doc):
        return

    year, month, day = str(add_months(doc.posting_date, -1)).split("-")
    doc.remarks = f"{get_month_name(month)} {year}"


def should_set_recurring_period_remarks(doc):
    remarks = (doc.remarks or "").strip()
    if remarks not in BLANK_REMARKS and not is_period_remark(remarks):
        return False

    return doc.tipo_de_factura == "Iguala" or bool(doc.auto_repeat)


def is_period_remark(remarks):
    parts = (remarks or "").strip().split()
    return len(parts) == 2 and parts[0] in PERIOD_REMARK_MONTHS and len(parts[1]) == 4 and parts[1].isdigit()


def get_comprobantes_conf_for_print(doc):
    filters = {
        "company": doc.company,
        "enabled": 1,
    }

    if doc.is_return:
        filters["document_type"] = "4"  # E34 - Credit Note
    elif doc.is_debit_note:
        filters["document_type"] = "3"  # E33 - Debit Note
    else:
        filters["tax_category"] = doc.tax_category

    return frappe.get_value(
        "Comprobantes Conf",
        filters,
        ["expiration", "description", "expiration"],
        as_dict=True,
    )


def before_print(doc, method, settings):
    print = frappe._dict({})
    print.comp = get_comprobantes_conf_for_print(doc)
    print.address = frappe.get_value(
        "Address",
        {"is_your_company_address":1},
        ["address_line1", "city","state", "phone", "fax"],
        as_dict=True
    )
    print.contact = frappe.get_value(
        "Contact",
        doc.contact_person,
        ["first_name", "last_name", "mobile_no", "email_id"],
        as_dict=True
    )
    print.owner_fullname = frappe.get_value("User", doc.owner, "full_name")
    print.return_against_ncf = frappe.get_value("Sales Invoice", doc.return_against, "ncf")
    print.contact = frappe.get_value(
        "Contact",
        doc.contact_person, 
        ["first_name", "last_name","mobile_no", "email_id"]
        , as_dict=True
    )
    
    doc.print = print

def on_submit(doc, method):
    autoclose_so()

def on_cancel(doc, method):
    reopen_so()

def autoclose_so():
    filters = {
        "docstatus": 1,
        "per_billed": 100,
        "status": ["!=", "closed"],
    }
    for name, in frappe.get_list("Sales Order", filters, as_list=True):
        so = frappe.get_doc("Sales Order", name)
        so.status = "Closed"
        so.db_update()
        frappe.db.commit()

def reopen_so():
    filters = {
        "docstatus": 1,
        "per_billed": ["<", 100],
        "status": "closed",
    }
    for name, in frappe.get_list("Sales Order", filters, as_list=True):
        so = frappe.get_doc("Sales Order", name)
        so.status = "To Bill"
        so.db_update()
        frappe.db.commit()

def send_whatsapp_notification(doc, method):
    from twilio.rest import Client
    twilio_settings = frappe.get_single("Twilio Settings")

    account_sid = twilio_settings.account_sid
    auth_token = twilio_settings.get_password(fieldname="auth_token")
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        from_=f'whatsapp:{twilio_settings.whatsapp_no}',
        body='Your Sales Order from Royal is ready here is the link: https://erpnext.karuwatech.com/desk#Form/Sales%20Order/SAL-ORD-2022-00723',
        to='whatsapp:+18298260772'
    )

def get_month_name(month):
    return MONTH_NAMES[int(month)]


def get_latest_exchange_rate(from_currency="USD", to_currency="DOP"):
    """
    Get the latest exchange rate for the given currencies.

    :param from_currency: The currency to convert from. Default is USD.
    :param to_currency: The currency to convert to. Default is DOP.
    :return: The latest exchange rate as a float.
    """
    doctype = "Currency Exchange"

    if from_currency == to_currency:
        return 1

    filters = {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "for_selling": 1,
    }

    field = ["exchange_rate"]
    order_by = "date Desc"

    return frappe.get_value(doctype, filters, field, order_by=order_by)


@frappe.whitelist()
def email_invoice(docname, email):
    return send_email(
        recipients=email.split(","),
        subject=f"Sales Invoice: {docname}",
        content=frappe.render_template('/templates/email/new_invoice.html', {}),
        doctype="Sales Invoice",
        name=docname,
        send_email=1,
        send_me_a_copy=0,
        print_format= "Factura de Venta",
        attachments=[],
        read_receipt=0,
        print_letterhead=1,
        print_language="en"
    )
