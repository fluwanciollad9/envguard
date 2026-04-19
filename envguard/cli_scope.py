"""CLI command for scope filtering of .env files."""
from __future__ import annotations
import json
import sys
import click
from envguard.parser import parse_env_file
from envguard.scoper import scope_env


@click.command("scope")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("scope")
@click.option("--strip-prefix", is_flag=True, default=False, help="Remove prefix from matched keys.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Case-sensitive prefix matching.")
@click.option("--unmatched", "show_unmatched", is_flag=True, default=False, help="Show unmatched keys instead.")
@click.option("--format", "fmt", type=click.Choice(["text", "json", "dotenv"]), default="text")
def scope_cmd(
    env_file: str,
    scope: str,
    strip_prefix: bool,
    case_sensitive: bool,
    show_unmatched: bool,
    fmt: str,
) -> None:
    """Filter keys from ENV_FILE by SCOPE prefix."""
    env = parse_env_file(env_file)
    result = scope_env(env, scope, strip_prefix=strip_prefix, case_sensitive=case_sensitive)

    target = result.unmatched if show_unmatched else result.matched

    if fmt == "json":
        click.echo(json.dumps({
            "scope": result.scope,
            "strip_prefix": strip_prefix,
            "keys": target,
            "summary": result.summary(),
        }, indent=2))
    elif fmt == "dotenv":
        for k, v in target.items():
            click.echo(f"{k}={v}")
    else:
        click.echo(result.summary())
        if not target:
            click.echo("  (none)")
        for k, v in target.items():
            click.echo(f"  {k}={v}")

    sys.exit(0 if target else 1)
