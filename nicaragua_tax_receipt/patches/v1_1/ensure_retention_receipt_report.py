import json

import frappe


REPORT_NAME = "Comprobantes de retencion en la fuente"
REPORT_MODULE = "Nicaragua Tax Receipt"
WORKSPACE_NAME = "Accounting"
WORKSPACE_SHORTCUT_LABEL = "Comprobantes de retencion en la fuente"
WORKSPACE_CARD_LABEL = "Informes Nicaragua"
ROLES = ("Accounts User", "Accounts Manager", "Auditor", "System Manager")


def execute():
	ensure_report()
	ensure_workspace_shortcut()
	ensure_workspace_card()
	frappe.clear_cache()


def ensure_report():
	report = frappe.get_doc("Report", REPORT_NAME) if frappe.db.exists("Report", REPORT_NAME) else None

	if not report:
		report = frappe.get_doc(
			{
				"doctype": "Report",
				"report_name": REPORT_NAME,
				"name": REPORT_NAME,
				"ref_doctype": "Payment Entry",
				"report_type": "Script Report",
				"module": REPORT_MODULE,
				"is_standard": "Yes",
				"prepared_report": 0,
				"roles": [{"role": role} for role in ROLES],
			}
		)
		report.insert(ignore_permissions=True)
		return

	changed = False
	changed |= set_value_if_changed(report, "ref_doctype", "Payment Entry")
	changed |= set_value_if_changed(report, "report_type", "Script Report")
	changed |= set_value_if_changed(report, "module", REPORT_MODULE)
	changed |= set_value_if_changed(report, "is_standard", "Yes")
	changed |= set_value_if_changed(report, "disabled", 0)
	changed |= set_value_if_changed(report, "prepared_report", 0)

	roles = [{"role": role} for role in ROLES]
	if [row.role for row in report.roles] != list(ROLES):
		report.set("roles", roles)
		changed = True

	if changed:
		report.save(ignore_permissions=True)


def ensure_workspace_shortcut():
	if not frappe.db.exists("Workspace", WORKSPACE_NAME):
		return

	workspace = frappe.get_doc("Workspace", WORKSPACE_NAME)
	for shortcut in workspace.shortcuts:
		if shortcut.type == "Report" and shortcut.link_to == REPORT_NAME:
			changed = set_value_if_changed(shortcut, "label", WORKSPACE_SHORTCUT_LABEL)
			if changed:
				workspace.save(ignore_permissions=True)
			return

	workspace.append(
		"shortcuts",
		{
			"type": "Report",
			"link_to": REPORT_NAME,
			"label": WORKSPACE_SHORTCUT_LABEL,
		},
	)
	workspace.save(ignore_permissions=True)


def ensure_workspace_card():
	if not frappe.db.exists("Workspace", WORKSPACE_NAME):
		return

	workspace = frappe.get_doc("Workspace", WORKSPACE_NAME)
	changed = ensure_workspace_link_group(workspace)
	changed |= ensure_workspace_content_block(workspace)
	if changed:
		workspace.save(ignore_permissions=True)


def ensure_workspace_link_group(workspace):
	changed = False
	card_break = None
	report_link = None

	for link in workspace.links:
		if link.type == "Card Break" and link.label == WORKSPACE_CARD_LABEL:
			card_break = link
		elif link.type == "Link" and link.link_to == REPORT_NAME and link.is_query_report:
			report_link = link

	if not card_break:
		workspace.append(
			"links",
			{
				"type": "Card Break",
				"label": WORKSPACE_CARD_LABEL,
			},
		)
		card_break = workspace.links[-1]
		changed = True

	if not report_link:
		workspace.append(
			"links",
			{
				"type": "Link",
				"label": REPORT_NAME,
				"link_type": "Report",
				"link_to": REPORT_NAME,
				"is_query_report": 1,
			},
		)
		report_link = workspace.links[-1]
		changed = True

	changed |= set_value_if_changed(report_link, "label", REPORT_NAME)
	changed |= set_value_if_changed(report_link, "link_type", "Report")
	changed |= set_value_if_changed(report_link, "link_to", REPORT_NAME)
	changed |= set_value_if_changed(report_link, "is_query_report", 1)
	changed |= set_value_if_changed(report_link, "hidden", 0)

	changed |= rebuild_workspace_link_order(workspace, card_break, report_link)
	return changed


def rebuild_workspace_link_order(workspace, card_break, report_link):
	other_links = [row for row in workspace.links if row.name not in {card_break.name, report_link.name}]
	ordered_links = other_links + [card_break, report_link]
	if all(current is expected for current, expected in zip(workspace.links, ordered_links, strict=True)):
		return False

	workspace.set("links", ordered_links)
	return True


def ensure_workspace_content_block(workspace):
	try:
		content = json.loads(workspace.content or "[]")
	except Exception:
		content = []
	if not isinstance(content, list):
		content = []

	updated_content = [
		block
		for block in content
		if not (
			block.get("type") == "card"
			and block.get("data", {}).get("card_name") == WORKSPACE_CARD_LABEL
		)
	]

	updated_content.append(
		{
			"id": "ntr-informes-nicaragua-card",
			"type": "card",
			"data": {
				"card_name": WORKSPACE_CARD_LABEL,
				"col": 4,
			},
		}
	)
	if content == updated_content:
		return False

	workspace.content = json.dumps(updated_content)
	return True


def set_value_if_changed(document, fieldname, value):
	if document.get(fieldname) == value:
		return False

	setattr(document, fieldname, value)
	return True
