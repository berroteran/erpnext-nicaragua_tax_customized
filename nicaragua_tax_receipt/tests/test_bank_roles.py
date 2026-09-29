import frappe
from frappe.tests.utils import FrappeTestCase

from nicaragua_tax_receipt.bank_roles import BANK_ROLE_PERMISSIONS, BANK_ROLES, ensure_bank_role_contract


class TestBankRoles(FrappeTestCase):
	def test_bank_roles_match_the_bel_custom_contract(self):
		self.assertEqual(BANK_ROLES, ("Bank User", "Bank Manager"))
		self.assertEqual(BANK_ROLE_PERMISSIONS["Bank User"]["create"], 0)
		self.assertEqual(BANK_ROLE_PERMISSIONS["Bank Manager"]["create"], 1)

		for role_name in BANK_ROLES:
			permissions = BANK_ROLE_PERMISSIONS[role_name]
			self.assertEqual(permissions["read"], 1)
			self.assertEqual(permissions["write"], 1)
			self.assertEqual(permissions["report"], 1)

	def test_bank_roles_and_permissions_are_reconciled(self):
		ensure_bank_role_contract()

		for role_name in BANK_ROLES:
			role = frappe.get_doc("Role", role_name)
			self.assertEqual(role.desk_access, 1)
			self.assertFalse(role.disabled)

			permissions = frappe.db.get_value(
				"Custom DocPerm",
				{"parent": "Bank", "role": role_name, "permlevel": 0},
				list(BANK_ROLE_PERMISSIONS[role_name]),
				as_dict=True,
			)
			self.assertIsNotNone(permissions)
			for fieldname, expected_value in BANK_ROLE_PERMISSIONS[role_name].items():
				self.assertEqual(permissions.get(fieldname), expected_value)
