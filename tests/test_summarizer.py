"""Tests for envguard.summarizer."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envguard.summarizer import summarize_env, SummaryReport
from envguard.cli_summarize import summarize_cmd


# ---------------------------------------------------------------------------
# Unit tests for summarize_env
# ---------------------------------------------------------------------------

def test_total_keys_counted():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    report = summarize_env(env)
    assert report.total_keys == 3


def test_empty_key_detected():
    env = {"HOST": "localhost", "SECRET": ""}
    report = summarize_env(env)
    assert "SECRET" in report.empty_keys


def test_no_empty_keys_for_clean_env():
    env = {"HOST": "localhost", "PORT": "5432"}
    report = summarize_env(env)
    assert report.empty_keys == []


def test_placeholder_detected():
    env = {"API_KEY": "<your-api-key>", "HOST": "localhost"}
    report = summarize_env(env)
    assert "API_KEY" in report.placeholder_keys


def test_no_placeholders_for_real_values():
    env = {"HOST": "localhost", "PORT": "5432"}
    report = summarize_env(env)
    assert report.placeholder_keys == []


def test_score_is_numeric():
    env = {"HOST": "localhost"}
    report = summarize_env(env)
    assert 0.0 <= report.score <= 100.0


def test_grade_is_letter():
    env = {"HOST": "localhost"}
    report = summarize_env(env)
    assert report.grade in {"A", "B", "C", "D", "F"}


def test_summary_string_contains_score():
    env = {"HOST": "localhost"}
    report = summarize_env(env)
    assert "Score" in report.summary()


def test_summary_string_contains_total_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    report = summarize_env(env)
    assert "2" in report.summary()


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def write_env(tmp_path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_cli_text_output(tmp_path):
    env_file = write_env(tmp_path, "HOST=localhost\nPORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(summarize_cmd, [env_file])
    assert result.exit_code == 0
    assert "Total keys" in result.output


def test_cli_json_output(tmp_path):
    import json
    env_file = write_env(tmp_path, "HOST=localhost\nPORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(summarize_cmd, [env_file, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "total_keys" in data
    assert "score" in data
    assert "grade" in data


def test_cli_min_score_passes(tmp_path):
    env_file = write_env(tmp_path, "HOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(summarize_cmd, [env_file, "--min-score", "0"])
    assert result.exit_code == 0


def test_cli_min_score_fails(tmp_path):
    env_file = write_env(tmp_path, "HOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(summarize_cmd, [env_file, "--min-score", "999"])
    assert result.exit_code == 1
