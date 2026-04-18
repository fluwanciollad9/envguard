"""CLI command: envguard profile — display a profile of an .env file."""
from __future__ import annotations
import json
import sys
import click
from envguard.parser import parse_env_file
from envguard.profiler import profile_env


@click.command("profile")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--long-threshold", default=100, show_default=True,
              help="Character length above which a value is considered long.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]),
              default="text", show_default=True)
@click.option("--show-entropy", is_flag=True, default=False,
              help="Include per-key entropy scores in output.")
def profile_cmd(
    env_file: str,
    long_threshold: int,
    fmt: str,
    show_entropy: bool,
) -> None:
    """Display a statistical profile of ENV_FILE."""
    env = parse_env_file(env_file)
    result = profile_env(env, long_value_threshold=long_threshold)

    if fmt == "json":
        data = {
            "total_keys": result.total_keys,
            "empty_keys": result.empty_keys,
            "long_values": result.long_values,
            "avg_value_length": round(result.avg_value_length, 2),
        }
        if show_entropy:
            data["entropy_scores"] = {
                k: round(v, 4) for k, v in result.entropy_scores.items()
            }
        click.echo(json.dumps(data, indent=2))
        return

    # text output
    click.echo(result.summary())
    if result.empty_keys:
        click.echo("\nEmpty keys:")
        for k in result.empty_keys:
            click.echo(f"  - {k}")
    if result.long_values:
        click.echo(f"\nLong values (>{long_threshold} chars):")
        for k in result.long_values:
            click.echo(f"  - {k}")
    if show_entropy:
        click.echo("\nEntropy scores:")
        for k, score in sorted(result.entropy_scores.items(),
                               key=lambda x: -x[1]):
            click.echo(f"  {k}: {score:.4f}")
