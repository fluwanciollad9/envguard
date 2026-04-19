"""Tests for envguard.stripper."""
from __future__ import annotations

import pytest

from envguard.stripper import strip_env, render_stripped, StripResult


BASE_ENV = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc123", "DEBUG": "true"}


def test_strip_single_key():
    result = strip_env(BASE_ENV, ["SECRET"])
    assert "SECRET" not in result.stripped
    assert "HOST" in result.stripped


def test_removed_list_populated():
    result = strip_env(BASE_ENV, ["PORT", "DEBUG"])
    assert set(result.removed) == {"PORT", "DEBUG"}


def test_not_found_recorded():
    result = strip_env(BASE_ENV, ["MISSING_KEY"])
    assert "MISSING_KEY" in result.not_found
    assert result.removed == []


def test_was_changed_true_when_removed():
    result = strip_env(BASE_ENV, ["HOST"])
    assert result.was_changed() is True


def test_was_changed_false_when_nothing_removed():
    result = strip_env(BASE_ENV, ["NONEXISTENT"])
    assert result.was_changed() is False


def test_original_env_not_mutated():
    env = dict(BASE_ENV)
    strip_env(env, ["HOST"])
    assert "HOST" in env


def test_multiple_keys_stripped():
    result = strip_env(BASE_ENV, ["HOST", "PORT", "DEBUG"])
    assert len(result.stripped) == 1
    assert "SECRET" in result.stripped


def test_summary_removed():
    result = strip_env(BASE_ENV, ["SECRET"])
    assert "removed" in result.summary()
    assert "SECRET" in result.summary()


def test_summary_not_found():
    result = strip_env(BASE_ENV, ["GHOST"])
    assert "not found" in result.summary()


def test_summary_nothing_to_strip():
    result = strip_env({}, [])
    assert result.summary() == "nothing to strip"


def test_render_stripped_format():
    env = {"A": "1", "B": "2"}
    result = strip_env(env, ["A"])
    rendered = render_stripped(result.stripped)
    assert "B=2" in rendered
    assert "A=" not in rendered


def test_render_ends_with_newline():
    env = {"X": "y"}
    result = strip_env(env, [])
    assert render_stripped(result.stripped).endswith("\n")


def test_render_empty_is_empty_string():
    result = strip_env({"K": "v"}, ["K"])
    assert render_stripped(result.stripped) == ""
