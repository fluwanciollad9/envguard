"""CLI sub-command: envguard export — render an .env file in another format."""
from __future__ import annotations
import sys
import click
from envguard.parser import parse_env_file
from envguard.exporter import export_env, ExportError, SUPPORTED_FORMATS


@click.command("export")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", "fmt",
    type=click.Choice(list(SUPPORTED_FORMATS), case_sensitive=False),
    default="dotenv",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Write output to file instead of stdout.",
)
def export_cmd(env_file: str, fmt: str, output: str | None) -> None:
    """Export ENV_FILE contents in the chosen format."""
    try:
        env = parse_env_file(env_file)
    except OSError as exc:
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(1)

    try:
        result = export_env(env, fmt)
    except ExportError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    if output:
        try:
            with open(output, "w", encoding="utf-8") as fh:
                fh.write(result)
                if result:
                    fh.write("\n")
            click.echo(f"Exported to {output}")
        except OSError as exc:
            click.echo(f"Error writing output: {exc}", err=True)
            sys.exit(1)
    else:
        click.echo(result)
