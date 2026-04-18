"""Tests for envguard.comparator."""
import pytest
from envguard.comparator import compare_envs, ValueChange


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_no_changes_when_identical():
    result = compare_envs(BASE, BASE)
    assert not result.has_changes
    assert result.changes == []


def test_added_key_detected():
    result = compare_envs(BASE, TARGET)
    added_keys = [c.key for c in result.added]
    assert "SECRET" in added_keys


def test_removed_key_detected():
    result = compare_envs(BASE, TARGET)
    removed_keys = [c.key for c in result.removed]
    assert "DEBUG" in removed_keys


def test_modified_key_detected():
    result = compare_envs(BASE, TARGET)
    modified_keys = [c.key for c in result.modified]
    assert "HOST" in modified_keys


def test_unchanged_key_not_in_changes():
    result = compare_envs(BASE, TARGET)
    all_keys = [c.key for c in result.changes]
    assert "PORT" not in all_keys


def test_summary_string():
    result = compare_envs(BASE, TARGET)
    s = result.summary()
    assert "added" in s
    assert "removed" in s
    assert "modified" in s


def test_value_change_str_added():
    vc = ValueChange("FOO", None, "bar")
    assert str(vc).startswith("+")


def test_value_change_str_removed():
    vc = ValueChange("FOO", "bar", None)
    assert str(vc).startswith("-")


def test_value_change_str_modified():
    vc = ValueChange("FOO", "old", "new")
    assert str(vc).startswith("~")


def test_empty_base_all_added():
    result = compare_envs({}, {"A": "1", "B": "2"})
    assert len(result.added) == 2
    assert result.removed == []
    assert result.modified == []


def test_empty_target_all_removed():
    result = compare_envs({"A": "1", "B": "2"}, {})
    assert len(result.removed) == 2
    assert result.added == []
    assert result.modified == []
