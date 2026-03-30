import frappe
from frappe import qb

@frappe.whitelist()
def get_bank_accounts(company, mop):
    BA = qb.DocType('Bank Account')
    MP = qb.DocType('Mode of Payment')
    MA = qb.DocType('Mode of Payment Account')

    data = frappe.qb.from_(MP).join(MA).on(
        MP.name == MA.parent
    ).join(BA).on(
        MA.default_account == BA.account
    ).where(
        (MP.name == mop)&
        (MA.company == company)
    ).select(
        BA.name
    ).limit(1).run(as_dict=True)

    return data[0].name if data else None