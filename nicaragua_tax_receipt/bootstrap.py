import frappe

from nicaragua_tax_receipt.bank_roles import ensure_bank_role_contract
from nicaragua_tax_receipt.patches.v1_0.add_tax_receipt_custom_fields import execute as add_tax_receipt_custom_fields
from nicaragua_tax_receipt.patches.v1_1.add_payment_entry_concept_field import execute as add_payment_entry_concept_field
from nicaragua_tax_receipt.patches.v1_1.add_payment_entry_deduction_receipt_field import (
	execute as add_payment_entry_deduction_receipt_field,
)
from nicaragua_tax_receipt.patches.v1_1.add_supplier_check_print_field import execute as add_supplier_check_print_field
from nicaragua_tax_receipt.patches.v1_1.align_cheque_section_visibility import execute as align_cheque_section_visibility
from nicaragua_tax_receipt.patches.v1_1.ensure_payment_entry_concept_layout import execute as ensure_payment_entry_concept_layout
from nicaragua_tax_receipt.patches.v1_1.ensure_retention_receipt_report import execute as ensure_retention_receipt_report
from nicaragua_tax_receipt.patches.v1_1.move_payment_entry_transaction_section_below_concept import (
	execute as move_payment_entry_transaction_section_below_concept,
)
from nicaragua_tax_receipt.patches.v1_1.normalize_spanish_labels import execute as normalize_spanish_labels
from nicaragua_tax_receipt.patches.v1_1.reorder_payment_entry_field_order import execute as reorder_payment_entry_field_order


def reconcile_site_metadata():
	"""Apply the app metadata in a deterministic and idempotent order."""
	ensure_core_fields()
	ensure_layout_and_labels()
	ensure_retention_receipt_report()


def ensure_core_fields():
	"""Create the fields that the app depends on before any layout or report logic."""
	ensure_bank_role_contract()
	add_tax_receipt_custom_fields()
	add_payment_entry_concept_field()
	add_payment_entry_deduction_receipt_field()
	add_supplier_check_print_field()


def ensure_layout_and_labels():
	"""Align sections, labels, and visibility after the required fields exist."""
	ensure_payment_entry_concept_layout()
	move_payment_entry_transaction_section_below_concept()
	reorder_payment_entry_field_order()
	align_cheque_section_visibility()
	normalize_spanish_labels()


def ensure_report_dependencies():
	"""Self-heal the minimum schema required by the retention report."""
	requirements = (
		("Payment Entry", "concepto", add_payment_entry_concept_field),
		("Advance Taxes and Charges", "custom_official_receipt_no", add_tax_receipt_custom_fields),
		("Payment Entry Deduction", "custom_receipt_no", add_payment_entry_deduction_receipt_field),
	)

	for doctype, fieldname, callback in requirements:
		if has_field(doctype, fieldname):
			continue

		callback()
		frappe.clear_cache(doctype=doctype)


def has_field(doctype, fieldname):
	if not frappe.db.exists("DocType", doctype):
		return False

	return frappe.get_meta(doctype).has_field(fieldname)
