"""Compatibility wrapper: expose `generate_log` at package root for tests.

This file simply re-exports `generate_log` from `lib.generate_log` so imports
like `from generate_log import generate_log` work in grading/test environments.
"""

from lib.generate_log import generate_log

__all__ = ["generate_log"]
