"""Tests for envguard.differ_whitespace."""
import pytest
from envguard.differ_whitespace import (
    WhitespaceDiffEntry,
    WhitespaceDiffResult,
    diff_whitespace,
)


def test_no_differences_when_identical():
    env = {"KEY": "value", "OTHER": "hello"}
    result = diff_whitespace(env, env)
    assert not result.has_differences()


def test_trailing_whitespace_change_detected():
    source = {"KEY": "value "}
    target = {"KEY": "value"}
    result = diff_whitespace(source, target)
    assert len(result.changed) == 1
    assert result.changed[0].key == "KEY"


def test_leading_whitespace_change_detected():
    source = {"KEY": " value"}
    target = {"KEY": "value"}
    result = diff_whitespace(source, target)
    assert len(result.changed) == 1


def test_both_sides_whitespace_change_detected():
    source = {"KEY": "  value  "}
    target = {"KEY": "value"}
    result = diff_whitespace(source, target)
    assert len(result.changed) == 1
    entry = result.changed[0]
    assert entry.source_leading == 2
    assert entry.source_trailing == 2
    assert entry.target_leading == 0
    assert entry.target_trailing == 0


def test_only_in_source_populated():
    source = {"KEY": " val", "EXTRA": "x"}
    target = {"KEY": " val"}
    result = diff_whitespace(source, target)
    assert "EXTRA" in result.only_in_source


def test_only_in_target_populated():
    source = {"KEY": "val"}
    target = {"KEY": "val", "NEW": " new "}
    result = diff_whitespace(source, target)
    assert "NEW" in result.only_in_target


def test_has_differences_true_when_only_in_source():
    result = diff_whitespace({"A": "x"}, {})
    assert result.has_differences()


def test_has_differences_false_clean():
    result = diff_whitespace({"A": "x"}, {"A": "x"})
    assert not result.has_differences()


def test_summary_no_differences():
    result = diff_whitespace({"A": "x"}, {"A": "x"})
    assert result.summary() == "no whitespace differences"


def test_summary_with_changes():
    source = {"A": " val "}
    target = {"A": "val"}
    result = diff_whitespace(source, target)
    assert "1 key(s) with whitespace differences" in result.summary()


def test_entry_str_representation():
    entry = WhitespaceDiffEntry(key="FOO", source_value=" bar ", target_value="bar")
    text = str(entry)
    assert "FOO" in text
    assert "leading" in text
    assert "trailing" in text


def test_plain_value_change_not_flagged():
    """A change with no whitespace on either side should not appear in changed."""
    source = {"KEY": "old"}
    target = {"KEY": "new"}
    result = diff_whitespace(source, target)
    assert len(result.changed) == 0
