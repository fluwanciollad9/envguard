"""Thin wrapper used by the CLI to print reporter output and set exit codes."""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from envguard.differ import DiffResult, has_differences
from envguard.reporter import OutputFormat, format_diff, format_validation
from envguard.validator import ValidationResult, is_valid

if TYPE_CHECKING:
    pass


def emit_diff(
    result: DiffResult,
    fmt: OutputFormat = "text",
    exit_nonzero: bool = True,
    file=None,
) -> int:
    """Print diff result and return suggested exit code.

    Args:
        result: The diff result to emit.
        fmt: Output format (e.g. ``"text"`` or ``"json"``).
        exit_nonzero: When *True*, return exit code 1 if differences exist.
        file: File-like object to write to; defaults to ``sys.stdout``.

    Returns:
        Suggested process exit code.
    """
    print(format_diff(result, fmt=fmt), file=file)
    if exit_nonzero and has_differences(result):
        return 1
    return 0


def emit_validation(
    result: ValidationResult,
    fmt: OutputFormat = "text",
    exit_nonzero: bool = True,
    file=None,
) -> int:
    """Print validation result and return suggested exit code.

    Args:
        result: The validation result to emit.
        fmt: Output format (e.g. ``"text"`` or ``"json"``).
        exit_nonzero: When *True*, return exit code 1 if validation failed.
        file: File-like object to write to; defaults to ``sys.stdout``.

    Returns:
        Suggested process exit code.
    """
    print(format_validation(result, fmt=fmt), file=file)
    if exit_nonzero and not is_valid(result):
        return 1
    return 0


def run_and_exit(
    result: DiffResult | ValidationResult,
    fmt: OutputFormat = "text",
    exit_nonzero: bool = True,
) -> None:
    """Emit result and call sys.exit with the appropriate code."""
    if isinstance(result, DiffResult):
        code = emit_diff(result, fmt=fmt, exit_nonzero=exit_nonzero)
    else:
        code = emit_validation(result, fmt=fmt, exit_nonzero=exit_nonzero)
    sys.exit(code)
