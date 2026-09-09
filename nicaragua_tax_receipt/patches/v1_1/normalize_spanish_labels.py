import frappe


DOCTYPE = "Payment Entry"

LABELS = {
	"Purchase Taxes and Charges-custom_require_official_receipt_no": "Requiere comprobante oficial",
	"Advance Taxes and Charges-custom_require_official_receipt_no": "Requiere comprobante oficial",
	"Advance Taxes and Charges-custom_official_receipt_no": "Número de comprobante oficial",
	"Payment Entry Deduction-custom_receipt_no": "No Comprobante",
	"Supplier-impresion_cheque": "Impresión en cheque",
}

PAYMENT_ENTRY_LABELS = {
	"deductions": "Deducciones o Pérdida",
}


def execute():
	for custom_field_name, label in LABELS.items():
		if not frappe.db.exists("Custom Field", custom_field_name):
			continue

		frappe.db.set_value("Custom Field", custom_field_name, "label", label, update_modified=False)

	for fieldname, label in PAYMENT_ENTRY_LABELS.items():
		upsert_property_setter(fieldname, "label", label)

	frappe.clear_cache(doctype=DOCTYPE)


def upsert_property_setter(fieldname, property_name, value):
	filters = {
		"doc_type": DOCTYPE,
		"field_name": fieldname,
		"property": property_name,
	}
	existing = frappe.db.get_value("Property Setter", filters, "name")

	if existing:
		frappe.db.set_value("Property Setter", existing, "value", value, update_modified=False)
		return

	frappe.get_doc(
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": DOCTYPE,
			"field_name": fieldname,
			"property": property_name,
			"property_type": "Data",
			"value": value,
		}
	).insert(ignore_permissions=True)
