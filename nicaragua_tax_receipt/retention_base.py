import json

import frappe
from frappe.utils import flt


SUPPORTED_REFERENCE_DOCTYPES = {
	"Purchase Invoice": {
		"taxable_candidates": ("base_tax_withholding_net_total", "base_net_total"),
		"total_candidates": ("base_rounded_total", "base_grand_total"),
	},
	"Purchase Order": {
		"taxable_candidates": ("base_tax_withholding_net_total", "base_net_total"),
		"total_candidates": ("base_grand_total",),
	},
	"Purchase Receipt": {
		"taxable_candidates": ("base_tax_withholding_net_total", "base_net_total"),
		"total_candidates": ("base_rounded_total", "base_grand_total"),
	},
}


def normalize_references(references):
	if isinstance(references, str):
		references = json.loads(references or "[]")

	return references or []


def get_company_exchange_rate(payment_type, source_exchange_rate=None, target_exchange_rate=None):
	if payment_type == "Receive":
		return flt(source_exchange_rate) or 1

	if payment_type == "Pay":
		return flt(target_exchange_rate) or 1

	return 1


def get_reference_key(doctype, docname):
	return f"{doctype}::{docname}"


def get_retention_reference_base_map(
	references,
	payment_type="Pay",
	source_exchange_rate=None,
	target_exchange_rate=None,
	precision=2,
	ignore_permissions=False,
):
	reference_rows = normalize_references(references)
	exchange_rate = get_company_exchange_rate(payment_type, source_exchange_rate, target_exchange_rate)
	base_map = {}

	for ref in reference_rows:
		doctype = ref.get("reference_doctype")
		docname = ref.get("reference_name")
		allocated_amount = flt(ref.get("allocated_amount"))

		if doctype not in SUPPORTED_REFERENCE_DOCTYPES or not docname or allocated_amount <= 0:
			continue

		if not ignore_permissions and not frappe.has_permission(doctype, "read", doc=docname):
			continue

		source_values = get_reference_source_values(doctype, docname)
		if not source_values:
			continue

		reference_total_base = abs(flt(source_values.get("reference_total_base")))
		taxable_total_base = abs(flt(source_values.get("taxable_total_base")))
		base_allocated_amount = flt(allocated_amount * exchange_rate, precision)

		if reference_total_base <= 0 or taxable_total_base <= 0 or base_allocated_amount <= 0:
			continue

		allocation_ratio = min(1, base_allocated_amount / reference_total_base)
		base_taxable_allocated_amount = flt(taxable_total_base * allocation_ratio, precision)

		base_map[get_reference_key(doctype, docname)] = {
			"reference_doctype": doctype,
			"reference_name": docname,
			"base_reference_total": reference_total_base,
			"base_taxable_total": taxable_total_base,
			"base_allocated_amount": base_allocated_amount,
			"allocation_ratio": allocation_ratio,
			"base_taxable_allocated_amount": base_taxable_allocated_amount,
		}

	return base_map


def get_retention_taxable_base_total(
	references,
	payment_type="Pay",
	source_exchange_rate=None,
	target_exchange_rate=None,
	precision=2,
	ignore_permissions=False,
):
	base_map = get_retention_reference_base_map(
		references=references,
		payment_type=payment_type,
		source_exchange_rate=source_exchange_rate,
		target_exchange_rate=target_exchange_rate,
		precision=precision,
		ignore_permissions=ignore_permissions,
	)

	return flt(
		sum(row.get("base_taxable_allocated_amount", 0) for row in base_map.values()),
		precision,
	)


def get_reference_source_values(doctype, docname):
	config = SUPPORTED_REFERENCE_DOCTYPES.get(doctype)
	if not config:
		return None

	meta = frappe.get_meta(doctype)
	fields = ["name"]

	for fieldname in (*config["taxable_candidates"], *config["total_candidates"]):
		if meta.has_field(fieldname) and fieldname not in fields:
			fields.append(fieldname)

	values = frappe.get_cached_value(doctype, docname, fields, as_dict=True)
	if not values:
		return None

	taxable_total_base = get_first_non_zero_value(values, config["taxable_candidates"])
	reference_total_base = get_first_non_zero_value(values, config["total_candidates"])

	return {
		"taxable_total_base": taxable_total_base,
		"reference_total_base": reference_total_base,
	}


def get_first_non_zero_value(values, candidates):
	for fieldname in candidates:
		value = flt(values.get(fieldname))
		if value:
			return value

	return 0
