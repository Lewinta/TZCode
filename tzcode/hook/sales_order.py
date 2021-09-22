import frappe
from frappe.utils import add_months, nowdate
import calendar
from frappe import _
def validate(doc, method):
    get_default_remarks(doc)

def get_default_remarks(doc):
    if not doc.auto_repeat:
        return
    last_month = add_months(nowdate(), -1)
    year, month, day = last_month.split("-")
    month_name = calendar.month_name[int(month)]

    doc.remarks = "Factura {} - {}".format(_(month_name), year)
