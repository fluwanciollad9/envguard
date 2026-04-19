"""Register the convert command with the main CLI."""
from __future__ import annotations
from envguard.cli_convert import convert_cmd


def register(cli: object) -> None:  # type: ignore[type-arg]
    """Attach convert_cmd to *cli* (a click.Group)."""
    cli.add_command(convert_cmd)  # type: ignore[attr-defined]
