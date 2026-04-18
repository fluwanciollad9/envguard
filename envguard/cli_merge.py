"""CLI sub-command: merge multiple .env files with precedence."""
from __future__ import annotations
import sys
import click
from envguard.parser import parse_env_file
from envguard.merger import merge_envs


@click.command("merge")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Write merged env to file instead of stdout.")
@click.option("--show-overrides", is_flag=True, default=False, help="Print override log to stderr.")
def merge_cmd(files: tuple, output: str | None, show_overrides: bool) -> None:
    """Merge FILE... in order (last file wins) and emit the result."""
    sources = []
    for path in files:
        try:
            env = parse_env_file(path)
        except OSError as exc:
            click.echo(f"error: {exc}", err=True)
            sys.exit(1)
        sources.append((path, env))

    result = merge_envs(sources)

    if show_overrides and result.overrides:
        click.echo("# Override log:", err=True)
        for key, old_src, new_src, new_val in result.overrides:
            click.echo(f"#  {key}: {old_src!r} -> {new_src!r} = {new_val!r}", err=True)

    lines = [f"{k}={v}" for k, v in sorted(result.merged.items())]
    content = "\n".join(lines) + "\n"

    if output:
        with open(output, "w") as fh:
            fh.write(content)
        click.echo(f"Merged {len(result.merged)} keys into {output}")
    else:
        click.echo(content, nl=False)
