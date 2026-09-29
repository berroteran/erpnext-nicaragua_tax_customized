(() => {
	const APP_NAME = "nicaragua_tax_receipt";
	const ENDPOINT = "nicaragua_tax_receipt.api.deployed_version.get_deployed_version";

	frappe.provide("nicaragua_tax_receipt.installed_versions");
	const extension = nicaragua_tax_receipt.installed_versions;
	if (extension.registered) return;
	extension.registered = true;

	function getTable(frm) {
		let table = frm.$wrapper.find("[data-bel-installed-versions]").first();
		if (table.length) return table;

		// Create the shared table only when another installed app has not done so.
		const section = $("<section>", { class: "form-section" });
		section.append($("<div>", { class: "section-head" }).append($("<h5>").text(__("Commits desplegados"))));
		table = $("<div>", {
			class: "table-responsive",
			"data-bel-installed-versions": "1",
		});
		const grid = $("<table>", { class: "table table-bordered" });
		const header = $("<tr>");
		["Aplicación", "Versión", "Rama", "Commit", "Git"].forEach((label) => {
			header.append($("<th>").text(__(label)));
		});
		grid.append($("<thead>").append(header), $("<tbody>"));
		table.append(grid);
		section.append(table);

		const installedAppsGrid = frm.fields_dict.installed_applications?.grid;
		if (installedAppsGrid) $(installedAppsGrid.wrapper).after(section);
		else frm.$wrapper.append(section);

		return table;
	}

	function updateOwnRow(frm, details) {
		const body = getTable(frm).find("tbody");
		let row = body.children().filter(function () {
			return this.getAttribute("data-bel-app") === APP_NAME;
		}).first();
		if (!row.length) row = $("<tr>", { "data-bel-app": APP_NAME }).appendTo(body);

		row.empty();
		[
			details.app_title || APP_NAME,
			details.version || __("No disponible"),
			details.git_branch || __("No disponible"),
			details.git_commit || __("No disponible"),
			details.git_available ? __("Disponible") : __("No disponible"),
		].forEach((value) => row.append($("<td>").text(value)));
	}

	frappe.ui.form.on("Installed Applications", {
		refresh(frm) {
			if (frappe.session.user !== "Administrator" && !frappe.user.has_role("System Manager")) return;

			frappe.call({
				method: ENDPOINT,
				callback(response) {
					if (response.exc || response.message?.app_name !== APP_NAME) return;
					updateOwnRow(frm, response.message);
				},
				error() {},
			});
		},
	});
})();
