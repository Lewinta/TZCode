import frappe
from pypika import Order
from frappe.utils import nowdate, date_diff, add_days


def all():
    pass


def daily():
    task_overdue_notification()
    today = nowdate()
    yesterday = add_days(today, -1)

    # "due_date": yesterday # removed from filters
    Invoice = frappe.qb.DocType("Sales Invoice")
    doclist = frappe.qb.from_(Invoice).select(
        Invoice.name,
        Invoice.customer,
        Invoice.posting_date
    ).where(
        (Invoice.status == "Overdue") &
        (Invoice.docstatus == 1)
    ).groupby(Invoice.customer).orderby(
        Invoice.customer
    ).orderby("posting_date").run()
    
    for d, in doclist:
        doc = frappe.get_doc("Sales Invoice", d)

        # send email for invoices this method every two days
        # if diff_days from today to due_date is greater divisible by 2
        # or if it was due yesterday
        due_days = date_diff(today, doc.due_date)
        frequency = doc.get("frequency", default=2)

        if isdivisible(due_days, frequency) \
                or doc.due_date == yesterday:
            doc.run_method("sales_invoice_overdue_notification")
    

def hourly():
    pass


def weekly():
    pass


def monthly():
    pass

def isdivisible(a, b):
    return a % b == 0

def task_overdue_notification():
    today = nowdate()
    yesterday = add_days(today, -1)

    # "due_date": yesterday # removed from filters
    doclist = frappe.get_list("Task", fields=["name"], filters={
                              "status": "Overdue"})
    for d in doclist:
        doc = frappe.get_doc("Task", d)

        if doc.exp_end_date:
            doc.run_method("tasks_overdue_notification")