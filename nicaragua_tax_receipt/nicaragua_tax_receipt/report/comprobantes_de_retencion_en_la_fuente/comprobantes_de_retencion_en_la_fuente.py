import frappe
from frappe import _

from nicaragua_tax_receipt.bootstrap import ensure_report_dependencies


PARTY_DOCTYPES = ("Supplier", "Customer")
REPORT_ROLES = ("Accounts User", "Accounts Manager", "Auditor", "System Manager")


def execute(filters=None):
	filters = frappe._dict(filters or {})
	ensure_report_dependencies()
	validate_filters(filters)

	party_details = get_party_details()
	account_filter = normalize_account_filter(filters.get("accounts"))
	data = get_tax_rows(filters, party_details, account_filter) + get_deduction_rows(filters, party_details, account_filter)
	data.sort(key=lambda row: (row.get("fecha"), row.get("entrada_de_pago"), row.get("origen"), row.get("cuenta")))

	return get_columns(), data


@frappe.whitelist()
def get_account_options(doctype=None, txt=None, searchfield=None, start=0, page_len=20, filters=None):
	if not can_read_report_data():
		frappe.throw(_("No tiene permisos para consultar cuentas de retención."), frappe.PermissionError)

	txt = (txt or "").strip().lower()
	options = []

	for account in get_used_retention_accounts():
		if txt and txt not in account.lower():
			continue
		options.append({"value": account, "description": account})

	return options[int(start) : int(start) + int(page_len)]


def can_read_report_data():
	if not frappe.has_permission("Payment Entry", "read"):
		return False

	return bool(set(REPORT_ROLES) & set(frappe.get_roles()))


def validate_filters(filters):
	if not filters.get("from_date") or not filters.get("to_date"):
		frappe.throw(_("Los filtros Desde y Hasta son obligatorios."))

	if filters.from_date > filters.to_date:
		frappe.throw(_("La fecha Desde no puede ser mayor que la fecha Hasta."))


def normalize_account_filter(accounts):
	if not accounts:
		return []

	if isinstance(accounts, str):
		parsed = frappe.parse_json(accounts)
		if isinstance(parsed, list):
			accounts = parsed
		else:
			accounts = [accounts]

	return [account for account in accounts if account]


def get_used_retention_accounts():
	rows = frappe.db.sql(
		"""
		SELECT DISTINCT account
		FROM (
			SELECT atc.account_head AS account
			FROM `tabAdvance Taxes and Charges` atc
			WHERE IFNULL(atc.account_head, '') != ''

			UNION

			SELECT ped.account AS account
			FROM `tabPayment Entry Deduction` ped
			WHERE IFNULL(ped.account, '') != ''
		) accounts
		INNER JOIN `tabAccount` acc
			ON acc.name = accounts.account
		WHERE acc.root_type = 'Liability'
		  AND acc.report_type = 'Balance Sheet'
		  AND IFNULL(acc.account_type, '') != 'Cash'
		  AND (
			IFNULL(acc.account_type, '') = 'Tax'
			OR UPPER(accounts.account) REGEXP 'RETENCION|IMPUEST|IVA'
		  )
		ORDER BY account
		""",
		as_dict=True,
	)

	return [row.account for row in rows]


def get_party_details():
	party_details = {}

	for doctype in PARTY_DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			continue

		meta = frappe.get_meta(doctype)
		fields = ["name"]
		if meta.has_field("supplier_name"):
			fields.append("supplier_name")
		if meta.has_field("customer_name"):
			fields.append("customer_name")
		if meta.has_field("tax_id"):
			fields.append("tax_id")

		for row in frappe.get_all(doctype, fields=fields, limit_page_length=0):
			party_details[(doctype, row.name)] = {
				"tax_id": row.get("tax_id"),
				"display_name": row.get("supplier_name") or row.get("customer_name") or row.name,
			}

	return party_details


def get_tax_rows(filters, party_details, account_filter):
	conditions = [
		"pe.docstatus = 1",
		"pe.posting_date BETWEEN %(from_date)s AND %(to_date)s",
		"IFNULL(atc.custom_official_receipt_no, '') != ''",
	]
	params = dict(filters)

	if account_filter:
		conditions.append("atc.account_head IN %(accounts)s")
		params["accounts"] = tuple(account_filter)

	rows = frappe.db.sql(
		f"""
		SELECT
			pe.name AS payment_entry,
			pe.posting_date,
			pe.party_type,
			pe.party,
			pe.party_name,
			pe.concepto,
			pe.mode_of_payment,
			pe.reference_no,
			pe.paid_amount,
			pe.received_amount,
			atc.account_head,
			atc.description,
			atc.rate,
			atc.tax_amount,
			atc.custom_official_receipt_no
		FROM `tabPayment Entry` pe
		INNER JOIN `tabAdvance Taxes and Charges` atc
			ON atc.parent = pe.name
		WHERE {" AND ".join(conditions)}
		ORDER BY pe.posting_date, pe.name, atc.idx
		""",
		params,
		as_dict=True,
	)

	return [build_tax_row(row, party_details) for row in rows]


def get_deduction_rows(filters, party_details, account_filter):
	conditions = [
		"pe.docstatus = 1",
		"pe.posting_date BETWEEN %(from_date)s AND %(to_date)s",
		"IFNULL(ped.custom_receipt_no, '') != ''",
	]
	params = dict(filters)

	if account_filter:
		conditions.append("ped.account IN %(accounts)s")
		params["accounts"] = tuple(account_filter)

	rows = frappe.db.sql(
		f"""
		SELECT
			pe.name AS payment_entry,
			pe.posting_date,
			pe.party_type,
			pe.party,
			pe.party_name,
			pe.concepto,
			pe.mode_of_payment,
			pe.reference_no,
			pe.paid_amount,
			pe.received_amount,
			ped.account,
			ped.description,
			ped.amount,
			ped.custom_receipt_no
		FROM `tabPayment Entry` pe
		INNER JOIN `tabPayment Entry Deduction` ped
			ON ped.parent = pe.name
		WHERE {" AND ".join(conditions)}
		ORDER BY pe.posting_date, pe.name, ped.idx
		""",
		params,
		as_dict=True,
	)

	return [build_deduction_row(row, party_details) for row in rows]


def build_tax_row(row, party_details):
	party = party_details.get((row.party_type, row.party), {})

	return frappe._dict(
		{
			"fecha": row.posting_date,
			"entrada_de_pago": row.payment_entry,
			"origen": "Impuestos",
			"tipo_tercero": row.party_type,
			"tercero": row.party,
			"cedula_ruc": party.get("tax_id"),
			"nombre_razon_social": row.party_name or party.get("display_name") or row.party,
			"concepto": row.concepto,
			"modo_de_pago": row.mode_of_payment,
			"numero_referencia_cheque": row.reference_no,
			"cuenta": row.account_head,
			"descripcion": row.description,
			"porcentaje_retencion": row.rate,
			"monto_bruto": get_gross_amount(row),
			"monto_retencion": row.tax_amount,
			"numero_comprobante": row.custom_official_receipt_no,
		}
	)


def build_deduction_row(row, party_details):
	party = party_details.get((row.party_type, row.party), {})

	return frappe._dict(
		{
			"fecha": row.posting_date,
			"entrada_de_pago": row.payment_entry,
			"origen": "Deducciones o Pérdida",
			"tipo_tercero": row.party_type,
			"tercero": row.party,
			"cedula_ruc": party.get("tax_id"),
			"nombre_razon_social": row.party_name or party.get("display_name") or row.party,
			"concepto": row.concepto,
			"modo_de_pago": row.mode_of_payment,
			"numero_referencia_cheque": row.reference_no,
			"cuenta": row.account,
			"descripcion": row.description,
			"porcentaje_retencion": None,
			"monto_bruto": get_gross_amount(row),
			"monto_retencion": row.amount,
			"numero_comprobante": row.custom_receipt_no,
		}
	)


def get_gross_amount(row):
	paid_amount = abs(frappe.utils.flt(row.get("paid_amount")))
	received_amount = abs(frappe.utils.flt(row.get("received_amount")))
	return max(paid_amount, received_amount)


def get_columns():
	return [
		{"label": _("Fecha"), "fieldname": "fecha", "fieldtype": "Date", "width": 95},
		{
			"label": _("Entrada de pago"),
			"fieldname": "entrada_de_pago",
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 170,
		},
		{"label": _("Origen"), "fieldname": "origen", "fieldtype": "Data", "width": 160},
		{"label": _("Tipo de tercero"), "fieldname": "tipo_tercero", "fieldtype": "Data", "width": 110},
		{
			"label": _("Tercero"),
			"fieldname": "tercero",
			"fieldtype": "Dynamic Link",
			"options": "tipo_tercero",
			"width": 180,
		},
		{"label": _("Cédula / RUC"), "fieldname": "cedula_ruc", "fieldtype": "Data", "width": 130},
		{"label": _("Nombre / Razón Social"), "fieldname": "nombre_razon_social", "fieldtype": "Data", "width": 220},
		{"label": _("Concepto"), "fieldname": "concepto", "fieldtype": "Data", "width": 220},
		{
			"label": _("Modo de pago"),
			"fieldname": "modo_de_pago",
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"width": 150,
		},
		{
			"label": _("N° de cheque / referencia"),
			"fieldname": "numero_referencia_cheque",
			"fieldtype": "Data",
			"width": 150,
		},
		{"label": _("Cuenta"), "fieldname": "cuenta", "fieldtype": "Data", "width": 220},
		{"label": _("Descripción"), "fieldname": "descripcion", "fieldtype": "Data", "width": 220},
		{"label": _("% Retención"), "fieldname": "porcentaje_retencion", "fieldtype": "Percent", "width": 105},
		{"label": _("Monto bruto"), "fieldname": "monto_bruto", "fieldtype": "Currency", "width": 120},
		{"label": _("Monto retención"), "fieldname": "monto_retencion", "fieldtype": "Currency", "width": 130},
		{"label": _("No Comprobante"), "fieldname": "numero_comprobante", "fieldtype": "Data", "width": 150},
	]
