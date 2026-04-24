"""Tests for envguard.reorderer."""
from __future__ import annotations

import pytest

from envguard.reorderer import reorder_env, render_reordered


ENV = {"C": "3", "A": "1", "B": "2"}


def test_keys_placed_in_given_order():
    result = reorder_env(ENV, ["A", "B", "C"])
    assert list(result.reordered.keys()) == ["A", "B", "C"]


def test_partial_order_appends_remainder():
    result = reorder_env(ENV, ["C"])
    assert list(result.reordered.keys())[0] == "C"
    # A and B appended in their original relative order
    remainder = list(result.reordered.keys())[1:]
    assert set(remainder) == {"A", "B"}


def test_drop_unrecognised_removes_extra_keys():
    result = reorder_env(ENV, ["A"], append_unrecognised=False)
    assert list(result.reordered.keys()) == ["A"]
    assert result.unrecognised == ["C", "B"]


def test_missing_order_keys_recorded():
    result = reorder_env(ENV, ["A", "Z"])
    assert "Z" in result.missing
    assert "Z" not in result.reordered


def test_was_changed_true_when_order_differs():
    result = reorder_env(ENV, ["A", "B", "C"])
    assert result.was_changed() is True


def test_was_changed_false_when_order_same():
    env = {"A": "1", "B": "2", "C": "3"}
    result = reorder_env(env, ["A", "B", "C"])
    assert result.was_changed() is False


def test_values_preserved_after_reorder():
    result = reorder_env(ENV, ["A", "B", "C"])
    assert result.reordered == {"A": "1", "B": "2", "C": "3"}


def test_original_not_mutated():
    original_keys = list(ENV.keys())
    reorder_env(ENV, ["A", "B", "C"])
    assert list(ENV.keys()) == original_keys


def test_empty_env_returns_empty_reordered():
    result = reorder_env({}, ["A", "B"])
    assert result.reordered == {}
    assert result.missing == ["A", "B"]


def test_empty_order_appends_all_as_unrecognised():
    result = reorder_env(ENV, [])
    assert set(result.reordered.keys()) == set(ENV.keys())
    assert set(result.unrecognised) == set(ENV.keys())


def test_summary_mentions_key_count():
    result = reorder_env(ENV, ["A", "B", "C"])
    assert "3" in result.summary()


def test_render_ends_with_newline():
    result = reorder_env({"A": "1"}, ["A"])
    assert render_reordered(result).endswith("\n")


def test_render_preserves_key_value_pairs():
    result = reorder_env({"X": "hello", "Y": "world"}, ["Y", "X"])
    rendered = render_reordered(result)
    assert "X=hello" in rendered
    assert "Y=world" in rendered
    assert rendered.index("Y=") < rendered.index("X=")


def test_render_empty_env_is_empty_string():
    result = reorder_env({}, [])
    assert render_reordered(result) == ""
