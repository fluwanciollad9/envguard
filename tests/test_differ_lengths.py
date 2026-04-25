"""Tests for envguard.differ_lengths."""
import pytest
from envguard.differ_lengths import LengthDiffEntry, LengthDiffResult, diff_lengths


SOURCE = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "short",
    "DATABASE_URL": "postgres://localhost/db",
    "ONLY_SOURCE": "x",
}

TARGET = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "a-much-longer-secret-value",
    "DATABASE_URL": "pg",
    "ONLY_TARGET": "y",
}


def test_no_changes_when_identical():
    env = {"A": "hello", "B": "world"}
    result = diff_lengths(env, env)
    assert not result.has_differences()
    assert result.changed == []
    assert result.only_in_source == []
    assert result.only_in_target == []


def test_longer_value_detected():
    result = diff_lengths(SOURCE, TARGET)
    keys = [e.key for e in result.changed]
    assert "SECRET_KEY" in keys
    entry = next(e for e in result.changed if e.key == "SECRET_KEY")
    assert entry.is_longer
    assert entry.delta > 0


def test_shorter_value_detected():
    result = diff_lengths(SOURCE, TARGET)
    entry = next(e for e in result.changed if e.key == "DATABASE_URL")
    assert entry.is_shorter
    assert entry.delta < 0


def test_equal_length_not_in_changed():
    result = diff_lengths(SOURCE, TARGET)
    keys = [e.key for e in result.changed]
    assert "APP_NAME" not in keys


def test_only_in_source_populated():
    result = diff_lengths(SOURCE, TARGET)
    assert "ONLY_SOURCE" in result.only_in_source


def test_only_in_target_populated():
    result = diff_lengths(SOURCE, TARGET)
    assert "ONLY_TARGET" in result.only_in_target


def test_has_differences_true():
    result = diff_lengths(SOURCE, TARGET)
    assert result.has_differences()


def test_has_differences_false_when_identical():
    env = {"KEY": "value"}
    result = diff_lengths(env, env)
    assert not result.has_differences()


def test_summary_no_differences():
    env = {"A": "same"}
    result = diff_lengths(env, env)
    assert result.summary() == "no differences"


def test_summary_describes_changes():
    result = diff_lengths(SOURCE, TARGET)
    s = result.summary()
    assert "length change" in s
    assert "only in source" in s
    assert "only in target" in s


def test_longer_in_target_helper():
    result = diff_lengths(SOURCE, TARGET)
    longer = result.longer_in_target()
    assert all(e.is_longer for e in longer)


def test_shorter_in_target_helper():
    result = diff_lengths(SOURCE, TARGET)
    shorter = result.shorter_in_target()
    assert all(e.is_shorter for e in shorter)


def test_entry_str_shows_delta():
    entry = LengthDiffEntry(key="FOO", source_len=3, target_len=10)
    s = str(entry)
    assert "FOO" in s
    assert "+7" in s


def test_entry_str_negative_delta():
    entry = LengthDiffEntry(key="BAR", source_len=10, target_len=3)
    s = str(entry)
    assert "-7" in s


def test_source_file_and_target_file_stored():
    result = diff_lengths({}, {}, source_file=".env.dev", target_file=".env.prod")
    assert result.source_file == ".env.dev"
    assert result.target_file == ".env.prod"
