import frappe
from frappe.utils import add_months, nowdate
import calendar

def validate(doc, method):
    get_default_remarks(doc)

def get_default_remarks(doc):
    if doc.remarks:
        return
    last_month = add_months(nowdate(), -1)
    year, month, day = last_month.split("-")
    month_name = calendar.month_name[int(month)]

    doc.remarks = "Invoice {} - {}".format(month_name, year)
