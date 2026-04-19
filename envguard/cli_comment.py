"""CLI commands for managing inline comments in .env files."""
import json
import sys
from pathlib import Path

import click

from envguard.commentor import add_comments, remove_comments, list_comments, was_changed


@click.group("comment")
def comment_cmd():
    """Manage inline comments in .env files."""


@comment_cmd.command("add")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", "pairs", multiple=True, metavar="KEY=TEXT",
              help="KEY=comment text (repeatable)")
@click.option("--in-place", is_flag=True, help="Write changes back to file.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def add_cmd(env_file, pairs, in_place, fmt):
    """Add or replace inline comments for specified keys."""
    annotations = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid --key value: {pair!r} (expected KEY=text)", err=True)
            sys.exit(1)
        k, _, v = pair.partition("=")
        annotations[k.strip()] = v.strip()
    if not annotations:
        click.echo("No --key values provided.", err=True)
        sys.exit(1)
    env_lines = Path(env_file).read_text().splitlines()
    result = add_comments(env_lines, annotations)
    output = "\n".join(result.lines)
    if in_place:
        Path(env_file).write_text(output + "\n")
    if fmt == "json":
        click.echo(json.dumps({"added": result.added, "comments": result.comments}))
    else:
        if not in_place:
            click.echo(output)
        click.echo(f"Updated comments for: {', '.join(result.added) or 'none'}", err=True)


@comment_cmd.command("remove")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, help="Keys to strip comments from (default: all).")
@click.option("--in-place", is_flag=True)
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def remove_cmd(env_file, keys, in_place, fmt):
    """Remove inline comments from .env file."""
    env_lines = Path(env_file).read_text().splitlines()
    result = remove_comments(env_lines, list(keys) if keys else None)
    output = "\n".join(result.lines)
    if in_place:
        Path(env_file).write_text(output + "\n")
    if fmt == "json":
        click.echo(json.dumps({"removed": result.removed}))
    else:
        if not in_place:
            click.echo(output)
        click.echo(f"Removed comments from: {', '.join(result.removed) or 'none'}", err=True)


@comment_cmd.command("list")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def list_cmd(env_file, fmt):
    """List all inline comments in .env file."""
    env_lines = Path(env_file).read_text().splitlines()
    comments = list_comments(env_lines)
    if fmt == "json":
        click.echo(json.dumps(comments))
    else:
        if not comments:
            click.echo("No inline comments found.")
        else:
            for key, comment in comments.items():
                click.echo(f"{key}: {comment}")
