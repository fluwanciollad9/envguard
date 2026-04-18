"""Integration tests for the rename CLI command."""
import json
import os
from click.testing import CliRunner
from envguard.cli_rename import rename_cmd


def write_env(tmp_path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_rename_prints_new_key(tmp_path):
    env_file = write_env(tmp_path, "OLD_KEY=hello\nKEEP=world\n")
    runner = CliRunner()
    result = runner.invoke(rename_cmd, [env_file, "--rename", "OLD_KEY=NEW_KEY"])
    assert result.exit_code == 0
    assert "OLD_KEY -> NEW_KEY" in result.output


def test_rename_in_place_writes_file(tmp_path):
    env_file = write_env(tmp_path, "OLD=1\nFOO=2\n")
    runner = CliRunner()
    result = runner.invoke(rename_cmd, [env_file, "--rename", "OLD=NEW", "--in-place"])
    assert result.exit_code == 0
    content = open(env_file).read()
    assert "NEW=1" in content
    assert "OLD=" not in content


def test_rename_dry_run_does_not_write(tmp_path):
    env_file = write_env(tmp_path, "OLD=1\n")
    original = open(env_file).read()
    runner = CliRunner()
    result = runner.invoke(rename_cmd, [env_file, "--rename", "OLD=NEW", "--dry-run"])
    assert result.exit_code == 0
    assert open(env_file).read() == original
    assert "dry-run" in result.output


def test_rename_json_output(tmp_path):
    env_file = write_env(tmp_path, "OLD=1\n")
    runner = CliRunner()
    result = runner.invoke(rename_cmd, [env_file, "--rename", "OLD=NEW", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert ["OLD", "NEW"] in data["changes"]


def test_rename_missing_key_reported(tmp_path):
    env_file = write_env(tmp_path, "FOO=1\n")
    runner = CliRunner()
    result = runner.invoke(rename_cmd, [env_file, "--rename", "MISSING=NEW"])
    assert "MISSING" in result.output or "MISSING" in (result.stderr or "")


def test_no_pairs_exits_nonzero(tmp_path):
    env_file = write_env(tmp_path, "FOO=1\n")
    runner = CliRunner()
    result = runner.invoke(rename_cmd, [env_file])
    assert result.exit_code != 0
