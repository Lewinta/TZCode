# Copyright (c) 2023, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.query_builder import CustomFunction, Criterion, Case, Query, functions as fn
from frappe.query_builder.custom import ConstantColumn
from tzcode.utils.utils import week_start, week_end

ISSUE = frappe.qb.DocType("Issue")
USER = frappe.qb.DocType("User")
TS = frappe.qb.DocType("Timesheet")
TSD = frappe.qb.DocType("Timesheet Detail")
EMP = frappe.qb.DocType("Employee")

def execute(filters=None):
	if filters.get("type") == "Historical":	
		return get_historical_columns(filters), get_historical_data(filters)
	elif filters.get("type") == "Development":
		return get_development_columns(filters), get_development_data(filters)
	
	elif filters.get("type") == "Implementation":
		pass
	else:
		return [], []


def get_historical_columns(filters):
	if filters.get("summary"):
		return [
			"Old:Int:90",
			"Current:Int:90",
			"Held:Int:90",
			"Open:Int:90",
			"Open + Held:Int:120",
			"Delivered:Int:100",
			"Closed:Int:90",
		]
	else:
		return [
			"Issue:Link/Issue:130",
			"Remote Ref.:Data:130",
			"Status:Data:80",
			"State:Data:175",
			"Opening Date:Date:120",
			"Due Date:Date:100",
			"Assigned On:Datetime:160",
			"Delivered On:Datetime:160",
			"Duration:Duration:140",
			"Resolution:Datetime:160",
			"Assigned:Data:120",
			"Approver:Data:120",
			"Customer:Data:200",
			"Hours:Float:70",
			"Points:Int:70",
			"Subject:Data:1200",
		]
	

def get_historical_data(filters):
	from_time = filters.get("from_date") + " 00:00:00"
	to_time = filters.get("to_date") + " 23:59:59"
	workflow_state = filters.get("workflow_state")
	employee = filters.get("employee")
	current_condition = [
		ISSUE.creation >= from_time,
		ISSUE.creation <= to_time
	]
	current_closed_condition = [
		ISSUE.delivered_for_qa >= from_time,
		ISSUE.delivered_for_qa <= to_time,
		ISSUE.status.isin(['Resolved', 'Closed']),
		ISSUE.workflow_state != 'Duplicated',
	]
	old_condition =  [
		~ISSUE.status.isin(['Cancelled','Resolved', 'Closed']),
	 	ISSUE.creation < filters.get("from_date")
	]
	current_delivered = [
		ISSUE.delivered_for_qa >= from_time,
		ISSUE.delivered_for_qa <= to_time,
		ISSUE.workflow_state.isin(['Ready for QA', 'Code Quality Passed'])
	]
	
	if workflow_state:
		current_condition.append(ISSUE.workflow_state == workflow_state)
		current_closed_condition.append(ISSUE.workflow_state == workflow_state)
		current_delivered.append(ISSUE.workflow_state == workflow_state)
	
	if employee:
		current_condition.append(ISSUE.resolver == employee)
		current_closed_condition.append(ISSUE.resolver == employee)
		old_condition.append(employee == fn.Coalesce(ISSUE.resolver, '-'))
		current_delivered.append(ISSUE.resolver == employee)

	resolver = Query.from_(USER).select(USER.full_name).where(USER.name == fn.Coalesce(ISSUE.resolver, '-'))
	approver = Query.from_(USER).select(USER.full_name).where(USER.name == fn.Coalesce(ISSUE.approver, '-'))
	hours = Query.from_(TS).join(TSD).on(TS.name == TSD.parent).join(EMP).on(TS.employee == EMP.name).select(
		fn.Sum(TSD.hours).as_('hours')
	).where(
		(TSD.parenttype == 'Timesheet')&
		(TSD.issue == ISSUE.name)&
		(EMP.user_id == fn.Coalesce(ISSUE.resolver, '-'))
	)
	
	
	if filters.get("summary"):
		return frappe.qb.from_(ISSUE).select(
			fn.Sum(Case().when(Criterion.all(old_condition), 1).else_(0)).as_('old_open_issues'),
			fn.Sum(Case().when(Criterion.all(current_condition), 1).else_(0)).as_('current_open_issues'),
			fn.Sum(Case().when(ISSUE.status == 'Hold', 1).else_(0)).as_('held_issues'),
			fn.Sum(Case().when(~ISSUE.status.isin(['Resolved', 'Closed', 'Hold']), 1).else_(0)).as_('open_issues'),
			fn.Sum(Case().when(~ISSUE.status.isin(['Resolved', 'Closed']), 1).else_(0)).as_('open_and_held_issues'),
			fn.Sum(Case().when(Criterion.all(current_delivered), 1).else_(0)).as_('current_delivered'),
			fn.Sum(Case().when(Criterion.all(current_closed_condition), 1).else_(0)).as_('closed_issues'),
		).run(debug=False)
	else:
		fields = [
			ISSUE.name,
			ISSUE.remote_reference,
			ISSUE.status,
			ISSUE.workflow_state,
			ISSUE.opening_date,
			ISSUE.due_date,
			ISSUE.assignation_date,
			ISSUE.delivered_for_qa,
			(ISSUE.delivered_for_qa - ISSUE.assignation_date).as_('time_to_resolution'),
			ISSUE.resolution_date,
			resolver,
			approver,
			ISSUE.customer,
			hours,
			ISSUE.estimated_points * 1,
			ISSUE.subject
		]
		
		if workflow_state:
			all_open =  Query.from_(ISSUE).select(*fields).where( ~ISSUE.status.isin(['Resolved', 'Closed', 'Hold'])& (ISSUE.workflow_state == workflow_state) )
		else:
			all_open =  Query.from_(ISSUE).select(*fields).where( ~ISSUE.status.isin(['Resolved', 'Closed', 'Hold']) )
		current_issues =  Query.from_(ISSUE).select(*fields).where( Criterion.all(current_condition) )
		current_closed =  Query.from_(ISSUE).select(*fields).where( Criterion.all(current_closed_condition) )
	
		return frappe.qb.from_(all_open + current_issues + current_closed).select('*').run(debug=False)
		

def get_development_columns(filters):
	dashboard = filters.get("dashboard") 
		
	if filters.get("summary"):
		return [
			"Employee:Data:130",
			"Hours:Float:100" if  dashboard else "Hours:Duration:100",
			"Delivered:Int:100",
			"Points:Int:100",
		]
	else:
		return [
			"Employee:Data:130",
			"Issue:Link/Issue:130",
			"Status:Data:80",
			"State:Data:175",
			"Delivered On:Datetime:160",
			"Customer:Data:200",
			"Hours:Duration:100",
			"Points:Int:70",
			"Subject:Data:1200",
		]


def get_development_data(filters):
	from_date = filters.get("from_date") or str(week_start())
	to_date = filters.get("to_date") or str(week_end())

	dashboard = filters.get("dashboard")
	
	if not filters.get("from_date") or not filters.get("to_date"):
		dashboard = True
	
	from_time = from_date + " 00:00:00"
	to_time = to_date + " 23:59:59"
	
	resolver = Query.from_(USER).select(USER.full_name).where(USER.name == fn.Coalesce(ISSUE.resolver, '-'))
	
	current_condition = [
		ISSUE.delivered_for_qa >= from_time,
		ISSUE.delivered_for_qa <= to_time,
		ISSUE.workflow_state.isin(['Ready for QA', 'Code Quality Passed', 'Closed'])
	]

	hours_dashboard = Query.from_(TS).join(TSD).on(TS.name == TSD.parent).join(EMP).on(TS.employee == EMP.name).select(
		fn.Sum(TSD.hours).as_('hours')
	).where(
		(TSD.parenttype == 'Timesheet')&
		(TSD.issue == ISSUE.name)&
		(EMP.user_id == fn.Coalesce(ISSUE.resolver, '-'))
	)

	hours_report = Query.from_(TS).join(TSD).on(TS.name == TSD.parent).join(EMP).on(TS.employee == EMP.name).select(
		fn.Sum(TSD.hours * 3600).as_('hours')
	).where(
		(TSD.parenttype == 'Timesheet')&
		(TSD.issue == ISSUE.name)&
		(EMP.user_id == fn.Coalesce(ISSUE.resolver, '-'))
	)

	hours = hours_dashboard if dashboard else hours_report

	if filters.get("summary"):
		return frappe.qb.from_(ISSUE).select(
			resolver,
			fn.Sum(hours),	
			fn.Count(1),
			fn.Sum(ISSUE.estimated_points * 1)
		).where(
			Criterion.all(current_condition)
		).groupby(ISSUE.resolver).run(debug=False)
	else:
		return frappe.qb.from_(ISSUE).select(
			resolver,
			ISSUE.name,
			ISSUE.status,
			ISSUE.workflow_state,
			ISSUE.delivered_for_qa,
			ISSUE.customer,
			hours,
			ISSUE.estimated_points * 1,
			ISSUE.subject
		).where(
			Criterion.all(current_condition)
		).run(debug=False)

def get_implementarion_columns(filters):
	pass


def get_implementarion_data(filters):
	pass
	