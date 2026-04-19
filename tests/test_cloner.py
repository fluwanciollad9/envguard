"""Tests for envguard.cloner."""
from __future__ import annotations

import pytest

from envguard.cloner import CloneResult, clone_env, render_cloned


ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "DEBUG": "true",
}


def test_clone_all_keys_by_default():
    result = clone_env(ENV)
    assert set(result.cloned.keys()) == set(ENV.keys())


def test_include_filter_keeps_only_specified():
    result = clone_env(ENV, include=["APP_NAME", "DEBUG"])
    assert set(result.cloned.keys()) == {"APP_NAME", "DEBUG"}


def test_include_filter_records_dropped():
    result = clone_env(ENV, include=["APP_NAME"])
    assert "DB_PASSWORD" in result.dropped_keys
    assert "API_KEY" in result.dropped_keys


def test_exclude_filter_removes_specified():
    result = clone_env(ENV, exclude=["DEBUG"])
    assert "DEBUG" not in result.cloned
    assert "DEBUG" in result.dropped_keys


def test_redact_sensitive_masks_password():
    result = clone_env(ENV, redact_sensitive=True)
    assert result.cloned["DB_PASSWORD"] == "***"
    assert "DB_PASSWORD" in result.redacted_keys


def test_redact_sensitive_masks_api_key():
    result = clone_env(ENV, redact_sensitive=True)
    assert result.cloned["API_KEY"] == "***"


def test_non_sensitive_values_unchanged_when_redacting():
    result = clone_env(ENV, redact_sensitive=True)
    assert result.cloned["APP_NAME"] == "myapp"
    assert result.cloned["DEBUG"] == "true"


def test_custom_redact_mask():
    result = clone_env(ENV, redact_sensitive=True, redact_mask="REDACTED")
    assert result.cloned["DB_PASSWORD"] == "REDACTED"


def test_was_changed_true_when_redacted():
    result = clone_env(ENV, redact_sensitive=True)
    assert result.was_changed()


def test_was_changed_false_when_clean_clone():
    result = clone_env(ENV)
    assert not result.was_changed()


def test_summary_includes_key_count():
    result = clone_env(ENV)
    assert "4 key(s) cloned" in result.summary()


def test_summary_includes_redacted_count():
    result = clone_env(ENV, redact_sensitive=True)
    assert "redacted" in result.summary()


def test_original_is_unchanged():
    result = clone_env(ENV, redact_sensitive=True)
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_render_cloned_produces_dotenv_lines():
    result = clone_env({"A": "1", "B": "2"})
    text = render_cloned(result)
    assert "A=1" in text
    assert "B=2" in text


def test_render_cloned_ends_with_newline():
    result = clone_env({"X": "y"})
    assert render_cloned(result).endswith("\n")


def test_render_empty_env_is_empty_string():
    result = clone_env({})
    assert render_cloned(result) == ""
