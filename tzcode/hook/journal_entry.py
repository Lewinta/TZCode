import frappe
from tzcode.hook.accounts_controller import cancel_gl_entries, delete_gl_entries

def on_cancel(doc, method):
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)

def on_update(doc, method):
    set_bank_accounts(doc)

def set_bank_accounts(doc):
    # This function will set the bank account for the journal entry accounts
    # that are missing it. It will use the account and company to find the bank account
    # and set it to the journal entry account
    
    BA = frappe.qb.DocType("Bank Account")
    JA = frappe.qb.DocType("Journal Entry Account")

    frappe.qb.update(JA ).join(BA).on(
        (JA.account == BA.account)&
        (BA.is_company_account == 1)
    ).set(
        JA.bank_account, BA.name
    ).where(
        JA.parent == doc.name
    ).run()