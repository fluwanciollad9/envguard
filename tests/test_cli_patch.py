import json
from pathlib import Path
from click.testing import CliRunner
from envguard.cli_patch import patch_cmd


def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_patch_prints_change(tmp_path):
    f = write_env(tmp_path, "PORT=5432\nHOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(patch_cmd, [str(f), "--set", "PORT=9999"])
    assert result.exit_code == 0
    assert "PORT" in result.output
    assert "9999" in result.output


def test_patch_in_place_writes_file(tmp_path):
    f = write_env(tmp_path, "PORT=5432\n")
    runner = CliRunner()
    runner.invoke(patch_cmd, [str(f), "--set", "PORT=8080", "--in-place"])
    assert "PORT=8080" in f.read_text()


def test_dry_run_does_not_write(tmp_path):
    f = write_env(tmp_path, "PORT=5432\n")
    runner = CliRunner()
    runner.invoke(patch_cmd, [str(f), "--set", "PORT=8080", "--in-place", "--dry-run"])
    assert "PORT=5432" in f.read_text()


def test_not_found_reported(tmp_path):
    f = write_env(tmp_path, "PORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(patch_cmd, [str(f), "--set", "GHOST=x"])
    assert "Not found" in result.output or "GHOST" in result.output


def test_json_output(tmp_path):
    f = write_env(tmp_path, "PORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(patch_cmd, [str(f), "--set", "PORT=7777", "--format", "json"])
    data = json.loads(result.output)
    assert data["was_changed"] is True
    assert data["applied"][0]["key"] == "PORT"


def test_invalid_pair_exits_one(tmp_path):
    f = write_env(tmp_path, "PORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(patch_cmd, [str(f), "--set", "BADPAIR"])
    assert result.exit_code == 1
