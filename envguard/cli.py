"""CLI entry point for envguard."""
import sys
import click
from envguard.parser import parse_env_file
from envguard.differ import diff_envs


@click.group()
def cli():
    """envguard — validate and diff .env files across environments."""


@cli.command()
@click.argument('base_env', type=click.Path(exists=True))
@click.argument('target_env', type=click.Path(exists=True))
@click.option('--no-values', is_flag=True, default=False,
              help='Hide actual values in diff output.')
def diff(base_env: str, target_env: str, no_values: bool):
    """Diff BASE_ENV against TARGET_ENV and report differences."""
    base = parse_env_file(base_env)
    target = parse_env_file(target_env)
    result = diff_envs(base, target)

    if not result.has_differences:
        click.secho('No differences found.', fg='green')
        sys.exit(0)

    if result.missing_keys:
        click.secho('\nMissing keys (in base, not in target):', fg='red', bold=True)
        for key in result.missing_keys:
            click.echo(f'  - {key}')

    if result.extra_keys:
        click.secho('\nExtra keys (in target, not in base):', fg='yellow', bold=True)
        for key in result.extra_keys:
            click.echo(f'  + {key}')

    if result.changed_keys:
        click.secho('\nChanged values:', fg='cyan', bold=True)
        for key, (base_val, target_val) in result.changed_keys.items():
            if no_values:
                click.echo(f'  ~ {key}')
            else:
                click.echo(f'  ~ {key}: {base_val!r} -> {target_val!r}')

    sys.exit(1)


if __name__ == '__main__':
    cli()
