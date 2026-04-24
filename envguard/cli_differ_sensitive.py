"""CLI command: envguard sensitive-diff <source> <target>"""
from __future__ import annotations

import json
import sys

import click

from envguard.differ_sensitive import diff_sensitive, SensitiveDiffEntry
from envguard.parser import parse_env_file


def _render_text(entries: list[SensitiveDiffEntry], redact: bool) -> str:
    lines: list[str] = []
    for entry in entries:
        tag = "[SENSITIVE]" if entry.is_sensitive else "[plain]"
        if entry.is_added:
            new = "***" if (redact and entry.is_sensitive) else entry.new_value
            lines.append(f"+ {entry.key}={new}  {tag}")
        elif entry.is_removed:
            lines.append(f"- {entry.key}  {tag}")
        else:
            old = "***" if (redact and entry.is_sensitive) else entry.old_value
            new = "***" if (redact and entry.is_sensitive) else entry.new_value
            lines.append(f"~ {entry.key}: {old} -> {new}  {tag}")
    return "\n".join(lines)


def _entry_to_dict(entry: SensitiveDiffEntry, redact: bool) -> dict:
    def maybe_redact(val: str | None) -> str | None:
        if val is None:
            return None
        return "***" if (redact and entry.is_sensitive) else val

    return {
        "key": entry.key,
        "is_sensitive": entry.is_sensitive,
        "old_value": maybe_redact(entry.old_value),
        "new_value": maybe_redact(entry.new_value),
        "change": (
            "added" if entry.is_added
            else "removed" if entry.is_removed
            else "modified"
        ),
    }


@click.command("sensitive-diff")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--redact", is_flag=True, default=False, help="Mask sensitive values in output.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero when sensitive changes exist.")
def sensitive_diff_cmd(source: str, target: str, fmt: str, redact: bool, strict: bool) -> None:
    """Diff two .env files, flagging changes to sensitive keys."""
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)
    result = diff_sensitive(src_env, tgt_env)

    if fmt == "json":
        payload = {
            "summary": result.summary(),
            "changes": [_entry_to_dict(e, redact) for e in result.changes],
        }
        click.echo(json.dumps(payload, indent=2))
    else:
        if not result.has_changes:
            click.echo("No differences found.")
        else:
            click.echo(_render_text(result.changes, redact))
            click.echo(result.summary())

    if strict and result.sensitive_changes:
        sys.exit(1)
