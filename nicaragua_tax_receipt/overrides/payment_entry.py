import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry as ERPNextPaymentEntry

from nicaragua_tax_receipt.retention_base import (
	get_retention_reference_base_map,
	get_retention_taxable_base_total,
)


class PaymentEntry(ERPNextPaymentEntry):
	def get_current_tax_amount(self, tax):
		if self.should_use_retention_net_base(tax):
			return flt((flt(tax.rate) / 100.0) * self.get_retention_net_base_amount())

		return super().get_current_tax_amount(tax)

	def get_current_tax_fraction(self, tax):
		if self.should_use_retention_net_base(tax) and cint(tax.included_in_paid_amount):
			paid_amount_after_tax = flt(self.paid_amount_after_tax)
			if not paid_amount_after_tax:
				return 0

			current_tax_fraction = (flt(tax.rate) / 100.0) * (
				self.get_retention_net_base_amount() / paid_amount_after_tax
			)

			if getattr(tax, "add_deduct_tax", None) == "Deduct":
				current_tax_fraction *= -1.0

			return current_tax_fraction

		return super().get_current_tax_fraction(tax)

	def should_use_retention_net_base(self, tax):
		if self.party_type != "Supplier" or self.payment_type != "Pay":
			return False

		if not self.is_retention_reduction_tax(tax):
			return False

		if tax.charge_type not in ("On Paid Amount", "On Net Total"):
			return False

		return bool(self.get_retention_reference_base_map())

	def is_retention_reduction_tax(self, tax):
		add_deduct_tax = getattr(tax, "add_deduct_tax", None)
		rate = flt(getattr(tax, "rate", 0))

		if add_deduct_tax == "Deduct":
			return True

		# ERPNext suele copiar estas retenciones como filas "Add"
		# con tasa negativa al traer la plantilla al Payment Entry.
		return add_deduct_tax == "Add" and rate < 0

	def get_retention_net_base_amount(self):
		if not hasattr(self, "_ntr_retention_net_base_amount"):
			self._ntr_retention_net_base_amount = get_retention_taxable_base_total(
				references=self.get("references") or [],
				payment_type=self.payment_type,
				source_exchange_rate=self.source_exchange_rate,
				target_exchange_rate=self.target_exchange_rate,
				precision=self.precision("base_paid_amount"),
				ignore_permissions=True,
			)

		return self._ntr_retention_net_base_amount

	def get_retention_reference_base_map(self):
		if not hasattr(self, "_ntr_retention_reference_base_map"):
			self._ntr_retention_reference_base_map = frappe._dict(
				get_retention_reference_base_map(
					references=self.get("references") or [],
					payment_type=self.payment_type,
					source_exchange_rate=self.source_exchange_rate,
					target_exchange_rate=self.target_exchange_rate,
					precision=self.precision("base_paid_amount"),
					ignore_permissions=True,
				)
			)

		return self._ntr_retention_reference_base_map


@frappe.whitelist()
def get_retention_reference_bases(
	references=None,
	payment_type="Pay",
	source_exchange_rate=None,
	target_exchange_rate=None,
	precision=2,
):
	if not frappe.has_permission("Payment Entry", "read"):
		frappe.throw(_("No tiene permisos para consultar la base de retención."), frappe.PermissionError)

	base_map = get_retention_reference_base_map(
		references=references,
		payment_type=payment_type,
		source_exchange_rate=source_exchange_rate,
		target_exchange_rate=target_exchange_rate,
		precision=precision,
	)

	return {
		"base_amount": flt(
			sum(row.get("base_taxable_allocated_amount", 0) for row in base_map.values()),
			precision,
		),
		"references": base_map,
	}
