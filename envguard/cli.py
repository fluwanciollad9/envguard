"""CLI entry-point for envguard."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .differ import diff_envs, has_differences
from .parser import parse_env_file
from .schema import SchemaError, load_schema, optional_keys, required_keys
from .validator import validate_env


@click.group()
def cli() -> None:
    """envguard — validate and diff .env files."""


@cli.command()
@click.argument("base", type=click.Path(exists=True))
@click.argument("compare", type=click.Path(exists=True))
def diff(base: str, compare: str) -> None:
    """Diff two .env files and report differences."""
    base_env = parse_env_file(base)
    compare_env = parse_env_file(compare)
    result = diff_envs(base_env, compare_env)

    if not has_differences(result):
        click.echo("No differences found.")
        return

    if result.added:
        click.echo("Added keys: " + ", ".join(sorted(result.added)))
    if result.removed:
        click.echo("Removed keys: " + ", ".join(sorted(result.removed)))
    if result.changed:
        click.echo("Changed keys: " + ", ".join(sorted(result.changed)))
    sys.exit(1)


@cli.command()
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--schema",
    "schema_path",
    required=True,
    type=click.Path(),
    help="Path to JSON or TOML schema file.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Fail on unknown keys not listed in schema.",
)
def validate(env_file: str, schema_path: str, strict: bool) -> None:
    """Validate an .env file against a schema."""
    try:
        schema = load_schema(schema_path)
    except SchemaError as exc:
        click.echo(f"Schema error: {exc}", err=True)
        sys.exit(2)

    env = parse_env_file(env_file)
    result = validate_env(
        env,
        required=required_keys(schema),
        optional=optional_keys(schema),
        allow_unknown=not strict,
    )

    click.echo(result.summary())
    if not result.is_valid:
        sys.exit(1)
