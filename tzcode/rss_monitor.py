# -*- coding: utf-8 -*-
import feedparser
import frappe
import requests

def send_telegram_message(text, settings):
    url = f"https://api.telegram.org/bot{settings.get_password('bot_token')}/sendMessage"
    data = {"chat_id": settings.chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        frappe.log_error(f"Telegram message failed: {e}")

@frappe.whitelist()
def check_upwork_feed():
    settings = frappe.get_doc("Tz Settings")
    if settings.disabled:
        return
    feed = feedparser.parse(settings.feed_url)
    if not feed.entries:
        return

    last_saved = settings.last_entry or ""
    new_entries = []

    for entry in feed.entries:
        if entry.id == last_saved:
            break
        new_entries.append(entry)

    if new_entries:
        settings.db_set("last_entry", new_entries[0].id)

    for entry in reversed(new_entries, settings):  # oldest first
        msg = f"<b>{entry.title}</b>\n{entry.link}"
        send_telegram_message(msg)