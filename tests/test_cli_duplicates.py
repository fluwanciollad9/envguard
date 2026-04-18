from __future__ import annotations
import json
from pathlib import Path
from click.testing import CliRunner
from envguard.cli_duplicates import duplicates_cmd


def write_env(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_no_duplicates_exits_zero(tmp_path):
    path = write_env(tmp_path, "FOO=1\nBAR=2\n")
    runner = CliRunner()
    result = runner.invoke(duplicates_cmd, [path])
    assert result.exit_code == 0
    assert "No duplicate" in result.output


def test_duplicates_found_text_output(tmp_path):
    path = write_env(tmp_path, "FOO=1\nFOO=2\n")
    runner = CliRunner()
    result = runner.invoke(duplicates_cmd, [path])
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_strict_exits_nonzero_on_duplicates(tmp_path):
    path = write_env(tmp_path, "FOO=1\nFOO=2\n")
    runner = CliRunner()
    result = runner.invoke(duplicates_cmd, ["--strict", path])
    assert result.exit_code == 1


def test_strict_exits_zero_when_clean(tmp_path):
    path = write_env(tmp_path, "FOO=1\nBAR=2\n")
    runner = CliRunner()
    result = runner.invoke(duplicates_cmd, ["--strict", path])
    assert result.exit_code == 0


def test_json_format_no_duplicates(tmp_path):
    path = write_env(tmp_path, "A=1\n")
    runner = CliRunner()
    result = runner.invoke(duplicates_cmd, ["--format", "json", path])
    data = json.loads(result.output)
    assert data["has_duplicates"] is False
    assert data["duplicates"] == {}


def test_json_format_with_duplicates(tmp_path):
    path = write_env(tmp_path, "KEY=a\nKEY=b\n")
    runner = CliRunner()
    result = runner.invoke(duplicates_cmd, ["--format", "json", path])
    data = json.loads(result.output)
    assert data["has_duplicates"] is True
    assert "KEY" in data["duplicates"]
