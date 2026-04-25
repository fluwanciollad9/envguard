"""Registration helper so section-diff is wired into the main CLI group."""
from __future__ import annotations

from envguard.cli_differ_sections import section_diff_cmd


def register(cli_group) -> None:  # type: ignore[type-arg]
    """Attach section_diff_cmd to the given Click group."""
    cli_group.add_command(section_diff_cmd)
