"""Integration tests for cli_pin commands."""
import json
from pathlib import Path

from click.testing import CliRunner

from envguard.cli_pin import pin_cmd


def write_env(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_lock_creates_file(tmp_path):
    env_file = tmp_path / ".env"
    write_env(env_file, "FOO=bar\nBAZ=qux\n")
    lock_file = tmp_path / "env.lock"
    runner = CliRunner()
    result = runner.invoke(pin_cmd, ["lock", str(env_file), "--output", str(lock_file)])
    assert result.exit_code == 0
    assert lock_file.exists()
    data = json.loads(lock_file.read_text())
    assert data["FOO"] == "bar"


def test_check_no_drift_exits_zero(tmp_path):
    env_file = tmp_path / ".env"
    write_env(env_file, "FOO=bar\n")
    lock_file = tmp_path / "env.lock"
    runner = CliRunner()
    runner.invoke(pin_cmd, ["lock", str(env_file), "--output", str(lock_file)])
    result = runner.invoke(pin_cmd, ["check", str(env_file), "--lock", str(lock_file)])
    assert result.exit_code == 0
    assert "no drift" in result.output


def test_check_drift_exits_nonzero(tmp_path):
    env_file = tmp_path / ".env"
    write_env(env_file, "FOO=bar\n")
    lock_file = tmp_path / "env.lock"
    runner = CliRunner()
    runner.invoke(pin_cmd, ["lock", str(env_file), "--output", str(lock_file)])
    write_env(env_file, "FOO=changed\n")
    result = runner.invoke(pin_cmd, ["check", str(env_file), "--lock", str(lock_file)])
    assert result.exit_code == 1
    assert "FOO" in result.output


def test_check_missing_lock_exits_one(tmp_path):
    env_file = tmp_path / ".env"
    write_env(env_file, "FOO=bar\n")
    runner = CliRunner()
    result = runner.invoke(pin_cmd, ["check", str(env_file), "--lock", str(tmp_path / "missing.lock")])
    assert result.exit_code == 1


def test_check_json_output(tmp_path):
    env_file = tmp_path / ".env"
    write_env(env_file, "FOO=bar\n")
    lock_file = tmp_path / "env.lock"
    runner = CliRunner()
    runner.invoke(pin_cmd, ["lock", str(env_file), "--output", str(lock_file)])
    write_env(env_file, "FOO=new\nEXTRA=yes\n")
    result = runner.invoke(pin_cmd, ["check", str(env_file), "--lock", str(lock_file), "--format", "json"])
    data = json.loads(result.output)
    assert "FOO" in data["drifted"]
    assert "EXTRA" in data["new_keys"]
    assert data["has_drift"] is True
