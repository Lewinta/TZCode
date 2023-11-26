# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import requests

import frappe
from frappe.utils import strip_html_tags


from typing import Dict

# this should be done in a doctype
client_manager = {
    "AMALOG SRL": "miguel.higuera@tzcode.tech",
    "LOGOMARCA": "miguel.higuera@tzcode.tech",
}

url_template = "https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"

# this should be done in a doctype
office_manager = {
    "brenorramirez@tzcode.tech": ("1173831622034997308", "F7CH65yxoQLbfh_wIIxR22ai-f4aRDqwY-pe0_Ou1tDvY2bRCM3-nk5_1KMQ1Vws_sPZ"),
    "isauraperez@tzcode.tech": ("1173834963901218858", "v8ZnfDj0Nl3P2YQrxZLGy9sBFdwbeGJC1xGWDJxixxEWYhecJhCmU410ixGkenOKJKpz"),
    "lewinvillar@tzcode.tech": ("1173831452983566446", "WLAQ0hmdZ65olPGLghMzLLAOW7lNp3siSphMXgDw1aUhPgb5L2idI1B7br300LorAKqn"),
    "miguel.higuera@tzcode.tech": ("1173831313652989962", "i6iOvOCy_MQVvqdzV3pAAordyGg2jHG_Ore8AIie_3DgoTbMnW927TyWhTpjwKrVuzy0"),
    "rainierpolanco@tzcode.tech": ("1173830877885767751", "v2O77CNSqYkvCWy8epTziOqh74KyiT4JpzoeO40JehbGVQFGT6BV6WayEIZSFR5EUMnq"),
    "reyferreras@tzcode.tech": ("1173830539648716851", "3geA0iLo8e-95OP7AD_6zYSgtU22FCq1iFwsqHcJZnQ9UXvCcsTcuoeu-3hppt_J6Nsb"),
    "walquiriapena@tzcode.tech": ("1173834963901218858", "v8ZnfDj0Nl3P2YQrxZLGy9sBFdwbeGJC1xGWDJxixxEWYhecJhCmU410ixGkenOKJKpz"),
    "yefritavarez@tzcode.tech": ("1173704570770305084", "JW1kD0WWmPSdyOqQ7xGoJXcOs8NBkWQLcAzEMJbFvzBC3qEBdBP2dEMhY9B77RBLc4uj"),
}

# this should be done in a doctype
role_manager = {
    "Support Manager": {
        "lewinvillar@tzcode.tech",
        "yefritavarez@tzcode.tech",
    },
    "Implementer Team": {
        "brenorramirez@tzcode.tech",
    },
    "Developer": {
        "miguel.higuera@tzcode.tech",
    },
    "Developer Junior": {
        "rainierpolanco@tzcode.tech",
        "reyferreras@tzcode.tech",
    },
    "Accounting Team": {
        "isauraperez@tzcode.tech",
        "walquiriapena@tzcode.tech",
    }
}

ticket_manager = "ticket@tzcode.tech"

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

    for user in role_manager["Support Manager"]:
        if user == current_user:
            continue # don't notify the current user

        message = f"""
            {on_creation_msg_template.format(**args)}
            {footer_template.format(**args)}
        """

        notify_channel(
            user,
            message,
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

    if doc.workflow_state == "Ready for Development":
        if "Support Manager" in user_roles:
            if doc.resolver:
                """Notify Developer of the workflow_state change"""
                
                message = f"""
                    {ticket_ready_for_development_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """

                notify_channel(
                    doc.resolver,
                    message,
                )
            else:
                """Notify Developer Team of the workflow_state change"""
                role_list = list()
                role_list.extend(role_manager["Developer"])
                role_list.extend(role_manager["Developer Junior"])

                for user in role_list:
                    message = f"""
                        {ticket_ready_for_development_without_resolver_msg_template.format(**args)}
                        {footer_template.format(**args)}
                    """

                    notify_channel(
                        user,
                        message,
                    )
        else:
            """Notify Support Managers of the workflow_state change"""
            if not doc.resolver:
                for user in role_manager["Support Manager"]:
                    if user == current_user:
                        continue # don't notify the current user (I know this is unlikely)

                    notify_channel(user, f"""
                        {ticket_ready_for_development_without_resolver_and_not_a_manager.format(**args)}
                        {footer_template.format(**args)}                        
                    """)
            else:
                users = list()
                users.extend(role_manager["Support Manager"])
                users.extend(role_manager["Developer"])

                for user in users:
                    if user == current_user:
                        continue # don't notify the current user

                    notify_channel(user, f"""
                        {ticket_ready_for_development_with_resolver_and_not_a_manager.format(**args)}
                        {footer_template.format(**args)}
                    """)
    elif doc.workflow_state == "Working":
        if before_save.workflow_state == "Ready for Development":
            """Notify Support Managers of the workflow_state change"""
            if doc.resolver:
                """Notify Developer of the workflow_state change"""
                if doc.resolver != current_user:
                    notify_channel(doc.resolver, f"""
                        {ticket_marked_as_working_by_someone_else_msg_template.format(**args)}
                        {footer_template.format(**args)}
                    """)

                    if current_user not in role_manager["Support Manager"]:
                        for user in role_manager["Support Manager"]:
                            if user == current_user:
                                continue

                            notify_channel(user, f"""
                                {ticket_marked_as_working_by_someone_else_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
                else:
                    """Notify Managers of ticket acquired by resolver"""
                    if current_user not in role_manager["Support Manager"]:
                        for user in role_manager["Support Manager"]:
                            if user == current_user:
                                continue

                            notify_channel(user, f"""
                                {ticket_marked_as_working_by_developer_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
            else:
                """Notify Managers of ticket started without resolver"""
                if current_user not in role_manager["Support Manager"]:
                    for user in role_manager["Support Manager"]:
                        if user == current_user:
                            continue

                        notify_channel(user, f"""
                            {ticket_marked_as_working_by_somebody_and_not_resolver_msg_template.format(**args)}
                            {footer_template.format(**args)}
                        """)
        elif before_save.workflow_state == "Code Quality Rejected":
            if doc.resolver:
                """Notify Developer of the workflow_state change"""
                if doc.resolver != current_user:
                    notify_channel(doc.resolver, f"""
                        {ticket_remarked_as_reworking_by_someone_else_msg_template.format(**args)}
                        {footer_template.format(**args)}
                    """)

                    if current_user not in role_manager["Support Manager"]:
                        for user in role_manager["Support Manager"]:
                            if user == current_user:
                                continue

                            notify_channel(user, f"""
                                {ticket_remarked_as_reworking_by_someone_else_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
                else:
                    """Notify Managers of ticket re-acquired by resolver"""
                    if current_user not in role_manager["Support Manager"]:
                        for user in role_manager["Support Manager"]:
                            if user == current_user:
                                continue

                            notify_channel(user, f"""
                                {ticket_marked_as_reworking_by_developer_msg_template.format(**args)}
                                {footer_template.format(**args)}
                            """)
            else:
                """Notify Managers of ticket started without resolver"""
                if current_user not in role_manager["Support Manager"]:
                    for user in role_manager["Support Manager"]:
                        if user == current_user:
                            continue

                        notify_channel(user, f"""
                            {ticket_remarked_as_working_by_somebody_and_not_resolver_msg_template.format(**args)}
                            {footer_template.format(**args)}
                        """)
        elif before_save.workflow_state == "On Hold":
            """Notify the developer that the ticket is back to Working"""
            if doc.resolver and doc.resolver != current_user:
                notify_channel(doc.resolver, f"""
                    {ticket_marked_as_working_by_someone_else_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)


    elif doc.workflow_state == "On Hold":
        """Notify Support Managers of the workflow_state change"""
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
                    {ticket_placed_on_hold_by_non_manager_user.format(**args)}
                    {footer_template.format(**args)}
                """)
        else:
            if doc.resolver and doc.resolver != current_user:
                notify_channel(doc.resolver, f"""
                    {ticket_placed_on_hold_for_developer.format(**args)}
                    {footer_template.format(**args)}
                """)

    elif doc.workflow_state == "Forgotten":
        """Notify Support Managers of the workflow_state change"""
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
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
        
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
                    {ticket_completed_by_non_manager_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        if doc.resolver and doc.resolver != current_user:
            notify_channel(doc.resolver, f"""
            {ticket_completed_msg_template.format(**args)}
            {footer_template.format(**args)}
            """)
    elif doc.workflow_state == "Code Quality Rejected":
        """Notify Developer of the workflow_state change"""
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
                    {ticket_rejected_by_non_manager_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        if doc.resolver and doc.resolver != current_user:
            notify_channel(doc.resolver, f"""
            {ticket_rejected_msg_template.format(**args)}
            {footer_template.format(**args)}
            """)
    elif doc.workflow_state == "Code Quality Passed":
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
                    {ticket_marked_as_qa_passed_by_non_manager_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        if doc.resolver and doc.resolver != current_user:
            notify_channel(doc.resolver, f"""
            {ticket_marked_as_qa_passed_msg_template.format(**args)}
            {footer_template.format(**args)}
            """)
    elif doc.workflow_state == "Ready for QA":
        """Notify Support Managers of the workflow_state change"""
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
                    {ticket_marked_as_ready_for_qa_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)
    else:
        """Notify Support Managers of the workflow_state change"""
        if current_user not in role_manager["Support Manager"]:
            for user in role_manager["Support Manager"]:
                notify_channel(user, f"""
                    {something_is_going_msg_template.format(**args)}
                    {footer_template.format(**args)}
                """)

        
def get_issue_link(name):
    # doctype = "Issue"
    # link_name = f"{doctype}: {name}"
    # return frappe.utils.get_link_to_form(doctype, name, link_name)

    return f"https://bo.tzcode.tech/app/issue/{name}"


def notify_channel(user, message):
    webhook_id, webhook_token = office_manager[user]
    url = url_template.format(
        webhook_id=webhook_id,
        webhook_token=webhook_token,
    )

    body = {
        "content": message,
    }

    response = requests.post(url, json=body)

    return response.status_code == 204


def get_share_url(name):
    doctype = "Issue"
    doc = frappe.get_doc(doctype, name)

    key = doc.get_document_share_key()
    return f"https://bo.tzcode.tech/issue/{name}?key={key}"
