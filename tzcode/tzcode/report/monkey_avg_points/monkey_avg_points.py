# Copyright (c) 2024, Yefri Tavarez and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe


class Report(object):
    def __init__(self, filters) -> None:
        self.filters = filters
        self.columns = list()
        self.data = list()

    def run(self):
        self.setup_columns()
        self.setup_data()

        return self.columns, self.data

    def setup_columns(self):
        self.columns = [
            {
                "fieldname": "resolver",
                "label": "Resolver",
                "fieldtype": "Link",
                "options": "User",
                "width": 120,
            },
            {
                "fieldname": "resolver_name",
                "label": "Resolver Name",
                "fieldtype": "Data",
                "width": 180,
            },
            {
                "fieldname": "month",
                "label": "Month",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "total_points",
                "label": "Monthly Total Pts",
                "fieldtype": "Float",
                "width": 140,
            },
            {
                "fieldname": "issue_count",
                "label": "Issue Count",
                "fieldtype": "Int",
                "width": 120,
            },
            {
                "fieldname": "avg_points",
                "label": "Weekly AVG Pts",
                "fieldtype": "Float",
                "width": 140,
                "bold": 1,
            },
            {
                "fieldname": "goal_points",
                "label": "Goal Pts",
                "fieldtype": "Float",
                "width": 140,
                "bold": 1,
            },
            {
                "fieldname": "prev_week_points",
                "label": "Prev Week Pts",
                "fieldtype": "Float",
                "width": 140,
            },
            {
                "fieldname": "this_week_points",
                "label": "Last Week Pts",
                "fieldtype": "Float",
                "width": 140,
            },
        ]

    def setup_data(self):
        sql_conditions = self.get_sql_conditions()
        sql_query = self.get_sql_query(sql_conditions)

        out = frappe.db.sql(sql_query, as_dict=True)

        self.post_process_data(out)

        self.data = out

    def get_sql_conditions(self):
        conditions = list()

        # always on conditions
        conditions.append("""
            IfNull(resolver, "") != ""
        """)

        conditions.append("""
            workflow_state Not In (
                "Duplicated", "Closed"
            )
        """)

        conditions.append("""
            workflow_state In (
                "Ready for QA", "Code Quality Passed", "Awaiting Customer", "Completed"
            )
        """)

        # add filters
        date_based_on = self.get_filter("date_based_on")
        if starting_date := self.get_filter("starting_date"):
            conditions.append(f"{date_based_on} >= {starting_date!r}")

        if ending_date := self.get_filter("ending_date"):
            conditions.append(f"{date_based_on} <= {ending_date!r}")

        if resolver := self.get_filter("resolver"):
            conditions.append(f"resolver = {resolver!r}")

        if status := self.get_filter("status"):
            conditions.append(f"status = {status!r}")

        if workflow_states := self.get_filter("workflow_states"):
            # workflow_state comes in as a comma separated string
            workflow_state_list = workflow_states.split(",")
            
            # wrap each state with quotes
            workflow_state_list = [
                f"{state!r}" for state in workflow_state_list if state
            ]

            # join the list with commas
            workflow_states = ", ".join(workflow_state_list)

            # add the condition only if there is at least one state
            if workflow_states:
                conditions.append(f"workflow_state In ({workflow_states})")

        return " And ".join(conditions)

    def get_filter(self, key):
        return self.filters.get(key, None)

    def get_sql_query(self, sql_conditions):
        WEEKS_IN_MONTH = 4

        date_based_on = self.get_filter("date_based_on")

        return f"""
            Select
                issue.resolver As resolver,
                user.full_name As resolver_name,
                Concat_Ws(
                    "-", Year(issue.{date_based_on}), Month(issue.{date_based_on})
                ) As month,
                Sum(
                    issue.estimated_points
                ) As total_points,
                Sum(
                    issue.issue_count
                ) As issue_count,
                (
                    Sum(
                        issue.estimated_points
                    ) / {WEEKS_IN_MONTH}
                ) As avg_points,
                (
                    Sum(
                        issue.estimated_points * 2
                    ) / {WEEKS_IN_MONTH}
                ) As goal_points,
                (
                    {self.prev_week_points(sql_conditions, date_based_on)}
                ) As prev_week_points,
                (
                    {self.this_week_points(sql_conditions, date_based_on)}
                ) As this_week_points
            From (
                {self.main_data_query(sql_conditions, date_based_on)}
            ) As issue
            Inner Join
                tabUser As user
                    On
                        user.name = issue.resolver
            Where
                1 = 1
            Group By
                issue.resolver,
                Concat(
                    Year(issue.{date_based_on}), LPad( -- pad with 0
                        Month(issue.{date_based_on}), 2, 0
                    )
                )
        """

    def this_week_points(self, sql_conditions, date_based_on):
        return f"""
            Select
                Sum(
                    IfNull(estimated_points, 0)
                )
            From
                tabIssue
            Where
                {sql_conditions}
                And resolver = issue.resolver
                And
                YearWeek(
                    Date(
                        {date_based_on}
                    )
                ) = YearWeek(
                    Current_Date()
                )
        """

    def prev_week_points(self, sql_conditions, date_based_on):
        return f"""
            Select
                Sum(
                    IfNull(estimated_points, 0)
                )
            From
                tabIssue
            Where
                {sql_conditions}
                And 
                resolver = issue.resolver
                And
                YearWeek(
                    Date(
                        {date_based_on}
                    )
                ) = YearWeek(
                    Current_Date() - Interval 1 Week
                )
        """

    def main_data_query(self, sql_conditions, date_based_on):
        return f"""
            Select
                resolver,
                {date_based_on},
                Sum(
                    Cast(estimated_points As Int)
                ) As estimated_points,
                Sum(
                    If (
                        IfNull(estimated_points, "") = "",
                        0,
                        1
                    )
                ) As issue_count,
                workflow_state
            From
                tabIssue
            Where
                {sql_conditions}
            Group By
                resolver,
                YearWeek(
                    Date(
                        {date_based_on}
                    )
                )
        """

    def post_process_data(self, out):
        for row in out:
            self.update_month_col(row)

    def update_month_col(self, row):
        """Converts the month from YYYY-MM to MMM YYYY"""
        year, month = row.month.split("-")

        month = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")

        row.month = month.strftime("%b %Y") # e.g. Jan 2021

def execute(filters=None):
    report = Report(filters)
    return report.run()
