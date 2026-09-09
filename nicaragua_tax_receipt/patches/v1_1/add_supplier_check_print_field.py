import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


DOCTYPE = "Supplier"
FIELDNAME = "impresion_cheque"


def execute():
	if frappe.db.exists("Custom Field", f"{DOCTYPE}-{FIELDNAME}"):
		return

	create_custom_fields(
		{
			DOCTYPE: [
				{
					"fieldname": FIELDNAME,
					"fieldtype": "Data",
					"label": "Impresión en cheque",
					"insert_after": "supplier_name",
					"allow_on_submit": 1,
				}
			]
		},
		update=True,
	)
