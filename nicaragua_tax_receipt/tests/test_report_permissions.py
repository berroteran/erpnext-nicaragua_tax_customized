from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from nicaragua_tax_receipt.nicaragua_tax_receipt.report.comprobantes_de_retencion_en_la_fuente import (
	comprobantes_de_retencion_en_la_fuente as report,
)


class TestRetentionReceiptReportPermissions(FrappeTestCase):
	def test_permits_payment_entry_readers_with_a_report_role(self):
		with (
			patch.object(frappe, "has_permission", return_value=True),
			patch.object(frappe, "get_roles", return_value=["Accounts User"]),
		):
			self.assertTrue(report.can_read_report_data())

	def test_rejects_payment_entry_readers_without_a_report_role(self):
		with (
			patch.object(frappe, "has_permission", return_value=True),
			patch.object(frappe, "get_roles", return_value=["Sales User"]),
		):
			self.assertFalse(report.can_read_report_data())

	def test_rejects_users_without_payment_entry_read_permission(self):
		with (
			patch.object(frappe, "has_permission", return_value=False),
			patch.object(frappe, "get_roles") as get_roles,
		):
			self.assertFalse(report.can_read_report_data())

		get_roles.assert_not_called()
