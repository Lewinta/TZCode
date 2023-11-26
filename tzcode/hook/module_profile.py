import frappe
from frappe.query_builder import functions as fn
from frappe.query_builder.custom import ConstantColumn
from frappe.core.doctype.module_profile.module_profile import ModuleProfile as _ModuleProfile

def validate(doc, method):
    # super(ModuleProfile, self).validate()
    calculate_totals(doc)

def calculate_totals(doc):
    fetch_module_info(doc)
    doc.selected_modules = len(doc.module_details)
    doc.extra_users = doc.users - 5 if doc.users > 5 else 0
    doc.users_amount = doc.extra_users * 20.0
    doc.modules_amount = sum([d.amount for d in doc.module_details])
    doc.total_amount = doc.modules_amount + doc.users_amount
    doc.monthly_fee = doc.total_amount * 0.05

def fetch_module_info(doc):
    DT = frappe.qb.DocType("DocType")
    MD = frappe.qb.DocType("Module Def")
    modules = [d.module for d in doc.module_details]
    if not modules:
        return
    module_data = frappe.qb.from_(DT).join(MD).on(
        DT.module == MD.name
    ).where(
        DT.module.isin(modules)
    ).select(
        DT.module, 
        fn.Count(1).as_("doctypes"),
    ).groupby( DT.module ).run(as_dict=True)
    
    doc.set("module_details", [])
    
    for row in module_data:
        doc.append("module_details", {
            "module": row.module,
            "doctypes": row.doctypes,
            "rate": 10,
            "amount": row.doctypes * 10,
        })
