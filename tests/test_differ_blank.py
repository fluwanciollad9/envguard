"""Tests for envguard.differ_blank."""
from __future__ import annotations

import pytest

from envguard.differ_blank import BlankDiffResult, diff_blank


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

SOURCE = {
    "APP_NAME": "myapp",
    "DB_PASS": "",          # blank in source
    "API_KEY": "   ",       # whitespace-only => blank
    "DEBUG": "true",
}

TARGET = {
    "APP_NAME": "myapp",
    "DB_PASS": "secret",    # fixed in target
    "API_KEY": "   ",       # still blank
    "DEBUG": "",            # regressed in target
}


# ---------------------------------------------------------------------------
# diff_blank tests
# ---------------------------------------------------------------------------

def test_fixed_key_detected():
    result = diff_blank(SOURCE, TARGET)
    assert "DB_PASS" in result.fixed


def test_regressed_key_detected():
    result = diff_blank(SOURCE, TARGET)
    assert "DEBUG" in result.regressed


def test_still_blank_key_detected():
    result = diff_blank(SOURCE, TARGET)
    assert "API_KEY" in result.still_blank


def test_non_blank_key_not_in_any_list():
    result = diff_blank(SOURCE, TARGET)
    assert "APP_NAME" not in result.fixed
    assert "APP_NAME" not in result.regressed
    assert "APP_NAME" not in result.still_blank


def test_has_regressions_true():
    result = diff_blank(SOURCE, TARGET)
    assert result.has_regressions() is True


def test_has_regressions_false_when_no_regressions():
    src = {"A": "", "B": "val"}
    tgt = {"A": "filled", "B": "val"}
    result = diff_blank(src, tgt)
    assert result.has_regressions() is False


def test_has_differences_true():
    result = diff_blank(SOURCE, TARGET)
    assert result.has_differences() is True


def test_has_differences_false_when_identical_blanks():
    env = {"X": "", "Y": "ok"}
    result = diff_blank(env, env.copy())
    assert result.has_differences() is False


def test_summary_contains_fixed_and_regressed():
    result = diff_blank(SOURCE, TARGET)
    s = result.summary()
    assert "fixed" in s
    assert "regressed" in s


def test_summary_no_differences():
    env = {"A": "val"}
    result = diff_blank(env, env.copy())
    assert result.summary() == "No blank-value differences."


def test_empty_envs_produce_no_differences():
    result = diff_blank({}, {})
    assert not result.has_differences()
    assert result.source_blanks == set()
    assert result.target_blanks == set()


def test_all_blank_in_source_all_filled_in_target():
    src = {"A": "", "B": ""}
    tgt = {"A": "x", "B": "y"}
    result = diff_blank(src, tgt)
    assert sorted(result.fixed) == ["A", "B"]
    assert result.regressed == []
    assert result.still_blank == []
