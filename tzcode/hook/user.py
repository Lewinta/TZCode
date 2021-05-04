import frappe

def validate(doc, event):
    if not doc.username:
        make_username(doc)
    
    first = doc.first_name.capitalize() if doc.first_name else ""
    last  = doc.last_name.capitalize() if doc.last_name else ""
    doc.update({
        "first_name": first,
        "last_name": last,
        "full_name": "{} {}".format(first, last),
    })
   
def make_username(doc):
    doc.username = '';

    first = doc.first_name.capitalize() if doc.first_name else ""
    last  = doc.last_name.capitalize() if doc.last_name else ""

    if doc.first_name:
        doc.username = first 

    if doc.last_name and doc.username:
        doc.username = "{}_{}".format(doc.username, last)
    else:
        doc.username = last