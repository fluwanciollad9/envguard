"""Tests for envguard.differ_regex."""
from __future__ import annotations

import pytest

from envguard.differ_regex import diff_env_by_regex, RegexDiffEntry


SOURCE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "SECRET_KEY": "abc123",
}

TARGET = {
    "DB_HOST": "prod-db",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "SECRET_KEY": "xyz789",
    "DB_NAME": "proddb",
}


def test_matched_keys_include_pattern_matches():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    assert "DB_HOST" in result.matched_keys
    assert "DB_PORT" in result.matched_keys
    assert "DB_NAME" in result.matched_keys


def test_non_matching_keys_excluded():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    assert "APP_NAME" not in result.matched_keys
    assert "SECRET_KEY" not in result.matched_keys


def test_modified_key_detected():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    keys_changed = [c.key for c in result.changes]
    assert "DB_HOST" in keys_changed


def test_unchanged_key_not_in_changes():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    keys_changed = [c.key for c in result.changes]
    assert "DB_PORT" not in keys_changed


def test_added_key_detected():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    added = [c for c in result.changes if c.is_added()]
    assert any(c.key == "DB_NAME" for c in added)


def test_removed_key_detected():
    result = diff_env_by_regex({"DB_OLD": "v"}, {}, r"^DB_")
    removed = [c for c in result.changes if c.is_removed()]
    assert any(c.key == "DB_OLD" for c in removed)


def test_has_differences_true_when_changes():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    assert result.has_differences() is True


def test_has_differences_false_when_identical():
    env = {"DB_HOST": "localhost"}
    result = diff_env_by_regex(env, env.copy(), r"^DB_")
    assert result.has_differences() is False


def test_pattern_stored_on_result():
    result = diff_env_by_regex(SOURCE, TARGET, r"SECRET")
    assert result.pattern == r"SECRET"


def test_summary_no_diff_message():
    env = {"DB_HOST": "same"}
    result = diff_env_by_regex(env, env.copy(), r"^DB_")
    assert "No differences" in result.summary()


def test_summary_reports_counts():
    result = diff_env_by_regex(SOURCE, TARGET, r"^DB_")
    s = result.summary()
    assert "modified" in s or "added" in s


def test_entry_str_added():
    entry = RegexDiffEntry(key="NEW", source_value=None, target_value="val")
    assert str(entry).startswith("+")


def test_entry_str_removed():
    entry = RegexDiffEntry(key="OLD", source_value="val", target_value=None)
    assert str(entry).startswith("-")


def test_entry_str_modified():
    entry = RegexDiffEntry(key="K", source_value="a", target_value="b")
    assert str(entry).startswith("~")
