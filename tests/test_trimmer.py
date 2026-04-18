"""Tests for envguard.trimmer."""
import pytest
from envguard.trimmer import trim_env, render_trimmed, was_changed


def test_clean_values_unchanged():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = trim_env(env)
    assert result.trimmed == env
    assert result.changed_keys == []


def test_trailing_space_detected():
    env = {"KEY": "value   "}
    result = trim_env(env)
    assert result.trimmed["KEY"] == "value"
    assert "KEY" in result.changed_keys


def test_leading_space_detected():
    env = {"KEY": "  value"}
    result = trim_env(env)
    assert result.trimmed["KEY"] == "value"
    assert "KEY" in result.changed_keys


def test_both_sides_trimmed():
    env = {"KEY": "  hello world  "}
    result = trim_env(env)
    assert result.trimmed["KEY"] == "hello world"


def test_was_changed_true():
    env = {"A": "val ", "B": "ok"}
    result = trim_env(env)
    assert was_changed(result) is True


def test_was_changed_false():
    env = {"A": "val", "B": "ok"}
    result = trim_env(env)
    assert was_changed(result) is False


def test_original_preserved():
    env = {"KEY": "value  "}
    result = trim_env(env)
    assert result.original["KEY"] == "value  "
    assert result.trimmed["KEY"] == "value"


def test_multiple_keys_only_dirty_recorded():
    env = {"A": "clean", "B": " dirty ", "C": "also_clean"}
    result = trim_env(env)
    assert result.changed_keys == ["B"]


def test_render_trimmed_basic():
    env = {"HOST": "localhost", "PORT": "8080"}
    out = render_trimmed(env)
    assert "HOST=localhost" in out
    assert "PORT=8080" in out


def test_render_trimmed_quotes_spaces():
    env = {"MSG": "hello world"}
    out = render_trimmed(env)
    assert 'MSG="hello world"' in out
