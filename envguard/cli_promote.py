"""CLI command: promote keys from one .env file into another."""
import click
import json
from envguard.parser import parse_env_file
from envguard.promoter import promote_env, render_promoted


@click.command("promote")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, required=True, help="Key(s) to promote.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in target.")
@click.option("--in-place", is_flag=True, default=False, help="Write result back to target file.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would change without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def promote_cmd(source, target, keys, overwrite, in_place, dry_run, fmt):
    """Promote specific keys from SOURCE .env into TARGET .env."""
    src = parse_env_file(source)
    tgt = parse_env_file(target)

    result = promote_env(
        src, tgt,
        keys=list(keys),
        overwrite=overwrite,
        source_label=source,
        target_label=target,
    )

    if fmt == "json":
        click.echo(json.dumps({
            "promoted": result.promoted,
            "skipped": result.skipped,
            "overwritten": result.overwritten,
            "was_changed": result.was_changed(),
            "summary": result.summary(),
        }, indent=2))
    else:
        click.echo(result.summary())
        for k, v in result.promoted.items():
            marker = "(overwrite)" if k in result.overwritten else "(new)"
            click.echo(f"  {k}={v}  {marker}")
        if result.skipped:
            for k in result.skipped:
                click.echo(f"  {k}  (skipped)")

    if result.was_changed() and in_place and not dry_run:
        rendered = render_promoted(tgt, result)
        with open(target, "w") as fh:
            fh.write(rendered)

    raise SystemExit(0 if result.was_changed() or not result.skipped else 0)
