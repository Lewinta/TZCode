import frappe
from frappe import _
from frappe.utils import cint
from tzcode.hook.accounts_controller import cancel_gl_entries, delete_gl_entries

def validate(doc, method):
    set_cost_center(doc)

def before_update_after_submit(doc, method):
    # `validate` no corre en "update after submit", asi que el cascade hay que
    # repetirlo aqui: si no, cambiar el centro de costo de una factura enviada
    # repostea el GL con el CC nuevo en cuentas por pagar/banco pero deja los
    # items (y por tanto el gasto) en el CC viejo.
    set_cost_center(doc)

def on_cancel(doc, method):
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)

def set_cost_center(doc):
    if not doc.cost_center:
        return
    for row in (doc.items or []) + (doc.taxes or []):
        row.cost_center = doc.cost_center

@frappe.whitelist()
def update_cost_center(purchase_invoice: str, cost_center: str):
    
    if not frappe.has_permission("Purchase Invoice", "write"):
        frappe.throw(_("You do not have permission to update Purchase Invoices."))

    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("Only System Managers can perform this action."))

    if not purchase_invoice or not cost_center:
        frappe.throw(_("Purchase Invoice and Cost Center are required."))

    if not frappe.db.exists("Purchase Invoice", purchase_invoice):
        frappe.throw(_("Purchase Invoice not found."))

    if not frappe.db.exists("Cost Center", cost_center):
        frappe.throw(_("Invalid Cost Center."))

    pi = frappe.get_doc("Purchase Invoice", purchase_invoice)

    if pi.docstatus != 1:
        frappe.throw(_("Only submitted Purchase Invoices can be updated."))

    if pi.cost_center == cost_center:
        frappe.throw(_("New Cost Center is the same as the current one."))

    # ---------- Update Purchase Invoice ----------
    pi.db_set("cost_center", cost_center, update_modified=False)

    # ---------- Update Items ----------
    for row in pi.items + pi.taxes:
        row.db_set("cost_center", cost_center, update_modified=False)

    # ---------- Update GL Entries ----------
    gl_entries = frappe.db.get_all(
        "GL Entry",
        filters={
            "voucher_type": "Purchase Invoice",
            "voucher_no": pi.name,
            "is_cancelled": 0
        },
        fields=["name", "cost_center"]
    )

    if not gl_entries:
        frappe.throw(_("No GL Entries found for this Purchase Invoice."))

    for gle in gl_entries:
        if gle.cost_center != cost_center:
            frappe.db.set_value(
                "GL Entry",
                gle.name,
                "cost_center",
                cost_center,
                update_modified=False
            )

    frappe.db.commit()

    return {
        "status": "success",
        "purchase_invoice": pi.name,
        "new_cost_center": cost_center
    }