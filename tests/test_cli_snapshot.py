"""Integration tests for snapshot CLI commands."""
import json
from pathlib import Path

from click.testing import CliRunner

from envguard.cli_snapshot import snapshot_cmd


def write_env(path, content):
    Path(path).write_text(content)


def test_save_creates_snapshot_file(tmp_path):
    env = str(tmp_path / ".env")
    out = str(tmp_path / "snap.json")
    write_env(env, "A=1\nB=2\n")
    runner = CliRunner()
    result = runner.invoke(snapshot_cmd, ["save", env, "-o", out])
    assert result.exit_code == 0
    assert Path(out).exists()
    assert "Snapshot saved" in result.output


def test_diff_no_changes_exits_zero(tmp_path):
    env = str(tmp_path / ".env")
    snap = str(tmp_path / "snap.json")
    write_env(env, "A=1\n")
    runner = CliRunner()
    runner.invoke(snapshot_cmd, ["save", env, "-o", snap])
    result = runner.invoke(snapshot_cmd, ["diff", env, "-s", snap])
    assert result.exit_code == 0


def test_diff_with_changes_exits_nonzero(tmp_path):
    env = str(tmp_path / ".env")
    snap = str(tmp_path / "snap.json")
    write_env(env, "A=1\n")
    runner = CliRunner()
    runner.invoke(snapshot_cmd, ["save", env, "-o", snap])
    write_env(env, "A=changed\n")
    result = runner.invoke(snapshot_cmd, ["diff", env, "-s", snap])
    assert result.exit_code != 0


def test_diff_missing_snapshot_exits_one(tmp_path):
    env = str(tmp_path / ".env")
    write_env(env, "A=1\n")
    runner = CliRunner()
    result = runner.invoke(snapshot_cmd, ["diff", env, "-s", str(tmp_path / "no.json")])
    assert result.exit_code == 1


def test_show_displays_keys(tmp_path):
    env = str(tmp_path / ".env")
    snap = str(tmp_path / "snap.json")
    write_env(env, "FOO=bar\nBAZ=qux\n")
    runner = CliRunner()
    runner.invoke(snapshot_cmd, ["save", env, "-o", snap])
    result = runner.invoke(snapshot_cmd, ["show", snap])
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "BAZ" in result.output
