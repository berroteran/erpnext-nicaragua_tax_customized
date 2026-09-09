from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from frappe import _dict
from frappe.utils import flt

from nicaragua_tax_receipt.overrides.payment_entry import PaymentEntry
from nicaragua_tax_receipt.retention_base import get_retention_taxable_base_total


class TestPaymentEntryRetentionBase(TestCase):
	@patch("nicaragua_tax_receipt.retention_base.frappe.get_cached_value")
	@patch("nicaragua_tax_receipt.retention_base.frappe.get_meta")
	@patch("nicaragua_tax_receipt.retention_base.frappe.has_permission")
	def test_reference_base_uses_purchase_invoice_net_total_proportionally(
		self, mock_has_permission, mock_get_meta, mock_get_cached_value
	):
		mock_has_permission.return_value = True
		mock_get_meta.return_value = SimpleNamespace(has_field=lambda fieldname: True)
		mock_get_cached_value.return_value = _dict(
			{
				"base_tax_withholding_net_total": 100,
				"base_net_total": 100,
				"base_rounded_total": 115,
				"base_grand_total": 115,
			}
		)

		full_base_amount = get_retention_taxable_base_total(
			references=[
				{
					"reference_doctype": "Purchase Invoice",
					"reference_name": "PINV-TEST-0001",
					"allocated_amount": 115,
				}
			],
			payment_type="Pay",
			target_exchange_rate=1,
		)
		partial_base_amount = get_retention_taxable_base_total(
			references=[
				{
					"reference_doctype": "Purchase Invoice",
					"reference_name": "PINV-TEST-0001",
					"allocated_amount": 57.5,
				}
			],
			payment_type="Pay",
			target_exchange_rate=1,
		)

		self.assertEqual(flt(full_base_amount, precision=2), 100.0)
		self.assertEqual(flt(partial_base_amount, precision=2), 50.0)

	def test_payment_entry_retention_tax_uses_reference_net_base(self):
		fake_payment_entry = SimpleNamespace(
			should_use_retention_net_base=lambda tax: True,
			get_retention_net_base_amount=lambda: 100,
		)
		tax_row = _dict({"rate": 2})

		tax_amount = PaymentEntry.get_current_tax_amount(fake_payment_entry, tax_row)

		self.assertEqual(flt(tax_amount, precision=2), 2.0)

	def test_add_negative_rate_is_treated_as_retention_reduction_tax(self):
		fake_payment_entry = SimpleNamespace()
		tax_row = _dict({"add_deduct_tax": "Add", "rate": -2})

		self.assertTrue(PaymentEntry.is_retention_reduction_tax(fake_payment_entry, tax_row))

	def test_deduct_positive_rate_is_treated_as_retention_reduction_tax(self):
		fake_payment_entry = SimpleNamespace()
		tax_row = _dict({"add_deduct_tax": "Deduct", "rate": 2})

		self.assertTrue(PaymentEntry.is_retention_reduction_tax(fake_payment_entry, tax_row))
