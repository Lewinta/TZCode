import frappe


@frappe.whitelist(allow_guest=True)
def store_data():
    # log the data received
    doc = frappe.new_doc("Error Log")

    doc.update({
        "title": "Discord Webhook",
        "error": frappe.as_json({
            "headers": frappe.request.headers,
            "data": frappe.local.form_dict,
        })
    })

    doc.flags.ignore_permissions = True
    doc.flags.ignore_mandatory = True
    doc.save()

# token: MTA5NTkwNDM2Njc0NzE5MzQwNA.G82ZUL.r4S60p-w-CPE-4jlttL6wnfoGCqOKwMbhHg1Ic


@frappe.whitelist()
def query_issues(*args, **kwargs):
    kwargs.pop("cmd")
    fields = {
        "name",
        "subject",
        "status",
        "priority",
        "description",
    }
    return frappe.get_all("Issue", filters=kwargs, fields=fields)
