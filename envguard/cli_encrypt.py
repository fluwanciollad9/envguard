"""CLI commands for encrypting/decrypting .env files."""
from __future__ import annotations
import click
import json
import sys
from envguard.parser import parse_env_file
from envguard.encryptor import encrypt_env, decrypt_env


def _render(env: dict) -> str:
    return "\n".join(f"{k}={v}" for k, v in env.items()) + "\n"


@click.group("encrypt")
def encrypt_cmd():
    """Encrypt or decrypt sensitive values in a .env file."""


@encrypt_cmd.command("run")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("--passphrase", "-p", required=True, help="Encryption passphrase.")
@click.option("--in-place", is_flag=True, help="Overwrite the source file.")
@click.option("--dry-run", is_flag=True, help="Print result without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def run_cmd(envfile, passphrase, in_place, dry_run, fmt):
    """Encrypt sensitive keys in ENVFILE."""
    env = parse_env_file(envfile)
    result = encrypt_env(env, passphrase)
    if fmt == "json":
        click.echo(json.dumps({"encrypted": result.encrypted, "count": result.encrypt_count}))
    else:
        if dry_run or not in_place:
            click.echo(_render(result.encrypted), nl=False)
        if in_place and not dry_run:
            with open(envfile, "w") as f:
                f.write(_render(result.encrypted))
            click.echo(result.summary())


@encrypt_cmd.command("decrypt")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("--passphrase", "-p", required=True, help="Decryption passphrase.")
@click.option("--in-place", is_flag=True, help="Overwrite the source file.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def decrypt_cmd(envfile, passphrase, in_place, fmt):
    """Decrypt encrypted keys in ENVFILE."""
    env = parse_env_file(envfile)
    decrypted = decrypt_env(env, passphrase)
    if fmt == "json":
        click.echo(json.dumps(decrypted))
    elif in_place:
        with open(envfile, "w") as f:
            f.write(_render(decrypted))
        click.echo("Decryption complete.")
    else:
        click.echo(_render(decrypted), nl=False)
