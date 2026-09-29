import frappe


BANK_ROLES = ("Bank User", "Bank Manager")

BANK_ROLE_PERMISSIONS = {
	"Bank User": {
		"select": 1,
		"read": 1,
		"write": 1,
		"create": 0,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 1,
		"import": 0,
		"set_user_permissions": 0,
		"share": 1,
		"print": 1,
		"email": 1,
	},
	"Bank Manager": {
		"select": 1,
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 1,
		"import": 0,
		"set_user_permissions": 0,
		"share": 1,
		"print": 1,
		"email": 1,
	},
}


def ensure_bank_role_contract():
	"""Create the BEL bank roles and reconcile their Bank permissions."""
	for role_name in BANK_ROLES:
		ensure_role(role_name)

	if not frappe.db.exists("DocType", "Bank"):
		return

	for role_name, permissions in BANK_ROLE_PERMISSIONS.items():
		ensure_bank_docperm(role_name, permissions)


def ensure_role(role_name):
	values = {
		"desk_access": 1,
		"disabled": 0,
		"is_custom": 0,
		"role_name": role_name,
		"two_factor_auth": 0,
	}

	if frappe.db.exists("Role", role_name):
		frappe.db.set_value("Role", role_name, values, update_modified=False)
		return

	frappe.get_doc({"doctype": "Role", **values}).insert(ignore_permissions=True)


def ensure_bank_docperm(role_name, permissions):
	filters = {"parent": "Bank", "role": role_name, "permlevel": 0}
	custom_docperm_name = frappe.db.get_value("Custom DocPerm", filters, "name")

	if custom_docperm_name:
		frappe.db.set_value("Custom DocPerm", custom_docperm_name, permissions, update_modified=False)
		return

	frappe.get_doc(
		{
			"doctype": "Custom DocPerm",
			"parent": "Bank",
			"role": role_name,
			"permlevel": 0,
			**permissions,
		}
	).insert(ignore_permissions=True)
