import frappe

def on_update(doc, method):
    set_bank_account(doc)

def set_bank_account(doc):
    # This function will set the bank account based on the account set in the 
    # mode of payment
    
    PE = frappe.qb.DocType("Payment Entry")
    MP = frappe.qb.DocType("Mode of Payment")
    MA = frappe.qb.DocType("Mode of Payment Account")
    BA = frappe.qb.DocType("Bank Account")

    frappe.qb.update(PE).join(MP).on(
        PE.mode_of_payment == MP.name
    ).join(MA).on(
        MP.name == MA.parent
    ).join(BA).on(
        MA.default_account == BA.account
    ).set(
        PE.bank_account, BA.name
    ).where(
        PE.name == doc.name
    ).run()

    # *** If you see the code above you are challenged to spot the issue. ***

    # frappe.db.sql(""" 
    #     UPDATE 
    #         `tabPayment Entry` AS PE 
    #     JOIN 
    #         `tabMode of Payment` AS MP 
    #     ON 
    #         PE.mode_of_payment = MP.name 
    #     JOIN 
    #         `tabMode of Payment Account` AS MA 
    #     ON 
    #         MP.name = MA.parent 
    #     JOIN 
    #         `tabBank Account` AS BA 
    #     ON 
    #         MA.default_account = BA.account 
    #     SET 
    #         PE.bank_account = BA.name 
    #     WHERE 
    #         PE.name = %s
    # """, doc.name)
