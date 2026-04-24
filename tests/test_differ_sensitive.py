"""Tests for envguard.differ_sensitive."""
import pytest

from envguard.differ_sensitive import (
    SensitiveDiffResult,
    diff_sensitive,
    _is_sensitive,
)


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_password_key_is_sensitive():
    assert _is_sensitive("DB_PASSWORD") is True


def test_token_key_is_sensitive():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_api_key_is_sensitive():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_plain_key_is_not_sensitive():
    assert _is_sensitive("APP_ENV") is False


# ---------------------------------------------------------------------------
# diff_sensitive
# ---------------------------------------------------------------------------

def test_no_changes_when_identical():
    env = {"APP_ENV": "production", "DB_PASSWORD": "secret"}
    result = diff_sensitive(env, env)
    assert not result.has_changes


def test_added_key_detected():
    source = {"APP_ENV": "dev"}
    target = {"APP_ENV": "dev", "NEW_KEY": "value"}
    result = diff_sensitive(source, target)
    assert len(result.changes) == 1
    assert result.changes[0].key == "NEW_KEY"
    assert result.changes[0].is_added


def test_removed_key_detected():
    source = {"APP_ENV": "dev", "OLD_KEY": "gone"}
    target = {"APP_ENV": "dev"}
    result = diff_sensitive(source, target)
    assert len(result.changes) == 1
    assert result.changes[0].is_removed


def test_modified_key_detected():
    source = {"APP_ENV": "dev"}
    target = {"APP_ENV": "production"}
    result = diff_sensitive(source, target)
    assert len(result.changes) == 1
    assert result.changes[0].is_modified


def test_sensitive_change_flagged():
    source = {"DB_PASSWORD": "old"}
    target = {"DB_PASSWORD": "new"}
    result = diff_sensitive(source, target)
    assert len(result.sensitive_changes) == 1
    assert len(result.non_sensitive_changes) == 0


def test_non_sensitive_change_flagged():
    source = {"APP_ENV": "dev"}
    target = {"APP_ENV": "prod"}
    result = diff_sensitive(source, target)
    assert len(result.non_sensitive_changes) == 1
    assert len(result.sensitive_changes) == 0


def test_mixed_changes_split_correctly():
    source = {"APP_ENV": "dev", "DB_PASSWORD": "old"}
    target = {"APP_ENV": "prod", "DB_PASSWORD": "new"}
    result = diff_sensitive(source, target)
    assert len(result.changes) == 2
    assert len(result.sensitive_changes) == 1
    assert len(result.non_sensitive_changes) == 1


def test_summary_no_changes():
    result = diff_sensitive({"A": "1"}, {"A": "1"})
    assert "No differences" in result.summary()


def test_summary_with_changes():
    source = {"APP_ENV": "dev", "DB_TOKEN": "abc"}
    target = {"APP_ENV": "prod", "DB_TOKEN": "xyz"}
    result = diff_sensitive(source, target)
    summary = result.summary()
    assert "2 change" in summary
    assert "1 sensitive" in summary
