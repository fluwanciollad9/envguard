"""CLI command for comparing sensitive key counts between two .env files."""

from __future__ import annotations

import json
import sys

import click

from envguard.differ_sensitive_counts import diff_sensitive_counts
from envguard.parser import parse_env_file


def _render_text(result) -> str:
    """Render a SensitiveCountDiff as a human-readable string."""
    lines: list[str] = []

    lines.append(
        f"Source sensitive keys : {result.source_sensitive_count}"
    )
    lines.append(
        f"Target sensitive keys : {result.target_sensitive_count}"
    )
    delta = result.sensitive_delta
    sign = "+" if delta >= 0 else ""
    lines.append(f"Delta                 : {sign}{delta}")
    lines.append("")

    if result.added_sensitive:
        lines.append("Added sensitive keys:")
        for k in sorted(result.added_sensitive):
            lines.append(f"  + {k}")

    if result.removed_sensitive:
        lines.append("Removed sensitive keys:")
        for k in sorted(result.removed_sensitive):
            lines.append(f"  - {k}")

    if result.has_regressions:
        lines.append("")
        lines.append("WARNING: sensitive key count has decreased (regression).")

    if not result.added_sensitive and not result.removed_sensitive:
        lines.append("No changes in sensitive key counts.")

    return "\n".join(lines)


def _render_json(result) -> str:
    """Render a SensitiveCountDiff as a JSON string."""
    payload = {
        "source_sensitive_count": result.source_sensitive_count,
        "target_sensitive_count": result.target_sensitive_count,
        "delta": result.sensitive_delta,
        "has_regressions": result.has_regressions,
        "added_sensitive": sorted(result.added_sensitive),
        "removed_sensitive": sorted(result.removed_sensitive),
    }
    return json.dumps(payload, indent=2)


@click.command("sensitive-counts")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 when a regression is detected.",
)
def sensitive_counts_cmd(source: str, target: str, fmt: str, strict: bool) -> None:
    """Compare the number of sensitive keys between SOURCE and TARGET .env files.

    A regression occurs when the target has fewer sensitive keys than the
    source, which may indicate that secrets have been accidentally removed or
    demoted to plain keys.
    """
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)

    result = diff_sensitive_counts(src_env, tgt_env)

    if fmt == "json":
        click.echo(_render_json(result))
    else:
        click.echo(_render_text(result))

    if strict and result.has_regressions:
        sys.exit(1)
