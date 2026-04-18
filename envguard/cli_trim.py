"""CLI command for trimming trailing/leading whitespace from .env values."""
from __future__ import annotations
import sys
import click
from envguard.parser import parse_env_file
from envguard.trimmer import trim_env, render_trimmed, was_changed


@click.command("trim")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("--in-place", "-i", is_flag=True, help="Write changes back to file.")
@click.option("--dry-run", is_flag=True, help="Show what would change without writing.")
@click.option("--json", "use_json", is_flag=True, help="Output JSON report.")
def trim_cmd(envfile: str, in_place: bool, dry_run: bool, use_json: bool) -> None:
    """Trim leading/trailing whitespace from all values in ENVFILE."""
    env = parse_env_file(envfile)
    result = trim_env(env)

    if use_json:
        import json
        report = {
            "changed_keys": result.changed_keys,
            "was_changed": was_changed(result),
            "trimmed": result.trimmed,
        }
        click.echo(json.dumps(report, indent=2))
        sys.exit(1 if was_changed(result) else 0)

    if not was_changed(result):
        click.echo("No whitespace issues found.")
        sys.exit(0)

    click.echo(f"Keys with whitespace trimmed ({len(result.changed_keys)}):")
    for key in result.changed_keys:
        old = repr(result.original[key])
        new = repr(result.trimmed[key])
        click.echo(f"  {key}: {old} -> {new}")

    if dry_run:
        click.echo("Dry run — no changes written.")
        sys.exit(1)

    if in_place:
        rendered = render_trimmed(result.trimmed)
        with open(envfile, "w") as fh:
            fh.write(rendered)
        click.echo(f"Written: {envfile}")
        sys.exit(0)

    sys.exit(1)
