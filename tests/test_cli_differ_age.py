"""CLI integration tests for age-diff command."""
from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from envguard.cli_differ_age import age_diff_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write_ts(tmp_path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def test_identical_files_exits_zero(runner, tmp_path):
    ts = {"KEY_A": 1000.0}
    src = write_ts(tmp_path, "src.json", ts)
    tgt = write_ts(tmp_path, "tgt.json", ts)
    result = runner.invoke(age_diff_cmd, [src, tgt])
    assert result.exit_code == 0
    assert "No age differences" in result.output


def test_diff_detected_in_text(runner, tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 5000.0})
    result = runner.invoke(age_diff_cmd, [src, tgt])
    assert result.exit_code == 0
    assert "KEY_A" in result.output


def test_strict_exits_nonzero_on_diff(runner, tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 9000.0})
    result = runner.invoke(age_diff_cmd, [src, tgt, "--strict"])
    assert result.exit_code == 1


def test_strict_exits_zero_when_clean(runner, tmp_path):
    ts = {"KEY_A": 1000.0}
    src = write_ts(tmp_path, "src.json", ts)
    tgt = write_ts(tmp_path, "tgt.json", ts)
    result = runner.invoke(age_diff_cmd, [src, tgt, "--strict"])
    assert result.exit_code == 0


def test_json_output_structure(runner, tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 2000.0})
    result = runner.invoke(age_diff_cmd, [src, tgt, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "changed" in data
    assert "has_differences" in data
    assert data["has_differences"] is True


def test_missing_file_exits_one(runner, tmp_path):
    result = runner.invoke(age_diff_cmd, [str(tmp_path / "ghost.json"), str(tmp_path / "ghost2.json")])
    assert result.exit_code == 1


def test_threshold_suppresses_small_deltas(runner, tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 1002.0})
    result = runner.invoke(age_diff_cmd, [src, tgt, "--threshold", "10", "--strict"])
    assert result.exit_code == 0
