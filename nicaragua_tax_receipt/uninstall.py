import frappe


def after_uninstall():
	"""Finish uninstall without deleting business data.

	The app stores user-entered values in Custom Fields on ERPNext standard
	DocTypes. Those columns and values are intentionally preserved so historical
	payments, reports, and print formats do not lose audit data.
	"""
	frappe.clear_cache()
