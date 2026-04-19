"""Tests for envguard.defaults."""
from __future__ import annotations
import pytest
from envguard.defaults import apply_defaults, DefaultsResult


def test_missing_key_gets_default():
    env = {"HOST": "localhost"}
    result = apply_defaults(env, {"PORT": "5432"})
    assert result.env["PORT"] == "5432"
    assert "PORT" in result.applied


def test_existing_key_not_overwritten_by_default():
    env = {"HOST": "prod.example.com"}
    result = apply_defaults(env, {"HOST": "localhost"})
    assert result.env["HOST"] == "prod.example.com"
    assert "HOST" in result.skipped
    assert "HOST" not in result.applied


def test_overwrite_flag_replaces_existing():
    env = {"HOST": "prod.example.com"}
    result = apply_defaults(env, {"HOST": "localhost"}, overwrite=True)
    assert result.env["HOST"] == "localhost"
    assert "HOST" in result.applied


def test_was_changed_true_when_applied():
    result = apply_defaults({}, {"KEY": "val"})
    assert result.was_changed() is True


def test_was_changed_false_when_all_skipped():
    result = apply_defaults({"KEY": "existing"}, {"KEY": "default"})
    assert result.was_changed() is False


def test_multiple_defaults_mixed():
    env = {"A": "1"}
    result = apply_defaults(env, {"A": "99", "B": "2", "C": "3"})
    assert result.env["A"] == "1"
    assert result.env["B"] == "2"
    assert result.env["C"] == "3"
    assert set(result.applied) == {"B", "C"}
    assert result.skipped == ["A"]


def test_empty_defaults_no_change():
    env = {"X": "10"}
    result = apply_defaults(env, {})
    assert result.env == {"X": "10"}
    assert result.applied == []
    assert result.skipped == []


def test_summary_no_defaults():
    result = apply_defaults({}, {})
    assert "No defaults" in result.summary()


def test_summary_with_applied_and_skipped():
    result": "1"}, {"A": "x", "B": "2"})
    s = result.summary()
    assert "B" in s
    assert "A" in s
