"""Tests for envguard.deduplicator."""
import pytest
from envguard.deduplicator import deduplicate_env, render_deduplicated


def lines(*args: str):
    return list(args)


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_no_duplicates_returns_all_keys():
    raw = lines("FOO=bar", "BAZ=qux")
    result = deduplicate_env(raw)
    assert result.env == {"FOO": "bar", "BAZ": "qux"}


def test_no_duplicates_was_changed_false():
    raw = lines("FOO=bar", "BAZ=qux")
    result = deduplicate_env(raw)
    assert not result.was_changed()


def test_duplicate_key_kept_last_by_default():
    raw = lines("FOO=first", "BAR=x", "FOO=second")
    result = deduplicate_env(raw)
    assert result.env["FOO"] == "second"


def test_duplicate_key_kept_first_when_specified():
    raw = lines("FOO=first", "FOO=second")
    result = deduplicate_env(raw, keep="first")
    assert result.env["FOO"] == "first"


def test_was_changed_true_when_duplicates_present():
    raw = lines("KEY=a", "KEY=b")
    result = deduplicate_env(raw)
    assert result.was_changed()


def test_duplicates_dict_contains_all_values():
    raw = lines("KEY=a", "KEY=b", "KEY=c")
    result = deduplicate_env(raw)
    assert result.duplicates["KEY"] == ["a", "b", "c"]


def test_comments_and_blanks_ignored():
    raw = lines("# comment", "", "FOO=bar", "FOO=baz")
    result = deduplicate_env(raw)
    assert result.was_changed()
    assert result.env["FOO"] == "baz"


def test_missing_equals_ignored():
    raw = lines("BADLINE", "GOOD=ok")
    result = deduplicate_env(raw)
    assert "BADLINE" not in result.env
    assert result.env["GOOD"] == "ok"


def test_order_preserves_first_occurrence():
    raw = lines("B=1", "A=2", "B=3")
    result = deduplicate_env(raw)
    assert result.order == ["B", "A"]


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_summary_no_duplicates():
    raw = lines("A=1")
    result = deduplicate_env(raw)
    assert "No duplicate" in result.summary()


def test_summary_mentions_key_and_count():
    raw = lines("FOO=x", "FOO=y", "FOO=z")
    result = deduplicate_env(raw)
    summary = result.summary()
    assert "FOO" in summary
    assert "3" in summary


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def test_render_ends_with_newline():
    raw = lines("A=1", "B=2")
    result = deduplicate_env(raw)
    rendered = render_deduplicated(result)
    assert rendered.endswith("\n")


def test_render_empty_env_is_empty_string():
    result = deduplicate_env([])
    assert render_deduplicated(result) == ""


def test_render_contains_final_values():
    raw = lines("X=old", "Y=keep", "X=new")
    result = deduplicate_env(raw)
    rendered = render_deduplicated(result)
    assert "X=new" in rendered
    assert "X=old" not in rendered
    assert "Y=keep" in rendered
