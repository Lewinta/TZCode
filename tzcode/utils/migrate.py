import frappe
from tzcode.utils.permission_manager import UserPermission

def after_migrate():
	add_permissions()
	# create_views()

def add_permissions():
	PM = UserPermission.create_perms
	# Read permissions are implicit
	
	# Bank
	PM('Bank', 'System Manager',  {'if_owner', 'set_user_permissions'}, inverse=True)
	PM('Bank', 'Accounts Manager',  {'write', 'create', 'export'})

	# Support Settings
	PM('Support Settings', 'Support Team')
	
	#Customer
	PM('Customer', 'Stock User')
	PM('Customer', 'Stock Manager')
	PM('Customer', 'Accounts Manager')

	#ToDo
	PM('ToDo', 'Support Team', {'write', 'create', 'report'})

def create_views():
	frappe.db.sql("drop view if exists `viewStatement`")
	frappe.db.commit()
	frappe.db.sql("""
	create view `viewStatement` AS
		SELECT 
			'Sales Invoice' as doctype,
			`tabSales Invoice`.name,
			`tabSales Invoice`.docstatus,
			`tabSales Invoice`.status,
			`tabSales Invoice`.ncf,
			`tabSales Invoice`.conversion_rate,
			`tabSales Invoice`.posting_date,
			`tabSales Invoice`.customer,
			`tabSales Invoice`.remarks,
			`tabSales Invoice`.total,
			`tabSales Invoice`.base_net_total,
			`tabSales Invoice`.net_total,
			`tabSales Invoice`.total_taxes_and_charges,
			`tabSales Invoice`.additional_discount_percentage,
			`tabSales Invoice`.base_total_taxes_and_charges,
			`tabSales Invoice`.grand_total,
			`tabSales Invoice`.base_grand_total,
			`tabSales Invoice`.grand_total - `tabSales Invoice`.outstanding_amount as paid_amount,
			`tabSales Invoice`.base_grand_total - `tabSales Invoice`.outstanding_amount as base_paid_amount,
			`tabSales Invoice`.discount_amount,
			`tabSales Invoice`.outstanding_amount / `tabSales Invoice`.conversion_rate as outstanding_amount,
			`tabSales Invoice`.outstanding_amount as base_outstanding_amount
		FROM
			`tabSales Invoice`
	
		UNION

		SELECT 
			'Sales Order' as doctype,
			`tabSales Order`.name,
			`tabSales Order`.docstatus,
			`tabSales Order`.status,
			'-' as ncf,
			`tabSales Order`.conversion_rate,
			`tabSales Order`.delivery_date as posting_date,
			`tabSales Order`.customer,
			`tabSales Order`.remarks,
			`tabSales Order`.total,
			`tabSales Order`.base_net_total,
			`tabSales Order`.net_total,
			`tabSales Order`.total_taxes_and_charges,
			`tabSales Order`.additional_discount_percentage,
			`tabSales Order`.base_total_taxes_and_charges,
			`tabSales Order`.grand_total,
			`tabSales Order`.base_grand_total,
			0.00 paid_amount,
			0.00 base_paid_amount,
			0.00 discount_amount,
			`tabSales Order`.grand_total as outstanding_amount,
			`tabSales Order`.base_grand_total as base_outstanding_amount
		FROM
			`tabSales Order`
	""")
	print("Statement View Created")