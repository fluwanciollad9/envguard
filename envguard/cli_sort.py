"""CLI command: envguard sort — sort keys in a .env file."""
from __future__ import annotations
import sys
import click
from envguard.parser import parse_env_file
from envguard.sorter import sort_env, render_sorted


@click.command("sort")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--check",
    is_flag=True,
    default=False,
    help="Exit with non-zero status if file is not already sorted.",
)
@click.option(
    "--in-place", "-i",
    is_flag=True,
    default=False,
    help="Write sorted output back to the file.",
)
@click.option(
    "--group",
    multiple=True,
    metavar="KEY,KEY,...",
    help="Ordered group of keys (repeatable). E.g. --group APP_NAME,APP_ENV",
)
def sort_cmd(env_file: str, check: bool, in_place: bool, group: tuple) -> None:
    """Sort keys in ENV_FILE alphabetically (or by --group order)."""
    env = parse_env_file(env_file)

    groups = None
    if group:
        groups = [g.split(",") for g in group]

    result = sort_env(env, groups=groups)

    if check:
        if result.was_changed:
            click.echo(f"{env_file}: keys are not sorted", err=True)
            sys.exit(1)
        click.echo(f"{env_file}: already sorted")
        return

    rendered = render_sorted(result)

    if in_place:
        with open(env_file, "w") as fh:
            fh.write(rendered)
        changed = "(changed)" if result.was_changed else "(no change)"
        click.echo(f"{env_file}: sorted {changed}")
    else:
        click.echo(rendered, nl=False)
