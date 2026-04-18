"""Tests for envguard.redactor."""
import pytest
from envguard.redactor import redact_env, REDACTED


def test_non_sensitive_keys_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    assert result.redacted == env
    assert result.redacted_keys == []


def test_password_key_redacted():
    env = {"DB_PASSWORD": "supersecret", "HOST": "localhost"}
    result = redact_env(env)
    assert result.redacted["DB_PASSWORD"] == REDACTED
    assert result.redacted["HOST"] == "localhost"
    assert result.redacted_keys == ["DB_PASSWORD"]


def test_token_key_redacted():
    env = {"GITHUB_TOKEN": "ghp_abc123"}
    result = redact_env(env)
    assert result.redacted["GITHUB_TOKEN"] == REDACTED


def test_api_key_redacted():
    env = {"STRIPE_API_KEY": "sk_live_xyz"}
    result = redact_env(env)
    assert result.redacted["STRIPE_API_KEY"] == REDACTED


def test_case_insensitive_matching():
    env = {"db_secret": "hidden"}
    result = redact_env(env)
    assert result.redacted["db_secret"] == REDACTED


def test_extra_patterns():
    env = {"INTERNAL_CERT": "cert-data", "HOST": "localhost"}
    result = redact_env(env, extra_patterns=["CERT"])
    assert result.redacted["INTERNAL_CERT"] == REDACTED
    assert result.redacted["HOST"] == "localhost"


def test_show_partial_reveals_prefix():
    env = {"APP_SECRET": "abcdefghij"}
    result = redact_env(env, show_partial=True)
    assert result.redacted["APP_SECRET"].startswith("abcd")
    assert "*" in result.redacted["APP_SECRET"]


def test_show_partial_short_value_fully_redacted():
    env = {"APP_SECRET": "abc"}
    result = redact_env(env, show_partial=True)
    assert result.redacted["APP_SECRET"] == REDACTED


def test_redacted_keys_sorted():
    env = {"Z_TOKEN": "t1", "A_PASSWORD": "p1", "HOST": "h"}
    result = redact_env(env)
    assert result.redacted_keys == ["A_PASSWORD", "Z_TOKEN"]


def test_empty_env():
    result = redact_env({})
    assert result.redacted == {}
    assert result.redacted_keys == []
