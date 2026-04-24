"""Tests for envguard.stringer."""
import json
import pytest

from envguard.stringer import stringify_env, StringResult


SIMPLE_ENV = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


# ---------------------------------------------------------------------------
# dotenv format
# ---------------------------------------------------------------------------

def test_dotenv_contains_all_keys():
    result = stringify_env(SIMPLE_ENV, fmt="dotenv")
    for key in SIMPLE_ENV:
        assert key in result.output


def test_dotenv_ends_with_newline():
    result = stringify_env(SIMPLE_ENV, fmt="dotenv")
    assert result.output.endswith("\n")


def test_dotenv_value_with_space_is_quoted():
    env = {"GREETING": "hello world"}
    result = stringify_env(env, fmt="dotenv")
    assert 'GREETING="hello world"' in result.output


def test_dotenv_plain_value_not_quoted():
    env = {"KEY": "simplevalue"}
    result = stringify_env(env, fmt="dotenv")
    assert result.output.strip() == "KEY=simplevalue"


# ---------------------------------------------------------------------------
# exports format
# ---------------------------------------------------------------------------

def test_exports_has_export_prefix():
    result = stringify_env(SIMPLE_ENV, fmt="exports")
    for key in SIMPLE_ENV:
        assert f"export {key}=" in result.output


def test_exports_ends_with_newline():
    result = stringify_env(SIMPLE_ENV, fmt="exports")
    assert result.output.endswith("\n")


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

def test_json_is_valid_json():
    result = stringify_env(SIMPLE_ENV, fmt="json")
    parsed = json.loads(result.output)
    assert parsed == SIMPLE_ENV


def test_json_preserves_all_keys():
    result = stringify_env(SIMPLE_ENV, fmt="json")
    parsed = json.loads(result.output)
    assert set(parsed.keys()) == set(SIMPLE_ENV.keys())


# ---------------------------------------------------------------------------
# YAML format
# ---------------------------------------------------------------------------

def test_yaml_contains_all_keys():
    result = stringify_env(SIMPLE_ENV, fmt="yaml")
    for key in SIMPLE_ENV:
        assert key in result.output


def test_yaml_value_with_colon_is_quoted():
    env = {"URL": "http://example.com"}
    result = stringify_env(env, fmt="yaml")
    assert '"http://example.com"' in result.output


# ---------------------------------------------------------------------------
# INI format
# ---------------------------------------------------------------------------

def test_ini_has_section_header():
    result = stringify_env(SIMPLE_ENV, fmt="ini")
    assert "[env]" in result.output


def test_ini_uses_equals_with_spaces():
    env = {"FOO": "bar"}
    result = stringify_env(env, fmt="ini")
    assert "FOO = bar" in result.output


# ---------------------------------------------------------------------------
# StringResult metadata
# ---------------------------------------------------------------------------

def test_key_count_matches():
    result = stringify_env(SIMPLE_ENV, fmt="dotenv")
    assert result.key_count == len(SIMPLE_ENV)


def test_summary_mentions_format():
    result = stringify_env(SIMPLE_ENV, fmt="json")
    assert "json" in result.summary()


def test_empty_env_returns_empty_output():
    result = stringify_env({}, fmt="dotenv")
    assert result.output == ""
    assert result.key_count == 0


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        stringify_env(SIMPLE_ENV, fmt="xml")  # type: ignore[arg-type]
