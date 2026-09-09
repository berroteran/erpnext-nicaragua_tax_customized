import frappe
from frappe import _


PAYMENT_ENTRY_DOCTYPE = "Payment Entry"
TAX_REQUIRED_FIELD = "custom_require_official_receipt_no"
CHILD_RECEIPT_FIELD = "custom_official_receipt_no"
CHEQUE_MODE_OF_PAYMENT = "Cheque"


def validate_payment_entry(doc, _method=None):
	if doc.doctype != PAYMENT_ENTRY_DOCTYPE:
		return

	validate_cheque_reference_fields(doc)

	if doc.party_type != "Supplier":
		return

	for tax in doc.get("taxes") or []:
		receipt_no = (tax.get(CHILD_RECEIPT_FIELD) or "").strip()
		if tax.get(CHILD_RECEIPT_FIELD) != receipt_no:
			tax.set(CHILD_RECEIPT_FIELD, receipt_no)

		if tax.get(TAX_REQUIRED_FIELD) and not receipt_no:
			frappe.throw(
				_(
						"Fila #{0}: El número de comprobante oficial es obligatorio para este impuesto."
				).format(tax.idx)
			)


def validate_cheque_reference_fields(doc):
	if doc.mode_of_payment != CHEQUE_MODE_OF_PAYMENT:
		return

	if not (doc.reference_no or "").strip():
		frappe.throw(_("El campo Cheque / No. de Referencia es obligatorio cuando el modo de pago es Cheque."))

	if not doc.reference_date:
		frappe.throw(_("El campo Cheque / Fecha de referencia es obligatorio cuando el modo de pago es Cheque."))
