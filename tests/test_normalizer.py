"""Tests for envguard.normalizer."""
import pytest
from envguard.normalizer import normalize_env, render_normalized


def test_uppercase_keys_by_default():
    result = normalize_env({"db_host": "localhost"})
    assert "DB_HOST" in result.normalized
    assert "db_host" not in result.normalized


def test_lowercase_key_change_recorded():
    result = normalize_env({"db_host": "localhost"})
    keys_changed = [c[0] for c in result.changes]
    assert "DB_HOST" in keys_changed


def test_strip_values_by_default():
    result = normalize_env({"KEY": "  value  "})
    assert result.normalized["KEY"] == "value"


def test_strip_value_change_recorded():
    result = normalize_env({"KEY": "  val  "})
    assert any(c[0] == "KEY" for c in result.changes)


def test_normalize_bool_true_variants():
    for variant in ("yes", "YES", "1", "on", "ON", "True"):
        result = normalize_env({"FLAG": variant})
        assert result.normalized["FLAG"] == "true", variant


def test_normalize_bool_false_variants():
    for variant in ("no", "NO", "0", "off", "OFF", "False"):
        result = normalize_env({"FLAG": variant})
        assert result.normalized["FLAG"] == "false", variant


def test_already_normalized_no_changes():
    result = normalize_env({"KEY": "value"})
    assert not result.was_changed()


def test_was_changed_true_when_modified():
    result = normalize_env({"key": "value"})
    assert result.was_changed()


def test_original_preserved():
    env = {"key": "  val  "}
    result = normalize_env(env)
    assert result.original == env


def test_uppercase_keys_disabled():
    result = normalize_env({"key": "val"}, uppercase_keys=False)
    assert "key" in result.normalized


def test_strip_values_disabled():
    result = normalize_env({"KEY": "  val  "}, strip_values=False)
    assert result.normalized["KEY"] == "  val  "


def test_normalize_bools_disabled():
    result = normalize_env({"FLAG": "yes"}, normalize_bools=False)
    assert result.normalized["FLAG"] == "yes"


def test_summary_no_changes():
    result = normalize_env({"KEY": "value"})
    assert "No normalization" in result.summary()


def test_summary_with_changes():
    result = normalize_env({"key": "value"})
    assert "change" in result.summary()


def test_render_normalized_ends_with_newline():
    result = normalize_env({"KEY": "val"})
    rendered = render_normalized(result)
    assert rendered.endswith("\n")


def test_render_normalized_empty_env():
    result = normalize_env({})
    assert render_normalized(result) == ""


def test_render_contains_all_keys():
    result = normalize_env({"A": "1", "B": "2"})
    rendered = render_normalized(result)
    assert "A=1" in rendered
    assert "B=2" in rendered
