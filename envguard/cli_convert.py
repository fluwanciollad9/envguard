"""CLI command for envguard convert."""
from __future__ import annotations
import json
import sys
import click
from envguard.parser import parse_env_file
from envguard.converter import convert_env, ConvertError, SUPPORTED_FORMATS


@click.command("convert")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--to",
    "target_format",
    required=True,
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    help="Target output format.",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Write output to file instead of stdout.",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
def convert_cmd(
    env_file: str,
    target_format: str,
    output: str | None,
    fmt: str,
) -> None:
    """Convert ENV_FILE to another format."""
    env = parse_env_file(env_file)
    try:
        result = convert_env(env, target_format)
    except ConvertError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "source_format": result.source_format,
                    "target_format": result.target_format,
                    "keys": len(result.env),
                    "output": result.output,
                },
                indent=2,
            )
        )
        return

    if output:
        with open(output, "w") as fh:
            fh.write(result.output)
        click.echo(f"Written to {output} ({result.summary()})")
    else:
        click.echo(result.output, nl=False)
