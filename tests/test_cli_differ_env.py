"""CLI integration tests for the envdiff command."""
import json
import pytest
from click.testing import CliRunner
from envguard.cli_differ_env import envdiff_cmd


def write_env(path, content):
    path.write_text(content)


@pytest.fixture
def runner():
    return CliRunner()


def test_identical_files_exits_zero(tmp_path, runner):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    write_env(f1, "A=1\nB=2\n")
    write_env(f2, "A=1\nB=2\n")
    result = runner.invoke(envdiff_cmd, [str(f1), str(f2)])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_added_key_shown(tmp_path, runner):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    write_env(f1, "A=1\n")
    write_env(f2, "A=1\nB=added\n")
    result = runner.invoke(envdiff_cmd, [str(f1), str(f2)])
    assert "+ B=added" in result.output


def test_removed_key_shown(tmp_path, runner):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    write_env(f1, "A=1\nB=gone\n")
    write_env(f2, "A=1\n")
    result = runner.invoke(envdiff_cmd, [str(f1), str(f2)])
    assert "- B=gone" in result.output


def test_strict_exits_nonzero_when_diff(tmp_path, runner):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    write_env(f1, "A=1\n")
    write_env(f2, "A=2\n")
    result = runner.invoke(envdiff_cmd, [str(f1), str(f2), "--strict"])
    assert result.exit_code == 1


def test_json_output_structure(tmp_path, runner):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    write_env(f1, "A=old\n")
    write_env(f2, "A=new\nB=extra\n")
    result = runner.invoke(envdiff_cmd, [str(f1), str(f2), "--format", "json"])
    data = json.loads(result.output)
    assert "added" in data
    assert "removed" in data
    assert "modified" in data
    assert data["modified"]["A"]["old"] == "old"
    assert data["modified"]["A"]["new"] == "new"
