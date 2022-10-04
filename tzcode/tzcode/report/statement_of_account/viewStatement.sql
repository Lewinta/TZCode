DROP VIEW IF EXISTS `viewStatement`;
CREATE VIEW 
	`viewStatement`
AS 
SELECT 

	'Sales Invoice' AS `doctype`,
	`tabSales Invoice`.`name` AS `name`,
	`tabSales Invoice`.`docstatus` AS `docstatus`,
	`tabSales Invoice`.`status` AS `status`,
	`tabSales Invoice`.`ncf` AS `ncf`,
	`tabSales Invoice`.`posting_date` AS `posting_date`,
	`tabSales Invoice`.`customer` AS `customer`,
	`tabSales Invoice`.`remarks` AS `remarks`,
	`tabSales Invoice`.`total` AS `total`,
	`tabSales Invoice`.`base_net_total` AS `base_net_total`,
	`tabSales Invoice`.`net_total` AS `net_total`,
	`tabSales Invoice`.`total_taxes_and_charges` AS `total_taxes_and_charges`,
	`tabSales Invoice`.`additional_discount_percentage` AS `additional_discount_percentage`,
	`tabSales Invoice`.`base_total_taxes_and_charges` AS `base_total_taxes_and_charges`,
	`tabSales Invoice`.`grand_total` AS `grand_total`,
	`tabSales Invoice`.`base_grand_total` AS `base_grand_total`,
	`tabSales Invoice`.`grand_total` - `tabSales Invoice`.`outstanding_amount` AS `paid_amount`,
	`tabSales Invoice`.`base_grand_total` - `tabSales Invoice`.`outstanding_amount` AS `base_paid_amount`,
	`tabSales Invoice`.`discount_amount` AS `discount_amount`,
	`tabSales Invoice`.`outstanding_amount` / `tabSales Invoice`.`conversion_rate` AS `outstanding_amount`,
	`tabSales Invoice`.`outstanding_amount` AS `base_outstanding_amount` 
from
	`tabSales Invoice` 
union
	select 
		'Sales Order' AS `doctype`,
		`tabSales Order`.`name` AS `name`,
		`tabSales Order`.`docstatus` AS `docstatus`,
		`tabSales Order`.`status` AS `status`,'-' AS `ncf`,
		`tabSales Order`.`delivery_date` AS `posting_date`,
		`tabSales Order`.`customer` AS `customer`,
		`tabSales Order`.`remarks` AS `remarks`,
		`tabSales Order`.`total` AS `total`,
		`tabSales Order`.`base_net_total` AS `base_net_total`,
		`tabSales Order`.`net_total` AS `net_total`,
		`tabSales Order`.`total_taxes_and_charges` AS `total_taxes_and_charges`,
		`tabSales Order`.`additional_discount_percentage` AS `additional_discount_percentage`,
		`tabSales Order`.`base_total_taxes_and_charges` AS `base_total_taxes_and_charges`,
		`tabSales Order`.`grand_total` AS `grand_total`,
		`tabSales Order`.`base_grand_total` AS `base_grand_total`,
		0.00 AS `paid_amount`,
		0.00 AS `base_paid_amount`,
		0.00 AS `discount_amount`,
		`tabSales Order`.`grand_total` AS `outstanding_amount`,
		`tabSales Order`.`base_grand_total` AS `base_outstanding_amount` from 
`tabSales Order`;