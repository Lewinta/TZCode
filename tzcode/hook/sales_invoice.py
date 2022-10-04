import frappe
from personal.hook.accounts_controller import cancel_gl_entries, delete_gl_entries
from frappe.utils import add_months

def before_insert(doc, method):
	if doc.tipo_de_factura != 'Iguala':
		return
	year, month, day = str(add_months(doc.posting_date, -1)).split("-")
	doc.remarks = f"{get_month_name(month)} {year}"
	

def on_submit(doc, method):
    autoclose_so()

def on_cancel(doc, method):
    reopen_so()
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)

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
	month_name = {
		1: "Enero", 2: "Febrero",
		3: "Marzo", 4: "Abril",
		5: "Mayo", 6: "Junio",
		7: "Julio", 8: "Agosto",
		9: "Septiembre", 10: "Octubre",
		11: "Noviembre", 12: "Diciembre",
	}
	return month_name[int(month)]