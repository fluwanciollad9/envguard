"""Tests for envguard.differ_optional."""
import pytest
from envguard.differ_optional import diff_optional, OptionalDiffEntry, OptionalDiffResult


SOURCE = {
    "DEBUG": "true",
    "LOG_LEVEL": "info",
    "FEATURE_FLAG": "off",
    "TIMEOUT": "30",
}

TARGET = {
    "DEBUG": "false",
    "LOG_LEVEL": "info",
    "NEW_OPTIONAL": "yes",
    "TIMEOUT": "60",
}

OPTIONAL = {"DEBUG", "LOG_LEVEL", "FEATURE_FLAG", "NEW_OPTIONAL", "TIMEOUT"}


def test_no_differences_when_identical():
    env = {"A": "1", "B": "2"}
    result = diff_optional(env, env.copy(), {"A", "B"})
    assert not result.has_differences()


def test_modified_key_detected():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    keys = [c.key for c in result.changes]
    assert "DEBUG" in keys
    assert "TIMEOUT" in keys


def test_unchanged_key_not_in_changes():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    keys = [c.key for c in result.changes]
    assert "LOG_LEVEL" not in keys


def test_only_in_source_detected():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    assert "FEATURE_FLAG" in result.only_in_source


def test_only_in_target_detected():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    assert "NEW_OPTIONAL" in result.only_in_target


def test_non_optional_keys_ignored():
    src = {"REQUIRED": "x", "OPT": "1"}
    tgt = {"REQUIRED": "y", "OPT": "1"}
    result = diff_optional(src, tgt, {"OPT"})
    assert not result.has_differences()
    assert "REQUIRED" not in [c.key for c in result.changes]


def test_has_differences_true_on_change():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    assert result.has_differences()


def test_has_differences_false_for_empty():
    result = diff_optional({}, {}, set())
    assert not result.has_differences()


def test_summary_no_differences():
    env = {"A": "1"}
    result = diff_optional(env, env.copy(), {"A"})
    assert "no differences" in result.summary()


def test_summary_with_changes():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    s = result.summary()
    assert "changed" in s


def test_summary_with_removed():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    assert "removed" in result.summary()


def test_summary_with_added():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    assert "added" in result.summary()


def test_entry_str_modified():
    entry = OptionalDiffEntry("KEY", "old", "new")
    assert "~KEY" in str(entry)
    assert "old" in str(entry)
    assert "new" in str(entry)


def test_entry_str_added():
    entry = OptionalDiffEntry("KEY", None, "val")
    assert str(entry).startswith("+KEY")


def test_entry_str_removed():
    entry = OptionalDiffEntry("KEY", "val", None)
    assert str(entry).startswith("-KEY")


def test_optional_keys_stored_on_result():
    result = diff_optional(SOURCE, TARGET, OPTIONAL)
    assert result.optional_keys == OPTIONAL
