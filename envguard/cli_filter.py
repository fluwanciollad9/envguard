import click
import json
from envguard.parser import parse_env_file
from envguard.filterer import filter_env


@click.command("filter")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("pattern")
@click.option("--invert", "-v", is_flag=True, help="Return keys that do NOT match.")
@click.option(
    "--key-only/--key-and-value",
    default=True,
    show_default=True,
    help="Match against key only, or key=value pair.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "dotenv"]),
    default="dotenv",
    show_default=True,
)
@click.option("--summary", "show_summary", is_flag=True, help="Print summary line.")
def filter_cmd(
    env_file: str,
    pattern: str,
    invert: bool,
    key_only: bool,
    fmt: str,
    show_summary: bool,
) -> None:
    """Filter .env keys by PATTERN (regex) and print matched entries."""
    try:
        env = parse_env_file(env_file)
        result = filter_env(env, pattern, invert=invert, key_only=key_only)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "pattern": result.pattern,
                    "matched": result.matched,
                    "excluded": list(result.excluded.keys()),
                    "match_count": result.match_count(),
                },
                indent=2,
            )
        )
    elif fmt == "text":
        for key in result.matched:
            click.echo(key)
    else:  # dotenv
        for key, value in result.matched.items():
            click.echo(f"{key}={value}")

    if show_summary:
        click.echo(result.summary(), err=True)
