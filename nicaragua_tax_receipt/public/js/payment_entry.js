const RETENTION_BASE_METHOD =
	"nicaragua_tax_receipt.overrides.payment_entry.get_retention_reference_bases";

function getRetentionReferenceRequestKey(frm) {
	return JSON.stringify({
		payment_type: frm.doc.payment_type,
		party_type: frm.doc.party_type,
		source_exchange_rate: frm.doc.source_exchange_rate,
		target_exchange_rate: frm.doc.target_exchange_rate,
		references: (frm.doc.references || []).map((row) => ({
			reference_doctype: row.reference_doctype,
			reference_name: row.reference_name,
			allocated_amount: row.allocated_amount,
		})),
	});
}

function getRetentionBasePrecision() {
	try {
		return precision("base_paid_amount") || 2;
	} catch (error) {
		return 2;
	}
}

function shouldUseRetentionNetBase(frm, tax) {
	const isRetentionReductionTax =
		tax.add_deduct_tax === "Deduct" ||
		(tax.add_deduct_tax === "Add" && flt(tax.rate) < 0);

	return (
		frm.doc.party_type === "Supplier" &&
		frm.doc.payment_type === "Pay" &&
		isRetentionReductionTax &&
		["On Paid Amount", "On Net Total"].includes(tax.charge_type) &&
		flt(frm.ntr_retention_base_payload?.base_amount) > 0
	);
}

function patchTaxCalculation(frm) {
	if (frm.__ntr_tax_patch_applied) {
		return;
	}

	const originalGetCurrentTaxAmount = frm.events.get_current_tax_amount.bind(frm.events);
	const originalGetCurrentTaxFraction = frm.events.get_current_tax_fraction.bind(frm.events);

	frm.events.get_current_tax_amount = function (form, tax) {
		if (shouldUseRetentionNetBase(form, tax)) {
			return flt((flt(tax.rate) / 100.0) * flt(form.ntr_retention_base_payload.base_amount));
		}

		return originalGetCurrentTaxAmount(form, tax);
	};

	frm.events.get_current_tax_fraction = function (form, tax) {
		if (shouldUseRetentionNetBase(form, tax) && cint(tax.included_in_paid_amount)) {
			const paidAmountAfterTax = flt(form.doc.paid_amount_after_tax);
			if (!paidAmountAfterTax) {
				return 0;
			}

			let currentTaxFraction =
				(flt(tax.rate) / 100.0) *
				(flt(form.ntr_retention_base_payload.base_amount) / paidAmountAfterTax);

			if (tax.add_deduct_tax === "Deduct") {
				currentTaxFraction *= -1.0;
			}

			return currentTaxFraction;
		}

		return originalGetCurrentTaxFraction(form, tax);
	};

	frm.__ntr_tax_patch_applied = true;
}

function refreshRetentionReferenceBases(frm) {
	if (!(frm.doc.party_type === "Supplier" && frm.doc.payment_type === "Pay")) {
		frm.ntr_retention_base_payload = { base_amount: 0, references: {} };
		if (frm.doc.taxes?.length) {
			frm.events.apply_taxes(frm);
		}
		return Promise.resolve();
	}

	const references = (frm.doc.references || []).filter(
		(row) => row.reference_doctype && row.reference_name && flt(row.allocated_amount) > 0
	);

	if (!references.length) {
		frm.ntr_retention_base_payload = { base_amount: 0, references: {} };
		if (frm.doc.taxes?.length) {
			frm.events.apply_taxes(frm);
		}
		return Promise.resolve();
	}

	const requestKey = getRetentionReferenceRequestKey(frm);
	if (frm.__ntr_retention_base_request_key === requestKey && frm.ntr_retention_base_payload) {
		return Promise.resolve(frm.ntr_retention_base_payload);
	}

	frm.__ntr_retention_base_request_key = requestKey;

	return frappe.call({
		method: RETENTION_BASE_METHOD,
		args: {
			references,
			payment_type: frm.doc.payment_type,
			source_exchange_rate: frm.doc.source_exchange_rate,
			target_exchange_rate: frm.doc.target_exchange_rate,
			precision: getRetentionBasePrecision(),
		},
		callback: (response) => {
			frm.ntr_retention_base_payload = response.message || { base_amount: 0, references: {} };
			if (frm.doc.taxes?.length) {
				frm.events.apply_taxes(frm);
			}
		},
	});
}

frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		patchTaxCalculation(frm);
		frm.trigger("toggle_cheque_reference_requirements");
		frm.trigger("configure_tax_grid");
		frm.trigger("load_retention_reference_bases");
	},

	mode_of_payment(frm) {
		frm.trigger("toggle_cheque_reference_requirements");
	},

	party_type(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	payment_type(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	source_exchange_rate(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	target_exchange_rate(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	references_on_form_rendered(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	taxes_on_form_rendered(frm) {
		frm.trigger("configure_tax_grid");
	},

	load_retention_reference_bases(frm) {
		return refreshRetentionReferenceBases(frm);
	},

	toggle_cheque_reference_requirements(frm) {
		const isCheque = frm.doc.mode_of_payment === "Cheque";
		frm.set_df_property("transaction_references", "depends_on", "eval:true");
		frm.set_df_property("reference_no", "depends_on", "eval:true");
		frm.set_df_property("reference_date", "depends_on", "eval:true");
		frm.set_df_property("clearance_date", "depends_on", "eval:doc.docstatus==1");
		frm.set_df_property("reference_no", "reqd", isCheque ? 1 : 0);
		frm.set_df_property("reference_date", "reqd", isCheque ? 1 : 0);
		frm.refresh_field("transaction_references");
		frm.refresh_field("reference_no");
		frm.refresh_field("reference_date");
		frm.refresh_field("clearance_date");
	},

	configure_tax_grid(frm) {
		if (frm.fields_dict.taxes?.grid) {
			frm.fields_dict.taxes.grid.toggle_display("custom_require_official_receipt_no", true);
			frm.fields_dict.taxes.grid.toggle_display("custom_official_receipt_no", true);
			frm.fields_dict.taxes.grid.update_docfield_property(
				"custom_require_official_receipt_no",
				"read_only",
				0
			);
			frm.fields_dict.taxes.grid.update_docfield_property(
				"custom_official_receipt_no",
				"read_only",
				0
			);
		}
	},
});

frappe.ui.form.on("Payment Entry Reference", {
	reference_doctype(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	reference_name(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	allocated_amount(frm) {
		frm.trigger("load_retention_reference_bases");
	},

	references_remove(frm) {
		frm.trigger("load_retention_reference_bases");
	},
});
