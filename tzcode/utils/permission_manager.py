
import frappe

PERMS = ['if_owner', 'read', 'write', 'create', 'delete', 'submit', 'cancel', 'amend', 'report', 'export', 'import', 'set_user_permissions', 'share', 'print', 'email']

class UserPermission():    
	def __init__(self, doctype, role, inverse, permlevel=0):
		self.doctype = doctype
		self.role = role
		self.permlevel = permlevel
		self.perms = { e: 1 if inverse else 0 for e in PERMS }
	
	@staticmethod
	def create_perms(doctype, role, cperms={}, inverse=False, perm_level=0):
		"""
		creates permissions for given doctype and role
		:param doctype: Example "Customer"
		:param role: Example "Role"
		
		(Optional)
		:param cperms: Permission elements to allow, if not provided only Read will be allowed
		:param inverse: Flag to use to disallow given cperms
		:param perm_level: Permission Level "0" if not given.
		"""
		permObj = UserPermission(doctype, role, inverse, perm_level)
		cperms = {e for e in cperms if e in PERMS}

		for e in cperms:
			permObj.perms[e] = 0 if inverse else 1
		
		permObj.perms['read'] = 1
		permObj.perms['permlevel'] = perm_level
		return permObj.update_permissions()
	
	def update_permissions(self):
		extra_filter = {'parent': self.doctype, 'role': self.role, 'permlevel': self.permlevel}
		if frappe.db.exists("Custom DocPerm", extra_filter):
			doc_perm = frappe.get_doc(
				"Custom DocPerm",
				extra_filter
			)
			doc_perm.update(self.perms)
			doc_perm.db_update()
		else:
			doc_perm = frappe.new_doc("Custom DocPerm")
			doc_perm.update(extra_filter)
			doc_perm.update(self.perms)
			doc_perm.save(ignore_permissions=True)
		print('---------------Setting up permissions of {} for {}---------------'.format(self.role, self.doctype))
		return "Permissions Added"
	
	@staticmethod
	def remove_perms(doctype, role):
		frappe.db.sql('DELETE FROM `tabCustom DocPerm` WHERE parent =%s and role =%s', (doctype, role))
		
