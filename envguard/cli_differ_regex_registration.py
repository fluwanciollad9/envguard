"""Registration helper for the regex-diff command."""
from __future__ import annotations

from envguard.cli_differ_regex import regex_diff_cmd


def register(cli_group) -> None:
    """Attach regex_diff_cmd to *cli_group*."""
    cli_group.add_command(regex_diff_cmd)
