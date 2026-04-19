"""CLI integration tests for the keydiff command."""
import json
import pytest
from click.testing import CliRunner
from envguard.cli_differ_keys import keydiff_cmd


def write_env(path, content):
    path.write_text(content)
    return str(path)


@pytest.fixture
def runner():
    return CliRunner()


def test_identical_files_exits_zero(runner, tmp_path):
    a = write_env(tmp_path / "a.env", "APP=1\nDB=sqlite\n")
    b = write_env(tmp_path / "b.env", "APP=1\nDB=sqlite\n")
    result = runner.invoke(keydiff_cmd, [a, b])
    assert result.exit_code == 0
    assert "identical" in result.output


def test_missing_key_shown(runner, tmp_path):
    a = write_env(tmp_path / "a.env", "APP=1\nDEBUG=true\n")
    b = write_env(tmp_path / "b.env", "APP=1\n")
    result = runner.invoke(keydiff_cmd, [a, b])
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_strict_exits_nonzero_when_diff(runner, tmp_path):
    a = write_env(tmp_path / "a.env", "APP=1\nEXTRA=x\n")
    b = write_env(tmp_path / "b.env", "APP=1\n")
    result = runner.invoke(keydiff_cmd, [a, b, "--strict"])
    assert result.exit_code == 1


def test_strict_exits_zero_when_identical(runner, tmp_path):
    a = write_env(tmp_path / "a.env", "APP=1\n")
    b = write_env(tmp_path / "b.env", "APP=1\n")
    result = runner.invoke(keydiff_cmd, [a, b, "--strict"])
    assert result.exit_code == 0


def test_json_output_structure(runner, tmp_path):
    a = write_env(tmp_path / "a.env", "APP=1\nFOO=bar\n")
    b = write_env(tmp_path / "b.env", "APP=1\nBAZ=qux\n")
    result = runner.invoke(keydiff_cmd, [a, b, "--format", "json"])
    data = json.loads(result.output)
    assert "only_in_source" in data
    assert "only_in_target" in data
    assert "common" in data
    assert "FOO" in data["only_in_source"]
    assert "BAZ" in data["only_in_target"]
    assert data["has_differences"] is True
