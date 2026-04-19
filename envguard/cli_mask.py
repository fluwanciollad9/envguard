"""CLI command: envguard mask — print env with sensitive values masked."""
from __future__ import annotations
import json
import sys
import click
from envguard.parser import parse_env_file
from envguard.masker import mask_env, DEFAULT_MASK


@click.command("mask")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--mask", "mask_str", default=DEFAULT_MASK, show_default=True, help="Replacement string for sensitive values.")
@click.option("--key", "extra_keys", multiple=True, help="Additional key to mask (repeatable).")
@click.option("--in-place", is_flag=True, help="Overwrite the file with masked output.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
def mask_cmd(env_file: str, mask_str: str, extra_keys: tuple, in_place: bool, fmt: str) -> None:
    """Mask sensitive values in ENV_FILE."""
    env = parse_env_file(env_file)
    result = mask_env(env, mask=mask_str, keys=list(extra_keys))

    if fmt == "json":
        click.echo(json.dumps({
            "masked_keys": result.masked_keys,
            "env": result.masked,
            "summary": result.summary(),
        }, indent=2))
        sys.exit(0)

    lines = [f"{k}={v}" for k, v in result.masked.items()]
    output = "\n".join(lines)

    if in_place:
        with open(env_file, "w") as fh:
            fh.write(output + "\n")
        click.echo(result.summary())
    else:
        click.echo(output)
        if result.was_masked():
            click.echo(f"# {result.summary()}", err=True)

    sys.exit(0)
