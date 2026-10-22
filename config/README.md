# Source download configuration

This directory intentionally contains no maintainer commit-email allowlist.
Use `python3 hub.py doctor` to check a self-hosted installation.

The complete developer suite and website builder require the development Git
checkout, including its CI files and maintainer identity policy. Those inputs
are intentionally excluded from this download. Installation does not require
them. Runtime tests that copy this directory can still prepare their fixtures.
