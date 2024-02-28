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
	elif filters.get("type") == "Timesheet":
		return get_timesheet_columns(filters), get_timesheet_data(filters)
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
			"Duration:Float:140",
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
			"Hours:Float:100" if  dashboard else "Hours:Float:100",
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
			"Hours:Float:100",
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
		ISSUE.workflow_state.isin(['Ready for QA', 'Code Quality Passed', 'Closed', 'Completed'])
	]

	hours_dashboard = Query.from_(TS).join(TSD).on(TS.name == TSD.parent).join(EMP).on(TS.employee == EMP.name).select(
		fn.Sum(TSD.hours).as_('hours')
	).where(
		(TSD.parenttype == 'Timesheet')&
		(TSD.issue == ISSUE.name)&
		(EMP.user_id == fn.Coalesce(ISSUE.resolver, '-'))
	)

	hours_report = Query.from_(TS).join(TSD).on(TS.name == TSD.parent).join(EMP).on(TS.employee == EMP.name).select(
		fn.Sum(TSD.hours).as_('hours')
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


def get_implementation_columns(filters):
	pass


def get_implementation_data(filters):
	pass


def get_timesheet_columns(filters):
	if filters.get("summary"):
		if filters.get("group_by") == "Developer":
			return [
				"Employee:Data:180",
				"Hours:Float:100",
				"Points:Int:100",
				"Productivity:Data:100",
			]
		
		if filters.get("group_by") == "Issue":
			return [
				"Employee:Data:180",
				"Timesheet:Link/Timesheet:130",
				"Issue:Link/Issue:130",
				"Duration:Duration:120",
				"Hours:Float:100",
				"Points:Int:100",
				"Workflow State:Data:175",
				"Subject:Data:1200",
			]
	else:
		return [
			"Employee:Data:180",
			"Timesheet:Link/Timesheet:130",
			"From Time:Datetime:160",
			"To Time:Datetime:160",
			"Duration:Duration:120",
			"Hours:Float:100",
			"Issue:Link/Issue:130",
			"State:Data:175",
			"Points:Data:70",
			"Customer:Data:200",
			"Subject:Data:1200",
		]

def get_timesheet_data(filters):
	from_date = filters.get("from_date") or str(week_start())
	to_date = filters.get("to_date") or str(week_end())

	from_time = from_date + " 00:00:00"
	to_time = to_date + " 23:59:59"

	current_condition = [
		TSD.from_time >= from_time,
		TSD.to_time <= to_time,
		TS.docstatus == 1
	]
	if filters.get("employee"):
		current_condition.append(TS.employee == filters.get("employee"))

	if filters.get("summary"):
		query = Query.from_(TS).join(TSD).on(
			TS.name == TSD.parent
		).join(ISSUE).on(
			TSD.issue == ISSUE.name
		).join(EMP).on(
			EMP.name == TS.employee
		).select(
			EMP.name.as_('employee'),
			EMP.employee_name,
			TS.name.as_('timesheet'),
			ISSUE.name.as_('issue'),
			ISSUE.workflow_state,
			ISSUE.subject,
			ISSUE.estimated_points,
			fn.Sum(TSD.hours).as_('hours'),
			fn.Sum(ISSUE.estimated_points * 1).as_('points')
		).where(
			Criterion.all(current_condition)
		)
		frappe.errprint(query.get_sql().replace('"', '`'))
		
		if filters.get("group_by") == "Issue":
			query = query.groupby(EMP.name, ISSUE.name)
		
		if filters.get("group_by") == "Developer":
			query = query.groupby(EMP.name)
		
		data = frappe.qb.from_(query).select('*').run(as_dict=True, debug=True)
		total_points = sum([flt(row.points) for row in data])
		result = []
		for row in data:
			if filters.get("group_by") == "Developer":
				productivity  = flt((row.points / total_points) * 100, 2)
				points = get_total_point_per_employee(row.employee, from_time, to_time)
				result.append(
					(
						row.employee_name,
						row.hours,
						points,
						f"{productivity}%"
					)
				)
			if filters.get("group_by") == "Issue":
				result.append(
					(
						row.employee_name,
						row.timesheet,
						row.issue,
						row.issue,
						row.hours * 3600,
						row.hours,
						row.estimated_points,
						row.workflow_state,
						row.subject
					)
				)
		
		return result			
	
	else:
		return frappe.qb.from_(TS).join(TSD).on(
			TS.name == TSD.parent
		).join(ISSUE).on(
			TSD.issue == ISSUE.name
		).join(EMP).on(
			EMP.name == TS.employee
		).select(
			EMP.employee_name,
			TS.name,
			TSD.from_time,
			TSD.to_time,
			TSD.hours * 3600,
			TSD.hours,
			ISSUE.name,
			ISSUE.workflow_state,
			ISSUE.estimated_points,
			ISSUE.customer,
			ISSUE.subject
		).where(
			Criterion.all(current_condition)
		).run(debug=False)

def get_total_point_per_employee(employee, from_time, to_time):
	tickets = Query.from_(TS).join(TSD).on(
		TS.name == TSD.parent
	).select(TSD.issue).where(
		(Criterion.all([
			TSD.from_time >= from_time,
			TSD.to_time <= to_time,
			TS.employee == employee,
			TS.docstatus == 1
		]))
	).distinct()
	
	query = frappe.qb.from_(ISSUE).select(
		fn.Sum(ISSUE.estimated_points * 1).as_('points')
	).where(
		ISSUE.name.isin(tickets)
	).run(as_dict=True, debug=False)

	return query[0].points or 0