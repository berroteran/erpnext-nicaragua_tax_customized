(() => {
	const APP_NAME = "nicaragua_tax_receipt";
	const ENDPOINT = "nicaragua_tax_receipt.api.deployed_version.get_deployed_version";

	// This is a JavaScript namespace, not a dependency on another BEL app.
	// It is already used by installed applications that contribute version rows.
	frappe.provide("bel.installed_versions");
	const shared = bel.installed_versions;

	shared.get_table = shared.get_table || function (frm) {
		let table = frm.$wrapper.find("[data-bel-installed-versions]").first();
		if (table.length) return table;

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
	};

	shared.upsert = shared.upsert || function (frm, details) {
		const appName = details.app_name || details.app;
		if (!appName) return;

		const body = shared.get_table(frm).find("tbody");
		let row = body.children().filter(function () {
			return this.getAttribute("data-bel-app") === appName;
		}).first();
		if (!row.length) row = $("<tr>", { "data-bel-app": appName }).appendTo(body);

		row.empty();
		[
			details.title || appName,
			details.version || __("No disponible"),
			details.branch || __("No disponible"),
			details.commit || __("No disponible"),
			details.git_available ? __("Disponible") : __("No disponible"),
		].forEach((value) => row.append($("<td>").text(value)));
	};

	shared.registered = shared.registered || {};
	if (shared.registered[APP_NAME]) return;
	shared.registered[APP_NAME] = true;

	frappe.ui.form.on("Installed Applications", {
		refresh(frm) {
			if (frappe.session.user !== "Administrator" && !frappe.user.has_role("System Manager")) return;

			frappe
				.xcall(ENDPOINT)
				.then((details) => {
					if (details?.app_name !== APP_NAME) return;
					shared.upsert(frm, {
						app: APP_NAME,
						title: details.app_title,
						version: details.version,
						branch: details.git_branch,
						commit: details.git_commit,
						git_available: details.git_available,
					});
				})
				.catch(() => {});
		},
	});
})();
