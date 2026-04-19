"""Tests for envguard.validator."""

from __future__ import annotations

import pytest

from envguard.validator import ValidationResult, validate_env


ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "DEBUG": "true",
}


def test_valid_env_passes():
    result = validate_env(ENV, required=["DATABASE_URL", "SECRET_KEY"])
    assert result.is_valid
    assert result.missing_required == []
    assert result.empty_required == []


def test_missing_required_key():
    result = validate_env(ENV, required=["DATABASE_URL", "MISSING_KEY"])
    assert not result.is_valid
    assert "MISSING_KEY" in result.missing_required


def test_empty_required_key():
    env = {**ENV, "SECRET_KEY": ""}
    result = validate_env(env, required=["DATABASE_URL", "SECRET_KEY"])
    assert not result.is_valid
    assert "SECRET_KEY" in result.empty_required


def test_unknown_keys_allowed_by_default():
    result = validate_env(ENV, required=["DATABASE_URL"], optional=["SECRET_KEY"])
    assert result.unknown_keys == []


def test_unknown_keys_flagged_when_strict():
    result = validate_env(
        ENV,
        required=["DATABASE_URL"],
        optional=["SECRET_KEY"],
        allow_unknown=False,
    )
    assert "DEBUG" in result.unknown_keys


def test_summary_all_passed():
    result = ValidationResult()
    assert result.summary() == "All validations passed."


def test_summary_shows_issues():
    result = ValidationResult(
        missing_required=["FOO"],
        empty_required=["BAR"],
        unknown_keys=["BAZ"],
    )
    summary = result.summary()
    assert "FOO" in summary
    assert "BAR" in summary
    assert "BAZ" in summary


def test_whitespace_only_value_treated_as_empty():
    """A value containing only whitespace should be treated as empty."""
    env = {**ENV, "SECRET_KEY": "   "}
    result = validate_env(env, required=["DATABASE_URL", "SECRET_KEY"])
    assert not result.is_valid
    assert "SECRET_KEY" in result.empty_required
