"""CLI command: envguard keydiff — compare key sets across two .env files."""
from __future__ import annotations
import json
import sys
import click
from envguard.parser import parse_env_file
from envguard.differ_keys import diff_keys


@click.command("keydiff")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--strict", is_flag=True, help="Exit 1 if any key differences found.")
def keydiff_cmd(source: str, target: str, fmt: str, strict: bool) -> None:
    """Show keys present in SOURCE but not TARGET, and vice-versa."""
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)
    result = diff_keys(src_env, tgt_env, source_name=source, target_name=target)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "source": source,
                    "target": target,
                    "only_in_source": sorted(result.only_in_source),
                    "only_in_target": sorted(result.only_in_target),
                    "common": sorted(result.common),
                    "has_differences": result.has_differences(),
                },
                indent=2,
            )
        )
    else:
        if not result.has_differences():
            click.echo("Key sets are identical.")
        else:
            for k in sorted(result.only_in_source):
                click.echo(f"< {k}  (only in {source})")
            for k in sorted(result.only_in_target):
                click.echo(f"> {k}  (only in {target})")

    if strict and result.has_differences():
        sys.exit(1)
