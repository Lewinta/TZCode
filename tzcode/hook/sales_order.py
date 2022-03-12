import frappe
from frappe.utils import add_months, nowdate
import calendar
from frappe import _
def validate(doc, method):
    get_default_remarks(doc)

def get_default_remarks(doc):
    month_names = {
        "01": "Ene", "02": "Feb", "03": "Ene",
        "04": "Mar", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Ago", "09": "Sep",
        "10": "Oct", "11": "Nov", "12": "Dic",
    }
    if not doc.auto_repeat or doc.remarks:
        return
    last_month = add_months(nowdate(), -1)
    year, month, day = last_month.split("-")
    month_name = calendar.month_name[int(month)]

    doc.remarks = "Mes de {} {}".format(month_names[month], year)
