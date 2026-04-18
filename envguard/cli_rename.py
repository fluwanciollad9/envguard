"""CLI command for renaming keys in a .env file."""
from __future__ import annotations
import sys
import click
from envguard.parser import parse_env_file
from envguard.renamer import rename_env, render_renamed, was_changed


@click.command("rename")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--rename", "pairs", multiple=True, metavar="OLD=NEW",
    help="Key rename mapping, e.g. OLD_KEY=NEW_KEY. Repeatable.",
)
@click.option("--in-place", is_flag=True, help="Write changes back to the file.")
@click.option("--dry-run", is_flag=True, help="Show what would change without writing.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def rename_cmd(env_file: str, pairs: tuple, in_place: bool, dry_run: bool, fmt: str) -> None:
    """Rename one or more keys in ENV_FILE."""
    if not pairs:
        click.echo("No --rename pairs provided.", err=True)
        sys.exit(1)

    renames: dict = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid rename pair '{pair}': expected OLD=NEW", err=True)
            sys.exit(1)
        old, new = pair.split("=", 1)
        renames[old.strip()] = new.strip()

    env = parse_env_file(env_file)
    result = rename_env(env, renames)

    if fmt == "json":
        import json
        click.echo(json.dumps({
            "changes": [list(c) for c in result.changes],
            "not_found": result.not_found,
        }))
    else:
        if result.changes:
            for old, new in result.changes:
                click.echo(f"  {old} -> {new}")
        else:
            click.echo("No keys renamed.")
        if result.not_found:
            click.echo(f"Keys not found: {', '.join(result.not_found)}", err=True)

    if dry_run:
        click.echo("(dry-run: no changes written)")
        sys.exit(0)

    if in_place and was_changed(result):
        with open(env_file, "w") as fh:
            fh.write(render_renamed(result))
        click.echo(f"Written to {env_file}")
    elif not in_place and was_changed(result):
        click.echo(render_renamed(result))
