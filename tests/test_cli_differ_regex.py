"""Integration tests for the regex-diff CLI command."""
from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envguard.cli_differ_regex import regex_diff_cmd


def write_env(tmp_path, name: str, content: str):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


@pytest.fixture()
def runner():
    return CliRunner()


def test_identical_files_exits_zero(tmp_path, runner):
    src = write_env(tmp_path, "a.env", "DB_HOST=localhost\nAPP=x\n")
    tgt = write_env(tmp_path, "b.env", "DB_HOST=localhost\nAPP=x\n")
    result = runner.invoke(regex_diff_cmd, [src, tgt, "--pattern", "^DB_"])
    assert result.exit_code == 0


def test_diff_detected_in_text(tmp_path, runner):
    src = write_env(tmp_path, "a.env", "DB_HOST=localhost\n")
    tgt = write_env(tmp_path, "b.env", "DB_HOST=prod-db\n")
    result = runner.invoke(regex_diff_cmd, [src, tgt, "--pattern", "^DB_"])
    assert "DB_HOST" in result.output


def test_strict_exits_nonzero_on_diff(tmp_path, runner):
    src = write_env(tmp_path, "a.env", "DB_HOST=localhost\n")
    tgt = write_env(tmp_path, "b.env", "DB_HOST=prod-db\n")
    result = runner.invoke(regex_diff_cmd, [src, tgt, "--pattern", "^DB_", "--strict"])
    assert result.exit_code == 1


def test_strict_exits_zero_when_no_diff(tmp_path, runner):
    src = write_env(tmp_path, "a.env", "DB_HOST=localhost\n")
    tgt = write_env(tmp_path, "b.env", "DB_HOST=localhost\n")
    result = runner.invoke(regex_diff_cmd, [src, tgt, "--pattern", "^DB_", "--strict"])
    assert result.exit_code == 0


def test_json_output_structure(tmp_path, runner):
    src = write_env(tmp_path, "a.env", "DB_HOST=localhost\nAPP=x\n")
    tgt = write_env(tmp_path, "b.env", "DB_HOST=prod-db\nAPP=x\n")
    result = runner.invoke(regex_diff_cmd, [src, tgt, "--pattern", "^DB_", "--format", "json"])
    data = json.loads(result.output)
    assert "pattern" in data
    assert "changes" in data
    assert "matched_keys" in data


def test_non_matching_keys_not_reported(tmp_path, runner):
    src = write_env(tmp_path, "a.env", "DB_HOST=localhost\nAPP=changed\n")
    tgt = write_env(tmp_path, "b.env", "DB_HOST=localhost\nAPP=other\n")
    result = runner.invoke(regex_diff_cmd, [src, tgt, "--pattern", "^DB_", "--format", "json"])
    data = json.loads(result.output)
    assert data["has_differences"] is False
    assert "APP" not in data["matched_keys"]
