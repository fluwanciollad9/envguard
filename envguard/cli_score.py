"""CLI command: envguard score — health score for an env file."""
import json
import click
from envguard.parser import parse_env_file
from envguard.scorer import score_env


@click.command("score")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, default=False, help="Penalise non-uppercase keys.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--min-score", type=int, default=0, help="Exit non-zero if score is below this.")
def score_cmd(env_file: str, strict: bool, fmt: str, min_score: int) -> None:
    """Score ENV_FILE and report an overall health grade."""
    env = parse_env_file(env_file)
    result = score_env(env, strict=strict)

    if fmt == "json":
        click.echo(json.dumps({
            "score": result.total,
            "grade": result.grade,
            "breakdown": result.breakdown,
            "penalties": result.penalties,
        }, indent=2))
    else:
        click.echo(result.summary())
        if result.penalties:
            click.echo("Penalties:")
            for reason, pts in result.penalties.items():
                click.echo(f"  -{pts:>3}  {reason}")

    if result.total < min_score:
        raise SystemExit(1)
