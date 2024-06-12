import frappe
from datetime import datetime, timedelta

def week_start(date=None):
    """
    Returns the start of the current week based on the given date.
    If no date is provided, it defaults to the current date.
    """
    if date is None:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Calculate the start of the current week (Monday)
    start_of_week = date - timedelta(days=date.weekday())

    return start_of_week

def week_end(date=None):
    """
    Returns the end of the current week based on the given date.
    If no date is provided, it defaults to the current date.
    """
    if date is None:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Calculate the start of the current week (Monday)
    start_of_week = date - timedelta(days=date.weekday())

    # Calculate the end of the current week (Sunday)
    end_of_week = start_of_week + timedelta(days=6)

    return end_of_week

def get_exchange_rates(transaction_date=None):
    # Get the exchange Rate between DOP and USD
    # This is a Freemium service and we must control the usage
    # to avoid being charged ;)
    import requests
    from_currency = "DOP"
    to_currency = "USD"
    settings = frappe.get_cached_doc("Currency Exchange Settings")
    if not transaction_date:
        transaction_date = frappe.utils.today()
    
    # We must skip if transaction_date is a weekend
    if datetime.strptime(transaction_date, "%Y-%m-%d").weekday() in [5, 6]:
        return

    req_params = {
        "transaction_date": transaction_date,
        "from_currency": from_currency,
        "to_currency": to_currency,
    }
    params = {}
    for row in settings.req_params:
        params[row.key] = format_ces_api(row.value, req_params)
    response = requests.get(format_ces_api(settings.api_endpoint, req_params), params=params)

    # expire in 6 hours
    response.raise_for_status()
    value = response.json()
    for res_key in settings.result_key:
        value = value[format_ces_api(str(res_key.key), req_params)]
    
    if value:
        dop_usd_exchange = frappe.new_doc("Currency Exchange")
        usd_dop_exchange = frappe.new_doc("Currency Exchange")
        defaults = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "transaction_date": transaction_date,
            "for_buying": 0,
            "for_selling": 1,
        }
        dop_usd_exchange.update(defaults)
        usd_dop_exchange.update(defaults)

        dop_usd_exchange.exchange_rate = value
        usd_dop_exchange.update({
            "exchange_rate": 1.0/value,
            "from_currency": dop_usd_exchange.to_currency,
            "to_currency": dop_usd_exchange.from_currency,
        }) 

        dop_usd_exchange.save()
        usd_dop_exchange.save()

def format_ces_api(data, param):
	return data.format(
		transaction_date=param.get("transaction_date"),
		to_currency=param.get("to_currency"),
		from_currency=param.get("from_currency"),
	)