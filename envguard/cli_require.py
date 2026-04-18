"""CLI command: envguard require — check env against schema requirements."""
import sys
import json
import click
from envguard.parser import parse_env_file
from envguard.requirer import check_requirements


@click.command("require")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--schema", required=True, type=click.Path(exists=True), help="Schema file (JSON/TOML)")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if optional keys are missing")
def require_cmd(env_file: str, schema: str, fmt: str, strict: bool) -> None:
    """Verify that ENV_FILE satisfies schema requirements."""
    env = parse_env_file(env_file)
    result = check_requirements(env, schema)

    if fmt == "json":
        out = {
            "missing_required": result.missing_required,
            "present_optional": result.present_optional,
            "missing_optional": result.missing_optional,
        }
        click.echo(json.dumps(out, indent=2))
    else:
        if result.missing_required:
            click.secho("MISSING REQUIRED:", fg="red", bold=True)
            for k in result.missing_required:
                click.secho(f"  - {k}", fg="red")
        if result.missing_optional:
            click.secho("Missing optional:", fg="yellow")
            for k in result.missing_optional:
                click.secho(f"  - {k}", fg="yellow")
        if not result.missing_required and not result.missing_optional:
            click.secho("All keys present.", fg="green")

    if result.has_missing_required():
        sys.exit(1)
    if strict and result.missing_optional:
        sys.exit(1)
