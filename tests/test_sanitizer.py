"""Tests for envguard.sanitizer."""
import pytest
from envguard.sanitizer import sanitize_env, SanitizeResult


def test_clean_values_unchanged():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = sanitize_env(env)
    assert result.env == env
    assert not result.was_changed()


def test_trailing_whitespace_removed():
    env = {"KEY": "value   "}
    result = sanitize_env(env)
    assert result.env["KEY"] == "value"
    assert result.was_changed()


def test_leading_whitespace_removed():
    env = {"KEY": "   value"}
    result = sanitize_env(env)
    assert result.env["KEY"] == "value"


def test_both_sides_trimmed():
    env = {"KEY": "  hello world  "}
    result = sanitize_env(env)
    assert result.env["KEY"] == "hello world"


def test_control_char_removed():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env)
    assert "\x00" not in result.env["KEY"]
    assert result.was_changed()


def test_multiple_control_chars_removed():
    env = {"KEY": "\x01hello\x1fworld\x7f"}
    result = sanitize_env(env)
    assert result.env["KEY"] == "helloworld"


def test_issue_recorded_for_dirty_value():
    env = {"SECRET": "  bad  "}
    result = sanitize_env(env)
    assert len(result.issues) == 1
    assert result.issues[0].key == "SECRET"
    assert result.issues[0].original == "  bad  "
    assert result.issues[0].sanitized == "bad"


def test_no_issues_for_clean_env():
    env = {"A": "1", "B": "hello"}
    result = sanitize_env(env)
    assert result.issues == []


def test_strip_whitespace_disabled():
    env = {"KEY": "  value  "}
    result = sanitize_env(env, strip_whitespace=False)
    assert result.env["KEY"] == "  value  "
    assert not result.was_changed()


def test_control_char_removal_disabled():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env, remove_control_chars=False)
    assert result.env["KEY"] == "val\x00ue"
    assert not result.was_changed()


def test_summary_no_issues():
    result = sanitize_env({"A": "clean"})
    assert "No sanitization" in result.summary()


def test_summary_with_issues():
    result = sanitize_env({"A": "  dirty  ", "B": "ok"})
    assert "1 value(s) sanitized" in result.summary()
    assert "A" in result.summary()


def test_issue_str():
    result = sanitize_env({"KEY": "  v  "})
    assert str(result.issues[0]) == "KEY: leading/trailing whitespace removed"


def test_multiple_keys_multiple_issues():
    env = {"A": " a ", "B": "b\x01", "C": "clean"}
    result = sanitize_env(env)
    assert len(result.issues) == 2
    dirty_keys = {i.key for i in result.issues}
    assert dirty_keys == {"A", "B"}
