frappe.query_reports["Comprobantes de retencion en la fuente"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Desde"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("Hasta"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: "accounts",
			label: __("Cuentas"),
			fieldtype: "MultiSelectList",
			get_data(txt) {
				return frappe.call({
					method: "nicaragua_tax_receipt.nicaragua_tax_receipt.report.comprobantes_de_retencion_en_la_fuente.comprobantes_de_retencion_en_la_fuente.get_account_options",
					args: { txt },
				}).then((r) => r.message || []);
			},
		},
	],
};
