"""Registration helper so the age-diff command can be attached to the root CLI."""
from __future__ import annotations

import click

from envguard.cli_differ_age import age_diff_cmd


def register(cli: click.Group) -> None:
    """Attach age_diff_cmd to *cli* under the name 'age-diff'."""
    cli.add_command(age_diff_cmd)
