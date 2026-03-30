import frappe 
from hrms.hr.doctype.interview_feedback.interview_feedback import InterviewFeedback as HRMSInterviewFeedback

class InterviewFeedback(HRMSInterviewFeedback):
    @property
    def description(self):
        if not self.skill:
            return None
        return frappe.get_value("Skill", self.skill, "description")