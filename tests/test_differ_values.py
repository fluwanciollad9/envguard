"""Tests for envguard.differ_values."""
import pytest
from envguard.differ_values import diff_values, ValueDiff


SOURCE = {"APP_ENV": "development", "DB_HOST": "localhost", "SECRET": "abc"}
TARGET = {"APP_ENV": "production", "DB_HOST": "localhost", "NEW_KEY": "hello"}


def test_no_changes_when_identical():
    result = diff_values({"A": "1"}, {"A": "1"})
    assert not result.has_differences()
    assert result.unchanged == ["A"]


def test_modified_key_detected():
    result = diff_values(SOURCE, TARGET)
    modified_keys = [d.key for d in result.modified()]
    assert "APP_ENV" in modified_keys


def test_added_key_detected():
    result = diff_values(SOURCE, TARGET)
    added_keys = [d.key for d in result.added()]
    assert "NEW_KEY" in added_keys


def test_removed_key_detected():
    result = diff_values(SOURCE, TARGET)
    removed_keys = [d.key for d in result.removed()]
    assert "SECRET" in removed_keys


def test_unchanged_key_not_in_diffs():
    result = diff_values(SOURCE, TARGET)
    assert "DB_HOST" in result.unchanged
    diff_keys = [d.key for d in result.diffs]
    assert "DB_HOST" not in diff_keys


def test_has_differences_true():
    result = diff_values(SOURCE, TARGET)
    assert result.has_differences()


def test_has_differences_false():
    env = {"A": "1", "B": "2"}
    result = diff_values(env, dict(env))
    assert not result.has_differences()


def test_summary_contains_labels():
    result = diff_values(SOURCE, TARGET, source_label="dev", target_label="prod")
    assert "dev" in result.summary()
    assert "prod" in result.summary()


def test_summary_counts():
    result = diff_values(SOURCE, TARGET)
    s = result.summary()
    assert "+1" in s  # added
    assert "-1" in s  # removed
    assert "~1" in s  # modified


def test_value_diff_str_added():
    d = ValueDiff(key="FOO", source_value=None, target_value="bar")
    assert str(d).startswith("+")


def test_value_diff_str_removed():
    d = ValueDiff(key="FOO", source_value="bar", target_value=None)
    assert str(d).startswith("-")


def test_value_diff_str_modified():
    d = ValueDiff(key="FOO", source_value="old", target_value="new")
    assert str(d).startswith("~")


def test_empty_envs_no_differences():
    result = diff_values({}, {})
    assert not result.has_differences()
    assert result.unchanged == []
