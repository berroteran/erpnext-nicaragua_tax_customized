import frappe
from frappe.tests.utils import FrappeTestCase

from nicaragua_tax_receipt.patches.v1_1.ensure_retention_receipt_report import (
	REPORT_NAME,
	WORKSPACE_NAME,
	execute,
)


class TestRetentionReceiptMetadata(FrappeTestCase):
	def test_reconciliation_does_not_write_metadata_that_is_already_current(self):
		execute()
		before = {
			"report": frappe.db.get_value("Report", REPORT_NAME, "modified"),
			"workspace": frappe.db.get_value("Workspace", WORKSPACE_NAME, "modified"),
		}

		execute()
		after = {
			"report": frappe.db.get_value("Report", REPORT_NAME, "modified"),
			"workspace": frappe.db.get_value("Workspace", WORKSPACE_NAME, "modified"),
		}

		self.assertEqual(after, before)
