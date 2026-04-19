"""Tests for envguard.scoper and cli_scope."""
from __future__ import annotations
import json
import pytest
from click.testing import CliRunner
from envguard.scoper import scope_env, ScopeResult
from envguard.cli_scope import scope_cmd


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envguard",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_matched_keys_returned():
    result = scope_env(ENV, "DB")
    assert "DB_HOST" in result.matched
    assert "DB_PORT" in result.matched


def test_unmatched_keys_excluded_from_matched():
    result = scope_env(ENV, "DB")
    assert "APP_NAME" not in result.matched
    assert "SECRET_KEY" not in result.matched


def test_unmatched_contains_non_scope_keys():
    result = scope_env(ENV, "DB")
    assert "APP_NAME" in result.unmatched
    assert "SECRET_KEY" in result.unmatched


def test_strip_prefix_removes_scope():
    result = scope_env(ENV, "DB", strip_prefix=True)
    assert "HOST" in result.matched
    assert "PORT" in result.matched
    assert "DB_HOST" not in result.matched


def test_match_count():
    result = scope_env(ENV, "APP")
    assert result.match_count() == 2


def test_summary_string():
    result = scope_env(ENV, "DB")
    assert "DB" in result.summary()
    assert "2" in result.summary()


def test_no_match_returns_empty():
    result = scope_env(ENV, "REDIS")
    assert result.matched == {}
    assert len(result.unmatched) == len(ENV)


def write_env(tmp_path, content: str):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_cli_text_output(tmp_path):
    f = write_env(tmp_path, "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=x\n")
    runner = CliRunner()
    res = runner.invoke(scope_cmd, [f, "DB"])
    assert res.exit_code == 0
    assert "DB_HOST" in res.output


def test_cli_json_output(tmp_path):
    f = write_env(tmp_path, "DB_HOST=localhost\nAPP_NAME=x\n")
    runner = CliRunner()
    res = runner.invoke(scope_cmd, [f, "DB", "--format", "json"])
    data = json.loads(res.output)
    assert "DB_HOST" in data["keys"]
    assert data["scope"] == "DB"


def test_cli_dotenv_output(tmp_path):
    f = write_env(tmp_path, "DB_HOST=localhost\nDB_PORT=5432\n")
    runner = CliRunner()
    res = runner.invoke(scope_cmd, [f, "DB", "--format", "dotenv"])
    assert "DB_HOST=localhost" in res.output


def test_cli_no_match_exits_one(tmp_path):
    f = write_env(tmp_path, "APP_NAME=x\n")
    runner = CliRunner()
    res = runner.invoke(scope_cmd, [f, "REDIS"])
    assert res.exit_code == 1
