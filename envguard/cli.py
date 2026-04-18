"""envguard CLI entry point."""
import click
from envguard.cli_merge import merge_cmd
from envguard.cli_audit import audit_cmd
from envguard.cli_snapshot import snapshot_cmd
from envguard.cli_interpolate import interpolate_cmd
from envguard.cli_redact import redact_cmd
from envguard.cli_export import export_cmd
from envguard.cli_sort import sort_cmd
from envguard.cli_rename import rename_cmd
from envguard.cli_duplicates import duplicates_cmd
from envguard.cli_profile import profile_cmd
from envguard.cli_trim import trim_cmd
from envguard.cli_require import require_cmd
from envguard.output import emit_diff, emit_validation, run_and_exit
from envguard.parser import parse_env_file
from envguard.differ import diff_envs
from envguard.validator import validate_env


@click.group()
def cli() -> None:
    """envguard — validate and diff .env files."""


@cli.command()
@click.argument("base", type=click.Path(exists=True))
@click.argument("compare", type=click.Path(exists=True))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def diff(base: str, compare: str, fmt: str) -> None:
    """Diff two .env files."""
    result = diff_envs(parse_env_file(base), parse_env_file(compare))
    run_and_exit(emit_diff(result, fmt))


@cli.command()
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--schema", required=True, type=click.Path(exists=True))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def validate(env_file: str, schema: str, fmt: str) -> None:
    """Validate an .env file against a schema."""
    result = validate_env(parse_env_file(env_file), schema)
    run_and_exit(emit_validation(result, fmt))


cli.add_command(merge_cmd, "merge")
cli.add_command(audit_cmd, "audit")
cli.add_command(snapshot_cmd, "snapshot")
cli.add_command(interpolate_cmd, "interpolate")
cli.add_command(redact_cmd, "redact")
cli.add_command(export_cmd, "export")
cli.add_command(sort_cmd, "sort")
cli.add_command(rename_cmd, "rename")
cli.add_command(duplicates_cmd, "duplicates")
cli.add_command(profile_cmd, "profile")
cli.add_command(trim_cmd, "trim")
cli.add_command(require_cmd, "require")
