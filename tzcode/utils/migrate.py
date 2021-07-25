import frappe

def after_migrate():
	pass
	# create_views()

def create_views():
	frappe.db.sql("drop view if exists `viewStatement`")
	frappe.db.commit()
	frappe.db.sql("""
	create view `viewStatement` AS
		SELECT 
			`tabSales Invoice`.name,
			`tabSales Invoice`.docstatus,
			`tabSales Invoice`.status,
			`tabSales Invoice`.posting_date,
			`tabSales Invoice`.customer,
			`tabSales Invoice`.remarks,
			`tabSales Invoice`.total,
			`tabSales Invoice`.base_total,
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
			`tabSales Order`.name,
			`tabSales Order`.docstatus,
			`tabSales Order`.status,
			`tabSales Order`.delivery_date as posting_date,
			`tabSales Order`.customer,
			`tabSales Order`.remarks,
			`tabSales Order`.total,
			`tabSales Order`.base_total,
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