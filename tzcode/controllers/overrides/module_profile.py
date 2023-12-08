import frappe
from frappe.query_builder import functions as fn
from frappe.core.doctype.module_profile.module_profile import ModuleProfile as FrappeModuleProfile

class ModuleProfile(FrappeModuleProfile):
    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        self.fetch_module_info()
        self.selected_modules = len(self.module_details)
        self.extra_users = self.users - 5 if self.users > 5 else 0
        self.users_amount = self.extra_users * 20.0
        self.modules_amount = sum([d.amount for d in self.module_details])
        self.total_amount = self.modules_amount + self.users_amount
        self.monthly_fee = self.total_amount * 0.05

    def fetch_module_info(self):
        DT = frappe.qb.DocType("DocType")
        MD = frappe.qb.DocType("Module Def")
        modules = [d.module for d in self.module_details]
        if not modules:
            return
        module_data = frappe.qb.from_(DT).join(MD).on(
            DT.module == MD.name
        ).where(
            DT.module.isin(modules)
        ).select(
            DT.module, 
            fn.Count(1).as_("doctypes"),
        ).groupby( DT.module ).run(as_dict=True, debug=True)
        
        self.set("module_details", [])
        
        for row in module_data:
            self.append("module_details", {
                "module": row.module,
                "doctypes": row.doctypes,
                "rate": 10,
                "amount": row.doctypes * 10,
            })
