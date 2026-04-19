"""CLI command: envguard envdiff — compare two .env files with full value reporting."""
import json
import click
from envguard.parser import parse_env_file
from envguard.differ_env import diff_env_files


@click.command("envdiff")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--strict", is_flag=True, help="Exit with code 1 if differences found.")
@click.option("--show-unchanged", is_flag=True, help="Also display unchanged keys.")
def envdiff_cmd(source: str, target: str, fmt: str, strict: bool, show_unchanged: bool) -> None:
    """Compare SOURCE and TARGET .env files, showing added, removed, and modified keys."""
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)
    result = diff_env_files(src_env, tgt_env, source_file=source, target_file=target)

    if fmt == "json":
        data = {
            "source": source,
            "target": target,
            "added": result.added,
            "removed": result.removed,
            "modified": {k: {"old": v[0], "new": v[1]} for k, v in result.modified.items()},
            "summary": result.summary(),
        }
        if show_unchanged:
            data["unchanged"] = result.unchanged
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"Comparing {source} -> {target}")
        for key, val in result.added.items():
            click.echo(f"  + {key}={val}")
        for key, val in result.removed.items():
            click.echo(f"  - {key}={val}")
        for key, (old, new) in result.modified.items():
            click.echo(f"  ~ {key}: {old!r} -> {new!r}")
        if show_unchanged:
            for key, val in result.unchanged.items():
                click.echo(f"    {key}={val}")
        click.echo(result.summary())

    if strict and result.has_differences():
        raise SystemExit(1)
