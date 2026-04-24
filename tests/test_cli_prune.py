"""Integration tests for the envguard prune CLI command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envguard.cli_prune import prune_cmd


def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_prune_explicit_key_shows_removed(tmp_path, runner):
    env_file = write_env(tmp_path, "APP=hello\nDEBUG=true\n")
    result = runner.invoke(prune_cmd, [str(env_file), "--key", "DEBUG"])
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_prune_empty_removes_empty_keys(tmp_path, runner):
    env_file = write_env(tmp_path, "APP=hello\nEMPTY=\n")
    result = runner.invoke(prune_cmd, [str(env_file), "--empty"])
    assert result.exit_code == 0
    assert "EMPTY" in result.output


def test_prune_pattern_removes_matching_values(tmp_path, runner):
    env_file = write_env(tmp_path, "APP=hello\nPH=<change_me>\n")
    result = runner.invoke(prune_cmd, [str(env_file), "--pattern", r"<.*>"])
    assert result.exit_code == 0
    assert "PH" in result.output


def test_prune_in_place_writes_file(tmp_path, runner):
    env_file = write_env(tmp_path, "APP=hello\nDEBUG=true\n")
    runner.invoke(prune_cmd, [str(env_file), "--key", "DEBUG", "--in-place"])
    content = env_file.read_text()
    assert "DEBUG" not in content
    assert "APP=hello" in content


def test_prune_dry_run_does_not_write(tmp_path, runner):
    original = "APP=hello\nDEBUG=true\n"
    env_file = write_env(tmp_path, original)
    runner.invoke(prune_cmd, [str(env_file), "--key", "DEBUG", "--in-place", "--dry-run"])
    assert env_file.read_text() == original


def test_prune_json_output_structure(tmp_path, runner):
    env_file = write_env(tmp_path, "APP=hello\nDEBUG=true\n")
    result = runner.invoke(prune_cmd, [str(env_file), "--key", "DEBUG", "--format", "json"])
    data = json.loads(result.output)
    assert "removed" in data
    assert "DEBUG" in data["removed"]
    assert "remaining" in data
    assert data["was_changed"] is True


def test_prune_no_criterion_shows_error(tmp_path, runner):
    env_file = write_env(tmp_path, "APP=hello\n")
    result = runner.invoke(prune_cmd, [str(env_file)])
    assert result.exit_code != 0
