# Copyright (c) 2023, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.query_builder import CustomFunction, Criterion, Case, Query, functions as fn
from frappe.query_builder.custom import ConstantColumn

def execute(filters=None):
	if filters.get("summary"):	
		return get_columns(), get_data(filters)
	else:
		return get_summary_columns(), get_summary_data(filters)


def get_columns():
	return [
		
		"Employee:Data:200",
		"Old:Int:80",
		"Open:Int:80",
		"% Open:Percent:90",
		"Closed:Int:80",
		"% Closed:Percent:90",
		"Held:Int:80",
		"% Held:Percent:90",
		"Total:Int:80",
		"% Total:Percent:80",
		"On Time:Int:80",
		"% On Time:Percent:120",
		"Story Points:Int:150",
		"Score:Float:150",

	]

def get_summary_columns():
	return [
		"Issue:Link/Issue:150",
		"Status:Data:100",
		"Opening Date:Date:120",
		"Due Date:Date:120",
		"Resolution:Datetime:160",
		"Allocated To:Data:120",
		"Customer:Data:200",
		"Estimated Points:Int:150",
		"Subject:Data:400",
	]

def get_data(filters):
	ISSUE = frappe.qb.DocType("Issue")
	USR = frappe.qb.DocType("User")
	If = CustomFunction('IF', ['condition', 'if', 'else'])

	conditions = []

	if filters.get("from_date"):
		conditions.append(ISSUE.creation <= filters.get("from_date"))
	if filters.get("to_date"):
		conditions.append(ISSUE.creation <= filters.get("to_date"))

	old_issues = Query.from_(ISSUE).left_join(USR).on(
		(ISSUE.creation < filters.get("from_date"))&
		(ISSUE.resolver == USR.name)
	).select(
		USR.full_name,
		ConstantColumn(0).as_('open_issues'),
		fn.Sum( Case().when(ISSUE.status.isin(['Cancelled','Resolved', 'Closed']), 0).else_(1)).as_('old_open_issues'),
		ConstantColumn(0).as_('closed_issues'),
		ConstantColumn(0).as_('held_issues'),
		ConstantColumn(0).as_('total_story_points'),
		ConstantColumn(0).as_('on_time')
	).where( 
		(USR.enabled == 1)
	).groupby(USR.name)
	
	current  = Query.from_(USR).left_join(ISSUE).on(
		Criterion.all(conditions)
	).select(
		USR.full_name,
		fn.Sum(
			Case().when(ISSUE.status.isin(['Hold','Cancelled','Resolved', 'Closed']), 0).else_(1)
		).as_('open_issues'),
		ConstantColumn(0).as_('old_open_issues'),
		fn.Sum(
			Case().when(ISSUE.status.isin(['Resolved', 'Closed']), 1).else_(0)
		).as_('closed_issues'),
		fn.Sum(
			Case().when(ISSUE.status == 'Hold', 1).else_(0)
		).as_('held_issues'),
		fn.Sum(
			Case().when(ISSUE.estimated_points, ISSUE.estimated_points).else_(0)
		).as_('total_story_points'),
		fn.Sum(
			Case().when(ISSUE.due_date < ISSUE.resolution_date, 1	).else_(0)
		).as_('on_time'),
	).where((ISSUE.resolver == USR.name)&
		(USR.enabled == 1)  ).groupby(USR.name)

	query =  current if not filters.get("old_issues") else current + old_issues

	data = frappe.qb.from_(query).select(
		query.full_name,
		fn.Sum(query.open_issues).as_('open_issues'),
		fn.Sum(query.old_open_issues).as_('old_open_issues'),
		fn.Sum(query.closed_issues).as_('closed_issues'),
		fn.Sum(query.held_issues).as_('held_issues'),
		fn.Sum(query.total_story_points).as_('total_story_points'),
		fn.Sum(query.on_time).as_('on_time')
	).groupby(query.full_name).run(as_dict=True, debug=True )

	result = []
	total_issues  = sum([flt(d.open_issues) + flt(d.closed_issues) + flt(d.held_issues) + flt(d.old_open_issues) for d in data])
	total_story_points = sum([flt(d.total_story_points) for d in data])
	max_score = 5

	for d in data:
		total_row = flt(d.open_issues) + flt(d.closed_issues) + flt(d.held_issues) + flt(d.old_open_issues)
		per_ontime = flt((flt(d.on_time) / total_issues) * 100, 2) if total_issues else 0
		per_open = flt((flt(d.open_issues) / total_issues) * 100, 2) if total_issues else 0
		per_closed = flt((flt(d.closed_issues) / total_issues) * 100, 2) if total_issues else 0
		per_held = flt((flt(d.held_issues) / total_issues) * 100, 2) if total_issues else 0
		per_total = flt(((flt(d.open_issues) + flt(d.closed_issues) + flt(d.held_issues)) / total_issues) * 100, 2) if total_issues else 0
		score = flt((flt(d.on_time) / total_row) * max_score, 2) if total_row else 0
		if not total_row:
			continue

		result.append(
			(
				d.full_name,			#Employee
				d.old_open_issues,			#Old
				d.open_issues,			#Open
				per_open,  				#% Open
				d.closed_issues,		#Closed
				per_closed, 			#% Closed
				d.held_issues,			#Held			
				per_held,				#% Held
				total_row,				#Total
				per_total, 				#% Total
				d.on_time,				#On Time
				per_ontime,				#% On Time
				d.total_story_points,	#Story Points
				score,					#Score
			)
		)

	return result			

def get_summary_data(filters):
	ISSUE = frappe.qb.DocType("Issue")
	USR = frappe.qb.DocType("User")
	If = CustomFunction('IF', ['condition', 'if', 'else'])
	conditions = []

	if filters.get("from_date"):
		conditions.append(ISSUE.due_date >= filters.get("from_date"))
	if filters.get("to_date"):
		conditions.append(ISSUE.due_date <= filters.get("to_date"))
	if filters.get("developer"):
		conditions.append(ISSUE.resolver == filters.get("developer"))
	else:
		frappe.msgprint("Please select developer")

	
	current =  Query.from_(ISSUE).join(USR).on(
		(ISSUE.resolver == USR.name)&
		(USR.enabled == 1)
	).select(
		ISSUE.name,
		ISSUE.status,
		ISSUE.opening_date,
		ISSUE.due_date,
		ISSUE.resolution_date,
		USR.full_name,
		ISSUE.customer,
		ISSUE.estimated_points * 1,
		ISSUE.subject
	).where( Criterion.all(conditions) )

	old = Query.from_(ISSUE).join(USR).on(
		(ISSUE.resolver == USR.name)&
		(USR.enabled == 1)
	).select(
		ISSUE.name,
		ISSUE.status,
		ISSUE.opening_date,
		ISSUE.due_date,
		ISSUE.resolution_date,
		USR.full_name,
		ISSUE.customer,
		ISSUE.estimated_points * 1,
		ISSUE.subject
	).where(
		(ISSUE.resolver == filters.get("developer"))&
		(~ISSUE.status.isin(['Cancelled','Resolved', 'Closed']))&
		(ISSUE.due_date < filters.get("from_date")) 
	)
	query = current if not filters.get("old_issues") else current + old
	return frappe.qb.from_(query).select('*').orderby(query.due_date).run()

	
	