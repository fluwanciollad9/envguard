"""CLI command: envguard cascade — merge env files with origin tracking."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

import click

from envguard.cascader import cascade_envs
from envguard.parser import parse_env_file


def _render_text(
    result,
    source_paths: List[Path],
    show_origins: bool,
) -> str:
    lines: List[str] = []
    for key, value in sorted(result.env.items()):
        if show_origins:
            src_idx = result.source_for(key)
            src_name = source_paths[src_idx].name
            lines.append(f"{key}={value}  # from {src_name}")
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


@click.command("cascade")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format",
    "fmt",
    default="dotenv",
    type=click.Choice(["dotenv", "json", "text"]),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--show-origins",
    is_flag=True,
    default=False,
    help="Annotate each key with its source file (text/dotenv only).",
)
@click.option(
    "--summary",
    "show_summary",
    is_flag=True,
    default=False,
    help="Print a one-line summary to stderr.",
)
def cascade_cmd(files, fmt, show_origins, show_summary):
    """Cascade FILES left-to-right; later files override earlier ones."""
    paths = [Path(f) for f in files]
    sources = [parse_env_file(str(p)) for p in paths]
    result = cascade_envs(sources)

    if show_summary:
        click.echo(result.summary(), err=True)

    if fmt == "json":
        payload = {
            "env": result.env,
            "override_count": result.override_count,
            "origins": {
                k: {"value": v, "source": paths[i].name}
                for k, (v, i) in result.origins.items()
            },
        }
        click.echo(json.dumps(payload, indent=2))
    else:
        click.echo(_render_text(result, paths, show_origins), nl=False)
