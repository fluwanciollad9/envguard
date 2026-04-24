"""Integration tests for the rotate CLI command."""
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envguard.cli_rotate import rotate_cmd


def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


@pytest.fixture()
def runner():
    return CliRunner()


def test_rename_prints_new_key(runner, tmp_path):
    env_file = write_env(tmp_path, "OLD_KEY=hello\nOTHER=world\n")
    result = runner.invoke(rotate_cmd, [str(env_file), "--map", "OLD_KEY=NEW_KEY"])
    assert result.exit_code == 0
    assert "NEW_KEY=hello" in result.output


def test_rename_in_place_writes_file(runner, tmp_path):
    env_file = write_env(tmp_path, "OLD_KEY=hello\n")
    runner.invoke(rotate_cmd, [str(env_file), "--map", "OLD_KEY=NEW_KEY", "--in-place"])
    content = env_file.read_text()
    assert "NEW_KEY=hello" in content
    assert "OLD_KEY" not in content


def test_dry_run_does_not_write(runner, tmp_path):
    env_file = write_env(tmp_path, "OLD_KEY=hello\n")
    runner.invoke(
        rotate_cmd,
        [str(env_file), "--map", "OLD_KEY=NEW_KEY", "--in-place", "--dry-run"],
    )
    content = env_file.read_text()
    assert "OLD_KEY=hello" in content


def test_json_output_structure(runner, tmp_path):
    env_file = write_env(tmp_path, "OLD_KEY=hello\nOTHER=world\n")
    result = runner.invoke(
        rotate_cmd,
        [str(env_file), "--map", "OLD_KEY=NEW_KEY", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "rotated" in data
    assert "renamed" in data
    assert ["OLD_KEY", "NEW_KEY"] in data["renamed"]


def test_not_found_exits_nonzero(runner, tmp_path):
    env_file = write_env(tmp_path, "EXISTING=val\n")
    result = runner.invoke(rotate_cmd, [str(env_file), "--map", "MISSING=NEW"])
    assert result.exit_code == 1


def test_text_format_shows_arrow(runner, tmp_path):
    env_file = write_env(tmp_path, "OLD=v\n")
    result = runner.invoke(
        rotate_cmd,
        [str(env_file), "--map", "OLD=NEW", "--format", "text"],
    )
    assert "OLD -> NEW" in result.output
