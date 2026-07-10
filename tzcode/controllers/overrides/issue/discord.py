# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import strip_html_tags

from typing import Dict

PUBLIC_URL_TEMPLATE = "{{ url }}/{{ doctype }}/{{ name }}?format={{ print_format|urlencode }}&key={{ key|urlencode }}"

client_manager = {
    "AMALOG SRL": "miguel.higuera@tzcode.tech",
    "LOGOMARCA": "miguel.higuera@tzcode.tech",
}

ticket_manager = "ticket@tzcode.tech"


def role_manager():
    from itops.discord.delivery import get_role_manager_map
    return get_role_manager_map()


def users_for_role(role_name):
    return role_manager().get(role_name, [])

# done here to avoid having to indent the whole thing
footer_template = """

Issue ID: {issue_id}
Description: {description:.140}...
Resolver: {resolver}
Edit Link: {issue_link}
Public Preview: {share_url}

>>> End of Message
"""

on_creation_msg_template = """
*{fullname}* has created a new ticket with workflow_state _{workflow_state}_ for client {customer_name}.
"""

# *{fullname}* has changed the workflow_state of {issue_id} to _{workflow_state}_.
ticket_ready_for_development_msg_template = """
A new ticket is Ready for Development and it has your name on it, literally.
"""

ticket_ready_for_development_without_resolver_msg_template = """
A new ticket is Ready for Development and has no resolver yet, it has almost your name on it, hurry up.
"""

ticket_ready_for_development_without_resolver_and_not_a_manager = """
*{fullname}* has marked as Ready for Development a ticket with no resolver.
"""

ticket_ready_for_development_with_resolver_and_not_a_manager = """
*{fullname}* has marked as Ready for Development (even though he is not a Support Manager)...
let's hope he knows what he is doing.
"""

ticket_marked_as_working_by_developer_msg_template = """
*{fullname}* has marked as Working a new ticket.
"""

ticket_marked_as_working_by_someone_else_msg_template = """
*{fullname}* has marked as Working a ticket that you were working on.
"""

ticket_marked_as_working_by_somebody_and_not_resolver_msg_template = """
*{fullname}* has marked as Working a ticket that has no resolver.
"""

ticket_marked_as_reworking_by_developer_msg_template = """
*{fullname}* has marked as Re-Working a ticket that was previously rejected. 
"""

ticket_remarked_as_reworking_by_someone_else_msg_template = """
*{fullname}* has started Re-Working a ticket that you were working on after it was first rejected. :thinking:
"""

ticket_remarked_as_working_by_somebody_and_not_resolver_msg_template = """
*{fullname}* has started Re-Working a ticket that has no resolver after it was first rejected. :thinking:
"""

ticket_placed_on_hold_by_non_manager_user = """
*{fullname}* has placed a ticket on hold. This is not a Support Manager. :thinking:
"""

ticket_placed_on_hold_for_developer = """
*{fullname}* has placed a ticket on hold for you. It's so sad :thinking:
"""

ticket_marked_as_forgotten_by_non_manager_user = """
*{fullname}* has marked a ticket as forgotten. This is not a Support Manager. :thinking:
"""

ticket_completed_msg_template = """
*{fullname}* has closed a ticket that was assigned to you. You got lucky. :sunglasses:
"""

ticket_completed_by_non_manager_msg_template = """
*{fullname}* has closed a ticket. Not sure why, but he is almost a Support Manager. :thinking:
"""

ticket_rejected_by_non_manager_msg_template = """
Roger, we have a problem... well, not really... *{fullname}* has rejected a ticket. Interesting! :thinking:
"""

ticket_rejected_msg_template = """
*{fullname}* has rejected a ticket that was assigned to you. You got unlucky. :sob:
"""

ticket_marked_as_qa_passed_by_non_manager_msg_template = """
*{fullname}* has marked a ticket as QA Passed. This is not a Support Manager. :thinking:
"""

ticket_marked_as_qa_passed_msg_template = """
*{fullname}* has marked a ticket as QA Passed that was assigned to you. You got lucky. :sunglasses:
"""

ticket_marked_as_ready_for_qa_msg_template = """
*{fullname}* has finally marked a ticket as Ready for QA. Yiiihaaaa! :tada:
"""

something_is_going_msg_template = """
*{fullname}* has done something to a ticket. I don't know what, but I am sure it is important.
"""


def trigger_discord_notifications(opts: Dict) -> None:
    """opts example: { "doc": doc, "is_new": True }"""
    doc = opts["doc"]

    try:
        is_new = opts["is_new"]
    except KeyError:
        is_new = False

    if is_new:
        # notify Support Managers
        notify_support_managers_on_new_tickets(doc)
        return # "New ticket, notify Support Managers"

    # if we made it this far off, that means this is NOT a NEW ticket
    db_doc = doc.get_doc_before_save()

    if not db_doc:
        return # "No previous version of the document, do nothing"

    if doc.workflow_state != db_doc.workflow_state:
        notify_of_workflow_state_change(db_doc, doc)


def notify_support_managers_on_new_tickets(doc):
    current_user = frappe.session.user
    # user_roles = frappe.get_roles()

    args = {
        "issue_id": doc.name,
        "customer_name": doc.customer,
        "fullname": frappe.utils.get_fullname(),
        "workflow_state": doc.workflow_state,
        "description": strip_html_tags(doc.description),
        "resolver": doc.get("resolver", default="N/A"),
        "workflow_state": doc.workflow_state,
        "issue_link": get_issue_link(doc.name),
        "share_url": get_share_url(doc.name),
    }

    if current_user == ticket_manager:
        args.update({
            "fullname": f"Somebody from -> {doc.customer}",
        })


    # if doc.workflow_state == "Pending":
    # 	"""Notify Support Managers of the new ticket"""
    # elif doc.workflow_state == "Ack":
    # 	"""Notify Support Managers of the new ticket"""
    # else:
    # 	"""Notify Support Managers of the new ticket"""

    for user in role_manager().get("Support Manager", []):
        if user == current_user:
            continue # don't notify the current user

        message = f"""
            {on_creation_msg_template.format(**args)}
            {footer_template.format(**args)}
        """

        notify_channel(
            user,
            message,
            context=args,
        )


def notify_of_workflow_state_change(before_save, doc):
    current_user = frappe.session.user
    user_roles = frappe.get_roles()

        # "issue_id": doc.name,
        # "customer_name": doc.customer,
        # "fullname": frappe.utils.get_fullname(),
        # "workflow_state": doc.workflow_state,
        # "description": strip_html_tags(doc.description),
        # "workflow_state": doc.workflow_state,
        # "issue_link": get_issue_link(doc.name),
        # "share_url": get_share_url(doc.name),

    args = {
        "issue_id": doc.name,
        "customer_name": doc.customer,
        "description": strip_html_tags(doc.description),
        "fullname": frappe.utils.get_fullname(),
        "workflow_state": doc.workflow_state,
        "resolver": doc.get("resolver", default="N/A"),
        "workflow_state": doc.workflow_state,
        "issue_link": get_issue_link(doc.name),
        "share_url": get_share_url(doc.name),
    }

    def notify(user, message):
        notify_channel(user, message, context=args)

    if doc.workflow_state == "Ready for Development":
        if "Support Manager" in user_roles:
            if doc.resolver:
                """Notify Developer of the workflow_state change"""

                message = f"""
                    {ticket_ready_for_development_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """

                notify(
                    doc.resolver,
                    message,
                )
            else:
                """Notify Developer Team of the workflow_state change"""
                role_list = list()
                role_list.extend(users_for_role("Developer"))
                role_list.extend(users_for_role("Developer Junior"))

                for user in role_list:
                    message = f"""
                        {ticket_ready_for_development_without_resolver_msg_template.format(**args)}
                        {footer_template.format(**args)}
                    """

                    notify(
                        user,
                        message,
                    )
        else:
            """Notify Support Managers of the workflow_state change"""
            if not doc.resolver:
                for user in users_for_role("Support Manager"):
                    if user == current_user:
                        continue # don't notify the current user (I know this is unlikely)

                    notify(user, f"""
                        {ticket_ready_for_development_without_resolver_and_not_a_manager.format(**args)}
                        {footer_template.format(**args)}                        
                    """)
            else:
                users = list()
                users.extend(users_for_role("Support Manager"))
                users.extend(users_for_role("Developer"))

                for user in users:
                    if user == current_user:
                        continue # don't notify the current user

                    notify(user, f"""
                        {ticket_ready_for_development_with_resolver_and_not_a_manager.format(**args)}
                        {footer_template.format(**args)}
                    """)
    elif doc.workflow_state == "Working":
        if before_save.workflow_state == "Ready for Development":
            """Notify Support Managers of the workflow_state change"""
            if doc.resolver:
                """Notify Developer of the workflow_state change"""
                if doc.resolver != current_user:
                    notify(doc.resolver, f"""
                        {ticket_marked_as_working_by_someone_else_msg_template.format(**args)}
                        {footer_template.format(**args)}
                    """)

                    if current_user not in users_for_role("Support Manager"):
                        for user in users_for_role("Support Manager"):
                            if user == current_user:
                                continue

                            notify(user, f"""
                                {ticket_marked_as_working_by_someone_else_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
                else:
                    """Notify Managers of ticket acquired by resolver"""
                    if current_user not in users_for_role("Support Manager"):
                        for user in users_for_role("Support Manager"):
                            if user == current_user:
                                continue

                            notify(user, f"""
                                {ticket_marked_as_working_by_developer_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
            else:
                """Notify Managers of ticket started without resolver"""
                if current_user not in users_for_role("Support Manager"):
                    for user in users_for_role("Support Manager"):
                        if user == current_user:
                            continue

                        notify(user, f"""
                            {ticket_marked_as_working_by_somebody_and_not_resolver_msg_template.format(**args)}
                            {footer_template.format(**args)}
                        """)
        elif before_save.workflow_state == "Code Quality Rejected":
            if doc.resolver:
                """Notify Developer of the workflow_state change"""
                if doc.resolver != current_user:
                    notify(doc.resolver, f"""
                        {ticket_remarked_as_reworking_by_someone_else_msg_template.format(**args)}
                        {footer_template.format(**args)}
                    """)

                    if current_user not in users_for_role("Support Manager"):
                        for user in users_for_role("Support Manager"):
                            if user == current_user:
                                continue

                            notify(user, f"""
                                {ticket_remarked_as_reworking_by_someone_else_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
                else:
                    """Notify Managers of ticket re-acquired by resolver"""
                    if current_user not in users_for_role("Support Manager"):
                        for user in users_for_role("Support Manager"):
                            if user == current_user:
                                continue

                            notify(user, f"""
                                {ticket_marked_as_reworking_by_developer_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
            else:
                """Notify Managers of ticket started without resolver"""
                if current_user not in users_for_role("Support Manager"):
                    for user in users_for_role("Support Manager"):
                        if user == current_user:
                            continue

                        notify(user, f"""
                            {ticket_remarked_as_working_by_somebody_and_not_resolver_msg_template.format(**args)}
                            {footer_template.format(**args)}
                        """)
        elif before_save.workflow_state == "On Hold":
            """Notify the developer that the ticket is back to Working"""
            if doc.resolver and doc.resolver != current_user:
                notify(doc.resolver, f"""
                    {ticket_marked_as_working_by_someone_else_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)


    elif doc.workflow_state == "On Hold":
        """Notify Support Managers of the workflow_state change"""
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {ticket_placed_on_hold_by_non_manager_user.format(**args)}
                    {footer_template.format(**args)}
                """)
        else:
            if doc.resolver and doc.resolver != current_user:
                notify(doc.resolver, f"""
                    {ticket_placed_on_hold_for_developer.format(**args)}
                    {footer_template.format(**args)}
                """)

    elif doc.workflow_state == "Forgotten":
        """Notify Support Managers of the workflow_state change"""
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {ticket_marked_as_forgotten_by_non_manager_user.format(**args)}
                    {footer_template.format(**args)}
                """)
    elif doc.workflow_state == "Completed":
        # if "Implementer Team" not in user_roles:
        #     """Notify Support Managers of the workflow_state change"""
        # else:
        #     """Notify the Developer of the completion"""

        # I would say, maybe Developer and guests are the only people not allow to complete a ticket.
        # so, if the user is not a Support Manager, then notify the Support Managers
        # and besides that, whether or not the ticket was not closed by a Manager we will inform the 
        # Developer of the completion (unless he is the one closing the ticket)
        
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {ticket_completed_by_non_manager_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        if doc.resolver and doc.resolver != current_user:
            notify(doc.resolver, f"""
            {ticket_completed_msg_template.format(**args)}
            {footer_template.format(**args)}
            """)
    elif doc.workflow_state == "Code Quality Rejected":
        """Notify Developer of the workflow_state change"""
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {ticket_rejected_by_non_manager_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        if doc.resolver and doc.resolver != current_user:
            notify(doc.resolver, f"""
            {ticket_rejected_msg_template.format(**args)}
            {footer_template.format(**args)}
            """)
    elif doc.workflow_state == "Code Quality Passed":
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {ticket_marked_as_qa_passed_by_non_manager_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        if doc.resolver and doc.resolver != current_user:
            notify(doc.resolver, f"""
            {ticket_marked_as_qa_passed_msg_template.format(**args)}
            {footer_template.format(**args)}
            """)
    elif doc.workflow_state == "Ready for QA":
        """Notify Support Managers of the workflow_state change"""
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {ticket_marked_as_ready_for_qa_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)
    else:
        """Notify Support Managers of the workflow_state change"""
        if current_user not in users_for_role("Support Manager"):
            for user in users_for_role("Support Manager"):
                notify(user, f"""
                    {something_is_going_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        
def get_issue_link(name):
    from itops.discord.settings import get_site_url
    return f"{get_site_url()}/app/issue/{name}"


def notify_channel(user, message, context=None):
    from itops.discord.delivery import send_issue_notification
    send_issue_notification(user, message, context=context)



def get_share_url(name):
    from itops.discord.settings import get_site_url
    doctype = "Issue"
    doc = frappe.get_doc(doctype, name)

    key = doc.get_document_share_key()

    opts = {
        "url": get_site_url(),
        "doctype": doctype,
        "name": name,
        "print_format": "Issue",
        "key": key,
    }

    return frappe.render_template(
        PUBLIC_URL_TEMPLATE, opts
    )
