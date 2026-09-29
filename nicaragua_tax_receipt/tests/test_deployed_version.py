import ast
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from nicaragua_tax_receipt.api import deployed_version


class TestDeployedVersion(FrappeTestCase):
	def test_returns_declared_version_branch_and_valid_short_sha(self):
		with (
			self.set_user("Administrator"),
			patch.object(deployed_version, "_get_checkout_path", return_value=Path("/tmp")),
			patch.object(
				deployed_version,
				"_run_git",
				side_effect=["true", "main", "a1b2c3d4e5f6"],
			),
		):
			result = deployed_version.get_deployed_version()

		self.assertEqual(result["app_name"], "nicaragua_tax_receipt")
		self.assertEqual(result["version"], deployed_version.__version__)
		self.assertEqual(result["git_branch"], "main")
		self.assertEqual(result["git_commit"], "a1b2c3d4e5f6")
		self.assertTrue(result["git_available"])

	def test_returns_controlled_response_when_git_is_unavailable(self):
		with (
			self.set_user("Administrator"),
			patch.object(deployed_version, "_get_checkout_path", return_value=Path("/tmp")),
			patch.object(deployed_version, "_run_git", side_effect=OSError("git missing")),
		):
			result = deployed_version.get_deployed_version()

		self.assertEqual(result["version"], deployed_version.__version__)
		self.assertFalse(result["git_available"])
		self.assertIsNone(result["git_branch"])
		self.assertIsNone(result["git_commit"])

	def test_rejects_invalid_sha(self):
		with (
			self.set_user("Administrator"),
			patch.object(deployed_version, "_get_checkout_path", return_value=Path("/tmp")),
			patch.object(deployed_version, "_run_git", side_effect=["true", "main", "not-a-sha"]),
		):
			result = deployed_version.get_deployed_version()

		self.assertFalse(result["git_available"])
		self.assertIsNone(result["git_commit"])

	def test_rejects_users_without_system_manager(self):
		with (
			patch.object(deployed_version.frappe, "only_for", side_effect=frappe.PermissionError) as only_for,
			self.assertRaises(frappe.PermissionError),
		):
			deployed_version.get_deployed_version()

		only_for.assert_called_once_with(("Administrator", "System Manager"))

	def test_does_not_persist_deployed_metadata(self):
		with (
			patch.object(deployed_version.frappe, "only_for"),
			patch.object(deployed_version.frappe, "db") as database,
			patch.object(deployed_version, "_get_checkout_path", return_value=Path("/tmp")),
			patch.object(deployed_version, "_run_git", side_effect=["true", "main", "a1b2c3d4e5f6"]),
		):
			deployed_version.get_deployed_version()

		self.assertEqual(database.method_calls, [])

	def test_hooks_register_only_the_installed_applications_script(self):
		hooks_path = Path(frappe.get_app_path("nicaragua_tax_receipt", "hooks.py"))
		hooks = ast.parse(hooks_path.read_text(encoding="utf-8"))
		assignments = {
			node.targets[0].id: node.value
			for node in hooks.body
			if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
		}

		doctype_js = ast.literal_eval(assignments["doctype_js"])
		self.assertEqual(doctype_js["Installed Applications"], "public/js/installed_applications.js")
		self.assertNotIn("override_whitelisted_methods", assignments)
		self.assertIn(
			"public/js/installed_applications.js",
			frappe.get_hooks("doctype_js", app_name="nicaragua_tax_receipt")["Installed Applications"],
		)

	def test_frontend_uses_shared_namespace_and_safe_row_updates(self):
		js_path = Path(frappe.get_app_path("nicaragua_tax_receipt", "public", "js", "installed_applications.js"))
		javascript = js_path.read_text(encoding="utf-8")

		self.assertIn('frappe.provide("nicaragua_tax_receipt.installed_versions")', javascript)
		self.assertIn("function updateOwnRow", javascript)
		self.assertIn('"data-bel-app": APP_NAME', javascript)
		self.assertIn('$("<td>").text(value)', javascript)
		self.assertNotIn("innerHTML", javascript)

	def test_frontend_javascript_has_valid_syntax(self):
		node = shutil.which("node")
		self.assertIsNotNone(node, "Node.js is required to validate Desk JavaScript syntax")
		js_path = Path(frappe.get_app_path("nicaragua_tax_receipt", "public", "js", "installed_applications.js"))
		subprocess.run([node, "--check", str(js_path)], check=True, capture_output=True, text=True)

	def test_uninstall_hook_does_not_delete_business_data(self):
		uninstall_path = Path(frappe.get_app_path("nicaragua_tax_receipt", "uninstall.py"))
		uninstall_source = uninstall_path.read_text(encoding="utf-8")
		self.assertNotIn("delete_doc", uninstall_source)
		self.assertNotIn("db.delete", uninstall_source)
