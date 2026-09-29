(() => {
	const APP_NAME = "nicaragua_tax_receipt";
	const ENDPOINT = "nicaragua_tax_receipt.api.deployed_version.get_deployed_version";
	const namespace = (window.frappe.installed_application_deployed_commits =
		window.frappe.installed_application_deployed_commits || {});

	namespace.providers = namespace.providers || {};
	namespace.register = namespace.register || function (appName, provider) {
		this.providers[appName] = provider;
	};

	namespace.get_section = namespace.get_section || function (frm) {
		const gridWrapper = frm.fields_dict.installed_applications?.$wrapper?.get(0);
		if (!gridWrapper) return null;

		const parent = gridWrapper.parentElement;
		let section = parent.querySelector("[data-deployed-commits-section]");
		if (section) return section;

		section = document.createElement("section");
		section.dataset.deployedCommitsSection = "1";
		section.className = "form-section card-section";

		const title = document.createElement("h5");
		title.className = "section-head";
		title.textContent = __("Commits desplegados");
		section.appendChild(title);

		const table = document.createElement("table");
		table.className = "table table-bordered";
		const header = document.createElement("thead");
		const headerRow = document.createElement("tr");
		[__("Aplicación"), __("Versión"), __("Rama"), __("Commit"), __("Git")].forEach((label) => {
			const cell = document.createElement("th");
			cell.textContent = label;
			headerRow.appendChild(cell);
		});
		header.appendChild(headerRow);
		table.appendChild(header);
		table.appendChild(document.createElement("tbody"));
		section.appendChild(table);
		parent.insertBefore(section, gridWrapper.nextSibling);

		return section;
	};

	namespace.update_row = namespace.update_row || function (frm, data) {
		const appName = String(data?.app_name || "");
		const section = namespace.get_section(frm);
		if (!appName || !section) return;

		const body = section.querySelector("tbody");
		let row = Array.from(body.rows).find((item) => item.dataset.appName === appName);
		if (!row) {
			row = document.createElement("tr");
			row.dataset.appName = appName;
			for (let index = 0; index < 5; index += 1) {
				row.appendChild(document.createElement("td"));
			}
			body.appendChild(row);
		}

		const unavailable = __("No disponible");
		const values = [
			data.app_title || appName,
			data.version || unavailable,
			data.git_branch || unavailable,
			data.git_commit || unavailable,
			data.git_available ? __("Disponible") : unavailable,
		];
		values.forEach((value, index) => {
			row.cells[index].textContent = value;
		});
	};

	namespace.refresh = namespace.refresh || function (frm) {
		if (frm.__deployed_commits_refresh_pending) return;
		frm.__deployed_commits_refresh_pending = true;

		Promise.resolve().then(() => {
			frm.__deployed_commits_refresh_pending = false;
			Object.entries(namespace.providers).forEach(([appName, provider]) => {
				Promise.resolve(provider())
					.then((data) => namespace.update_row(frm, data))
					.catch(() =>
						namespace.update_row(frm, {
							app_name: appName,
							app_title: appName,
							version: __("No disponible"),
							git_available: false,
						})
					);
			});
		});
	};

	namespace.register(APP_NAME, () => frappe.xcall(ENDPOINT));

	frappe.ui.form.on("Installed Applications", {
		refresh(frm) {
			namespace.refresh(frm);
		},
	});
})();
