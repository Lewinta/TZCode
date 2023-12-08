import frappe

from frappe.utils import add_months

def before_insert(doc, method):
	# update exchange rate
	if not doc.dont_override_conversion_rate:
		doc.conversion_rate = get_latest_exchange_rate(from_currency=doc.currency)

	if doc.tipo_de_factura != 'Iguala':
		return

	year, month, day = str(add_months(doc.posting_date, -1)).split("-")
	doc.remarks = f"{get_month_name(month)} {year}"

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
	month_name = {
		1: "Enero", 2: "Febrero",
		3: "Marzo", 4: "Abril",
		5: "Mayo", 6: "Junio",
		7: "Julio", 8: "Agosto",
		9: "Septiembre", 10: "Octubre",
		11: "Noviembre", 12: "Diciembre",
	}
	return month_name[int(month)]


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
