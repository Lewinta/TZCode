# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import os
import time

import frappe


LOCK_FILE = "create_bulk_issue.lock"


def lock_exists():
	# check to see if the lock exists

	# return True if the lock exists
	# return False if the lock does not exist
	
	return os.path.exists(LOCK_FILE)


def queue_after_5_secs(
    method, subject, status, customer, raised_by,
	remote_reference, priority, description
):
	# will retry the execution of the method
	# after 5 seconds if the lock exists
	# and the method is queued
	time.sleep(5)

	frappe.enqueue(
		method,
		subject=subject,
		status=status,
		customer=customer,
		raised_by=raised_by,
		remote_reference=remote_reference,
		priority=priority,
		description=description,
		enqueue_after_commit=True,
	)


def create_lock(hsh):
	# create the lock file
	# to prevent the execution of the method
	# by another process
	with open(LOCK_FILE, "w") as lock:
		lock.write(hsh)

	# in another thread, let's wait for 5 seconds
	# and then remove the lock file
	# this is just in case the method fails to remove
	# the lock file after execution
	remove_lock_after_5_secs(hsh)


def remove_lock_after_5_secs(hsh):
	frappe.enqueue(
		_remove_lock_after_5_secs,
		hsh=hsh,
		enqueue_after_commit=True,
	)


def _remove_lock_after_5_secs(hsh):
	time.sleep(5)
	remove_lock(hsh)


def remove_lock(hsh):
	# only remove the lock if hsh matches
	# the hash in the lock file

	if lock_exists():
		with open(LOCK_FILE, "r") as lock:
			contents = lock.read()

		if contents == hsh:
			os.remove(LOCK_FILE)
