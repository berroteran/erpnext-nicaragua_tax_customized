"""Expose the deployed application version without storing Git metadata."""

import re
import subprocess
from pathlib import Path

import frappe

from nicaragua_tax_receipt import __version__


APP_NAME = "nicaragua_tax_receipt"
APP_TITLE = "Nicaragua Tax Receipt"
GIT_TIMEOUT_SECONDS = 3
SHORT_SHA_PATTERN = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)


@frappe.whitelist()
def get_deployed_version() -> dict:
	"""Return live version control data for this app to system administrators."""
	frappe.only_for(("Administrator", "System Manager"))

	version = {
		"app_name": APP_NAME,
		"app_title": APP_TITLE,
		"version": __version__,
		"git_available": False,
		"git_branch": None,
		"git_commit": None,
	}

	try:
		checkout_path = _get_checkout_path()
		if not checkout_path.is_dir() or _run_git(["rev-parse", "--is-inside-work-tree"], checkout_path) != "true":
			return version

		branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], checkout_path)
		commit = _run_git(["rev-parse", "--short=12", "HEAD"], checkout_path)
		if not SHORT_SHA_PATTERN.fullmatch(commit):
			return version

		version.update(
			{
				"git_available": True,
				"git_branch": branch or None,
				"git_commit": commit.lower(),
			}
		)
	except (OSError, RuntimeError, subprocess.SubprocessError):
		# Git metadata is optional and must never prevent the form from loading.
		pass

	return version


def _get_checkout_path() -> Path:
	"""Resolve the repository directory that contains this installed application."""
	return Path(frappe.get_app_path(APP_NAME)).resolve().parent


def _run_git(arguments: list[str], checkout_path: Path) -> str:
	"""Run a bounded Git command inside this application's installed checkout."""
	result = subprocess.run(
		["git", *arguments],
		cwd=checkout_path,
		capture_output=True,
		check=False,
		text=True,
		timeout=GIT_TIMEOUT_SECONDS,
	)
	if result.returncode:
		raise RuntimeError("Git metadata is unavailable")

	return result.stdout.strip()
