"""Tests for envguard.placeholder and cli_placeholder."""
from __future__ import annotations
import json
import os
import pytest
from click.testing import CliRunner
from envguard.placeholder import find_placeholders, _is_placeholder
from envguard.cli_placeholder import placeholder_cmd


# --- unit tests ---

def test_no_placeholders_for_real_values():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = find_placeholders(env)
    assert not result.has_placeholders
    assert result.found == {}


def test_angle_bracket_placeholder():
    assert _is_placeholder("<your-secret>")


def test_double_brace_placeholder():
    assert _is_placeholder("{{SECRET_KEY}}")


def test_dollar_brace_placeholder():
    assert _is_placeholder("${API_KEY}")


def test_changeme_placeholder():
    assert _is_placeholder("CHANGEME")
    assert _is_placeholder("change_me")


def test_square_bracket_placeholder():
    assert _is_placeholder("[insert value]")


def test_real_value_not_flagged():
    assert not _is_placeholder("supersecretpassword123")
    assert not _is_placeholder("https://example.com")


def test_find_placeholders_returns_only_flagged_keys():
    env = {"REAL": "abc123", "FAKE": "<replace-me>", "ALSO_FAKE": "CHANGEME"}
    result = find_placeholders(env)
    assert result.has_placeholders
    assert "FAKE" in result.found
    assert "ALSO_FAKE" in result.found
    assert "REAL" not in result.found


def test_summary_lists_keys():
    env = {"TOKEN": "{{TOKEN}}"}
    result = find_placeholders(env)
    assert "TOKEN" in result.summary()


# --- CLI tests ---

def write_env(tmp_path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_cli_no_placeholders_exits_zero(tmp_path):
    path = write_env(tmp_path, "HOST=localhost\nPORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(placeholder_cmd, [path])
    assert result.exit_code == 0
    assert "No placeholder" in result.output


def test_cli_placeholder_found_text(tmp_path):
    path = write_env(tmp_path, "API_KEY=<your-api-key>\nHOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(placeholder_cmd, [path])
    assert "API_KEY" in result.output


def test_cli_strict_exits_nonzero_on_placeholder(tmp_path):
    path = write_env(tmp_path, "SECRET=CHANGEME\n")
    runner = CliRunner()
    result = runner.invoke(placeholder_cmd, [path, "--strict"])
    assert result.exit_code == 1


def test_cli_json_output(tmp_path):
    path = write_env(tmp_path, "TOKEN={{TOKEN}}\nHOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(placeholder_cmd, [path, "--format", "json"])
    data = json.loads(result.output)
    assert data["has_placeholders"] is True
    assert "TOKEN" in data["placeholders"]
