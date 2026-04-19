"""Register keydiff command — import and attach to the main CLI group.

Usage in cli.py or main entry point::

    from envguard.cli_differ_keys_registration import register
    register(cli)
"""
from __future__ import annotations
import click
from envguard.cli_differ_keys import keydiff_cmd


def register(group: click.Group) -> None:
    """Attach the keydiff sub-command to *group*."""
    group.add_command(keydiff_cmd)
