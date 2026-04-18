"""CLI command for auditing .env files for security and quality issues."""

import click
from pathlib import Path

from envguard.parser import parse_env_file
from envguard.auditor import audit_env
from envguard.reporter import format_validation  # reuse similar formatting pattern
from envguard.output import run_and_exit


@click.command(name="audit")
@click.argument("env_files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format for audit results.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with non-zero status if any warnings are found (not just errors).",
)
@click.pass_context
def audit_cmd(ctx: click.Context, env_files: tuple, output_format: str, strict: bool) -> None:
    """Audit one or more .env files for security and quality issues.

    Checks for empty secrets, placeholder values, weak secret lengths,
    and other common problems.

    ENV_FILES: one or more paths to .env files to audit.
    """
    combined: dict[str, str] = {}
    for path in env_files:
        parsed = parse_env_file(Path(path))
        combined.update(parsed)

    result = audit_env(combined)

    if output_format == "json":
        import json
        from envguard.auditor import errors, warnings

        data = {
            "has_issues": result.has_issues,
            "errors": [
                {"key": i.key, "message": i.message, "severity": i.severity}
                for i in errors(result)
            ],
            "warnings": [
                {"key": i.key, "message": i.message, "severity": i.severity}
                for i in warnings(result)
            ],
        }
        click.echo(json.dumps(data, indent=2))
    else:
        _print_text(result)

    # Determine exit code
    from envguard.auditor import errors, warnings as get_warnings

    has_errors = bool(errors(result))
    has_warnings = bool(get_warnings(result))

    if has_errors or (strict and has_warnings):
        ctx.exit(1)


def _print_text(result) -> None:
    """Print audit results in human-readable text format."""
    from envguard.auditor import errors, warnings

    err_list = errors(result)
    warn_list = warnings(result)

    if not result.has_issues:
        click.secho("✔ No audit issues found.", fg="green")
        return

    if err_list:
        click.secho(f"Errors ({len(err_list)}):", fg="red", bold=True)
        for issue in err_list:
            click.secho(f"  [ERROR] {issue.key}: {issue.message}", fg="red")

    if warn_list:
        click.secho(f"Warnings ({len(warn_list)}):", fg="yellow", bold=True)
        for issue in warn_list:
            click.secho(f"  [WARN]  {issue.key}: {issue.message}", fg="yellow")
