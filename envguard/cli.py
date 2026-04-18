"""Main CLI entry point for envguard."""
import click

from envguard.output import emit_diff, emit_validation, run_and_exit
from envguard.cli_merge import merge_cmd
from envguard.cli_audit import audit_cmd
from envguard.cli_snapshot import snapshot_cmd


@click.group()
def cli():
    """envguard — validate and diff .env files."""


@cli.command()
@click.argument("base")
@click.argument("compare")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--exit-code", is_flag=True, default=False, help="Exit 1 if differences found.")
def diff(base: str, compare: str, fmt: str, exit_code: bool):
    """Diff two .env files."""
    from envguard.differ import diff_envs
    from envguard.parser import parse_env_file

    result = diff_envs(parse_env_file(base), parse_env_file(compare))
    run_and_exit(emit_diff(result, fmt=fmt), use_exit_code=exit_code and (result.missing or result.extra or result.changed))


@cli.command()
@click.argument("env_file")
@click.option("-s", "--schema", "schema_path", required=True, help="Path to schema file (TOML or JSON).")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--exit-code", is_flag=True, default=False)
def validate(env_file: str, schema_path: str, fmt: str, exit_code: bool):
    """Validate an .env file against a schema."""
    from envguard.validator import validate_env
    from envguard.schema import load_schema

    schema = load_schema(schema_path)
    result = validate_env(schema, env_file)
    run_and_exit(emit_validation(result, fmt=fmt), use_exit_code=exit_code and not result.valid)


cli.add_command(merge_cmd, name="merge")
cli.add_command(audit_cmd, name="audit")
cli.add_command(snapshot_cmd, name="snapshot")


if __name__ == "__main__":
    cli()
