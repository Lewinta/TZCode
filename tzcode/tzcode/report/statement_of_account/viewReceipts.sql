DROP VIEW IF EXISTS `viewReceipts`;

CREATE VIEW `viewReceipts`
AS
SELECT 
	'Payment Entry' AS doctype,
	`tabPayment Entry`.name as document,
	`tabPayment Entry`.posting_date,
	`tabPayment Entry`.party,
	`tabPayment Entry Reference`.allocated_amount as paid_amount,
	`tabPayment Entry Reference`.allocated_amount as base_paid_amount,
	`tabPayment Entry Reference`.reference_doctype,
	`tabPayment Entry Reference`.reference_name

FROM 
	`tabPayment Entry`
JOIN
	`tabPayment Entry Reference`
ON
	`tabPayment Entry`.name = `tabPayment Entry Reference`.parent
WHERE 
	`tabPayment Entry`.docstatus = 1

UNION

SELECT
	'Journal Entry' as doctype,
	`tabJournal Entry`.name as document,
	`tabJournal Entry`.posting_date,
	`tabJournal Entry Account`.party,
	IF(`tabJournal Entry Account`.debit > 0, `tabJournal Entry Account`.debit , `tabJournal Entry Account`.credit) as paid_amount,
	IF(`tabJournal Entry Account`.debit_in_account_currency > 0, `tabJournal Entry Account`.debit_in_account_currency , `tabJournal Entry Account`.credit_in_account_currency) as base_paid_amount,
	`tabJournal Entry Account`.reference_type as reference_doctype,
	`tabJournal Entry Account`.reference_name
FROM 
	`tabJournal Entry`
JOIN
	`tabJournal Entry Account`
ON
	`tabJournal Entry`.name = `tabJournal Entry Account`.parent
WHERE 
	`tabJournal Entry`.docstatus = 1
AND
	`tabJournal Entry Account`.reference_name IS NOT NULL
AND 
	`tabJournal Entry Account`.reference_type in (
		'Sales Order',
		'Sales Invoice',
		'Purchase Order',
		'Purchase Invoice'
	)
