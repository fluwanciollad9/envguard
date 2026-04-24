"""Unit tests for envguard.pruner."""
from __future__ import annotations

import pytest

from envguard.pruner import prune_env, render_pruned


ENV = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "supersecret",
    "DATABASE_URL": "postgres://localhost/db",
    "EMPTY_VAR": "",
    "DEBUG": "true",
    "PLACEHOLDER": "<your_value>",
}


def test_prune_explicit_keys_removed():
    result = prune_env(ENV, keys=["DEBUG", "APP_NAME"])
    assert "DEBUG" not in result.pruned
    assert "APP_NAME" not in result.pruned


def test_prune_explicit_keys_other_keys_preserved():
    result = prune_env(ENV, keys=["DEBUG"])
    assert "APP_NAME" in result.pruned
    assert "SECRET_KEY" in result.pruned


def test_prune_empty_only_removes_empty_values():
    result = prune_env(ENV, empty_only=True)
    assert "EMPTY_VAR" not in result.pruned
    assert "APP_NAME" in result.pruned


def test_prune_empty_only_removed_list_populated():
    result = prune_env(ENV, empty_only=True)
    assert "EMPTY_VAR" in result.removed


def test_prune_pattern_matches_value():
    result = prune_env(ENV, pattern=r"<.*>")
    assert "PLACEHOLDER" not in result.pruned


def test_prune_pattern_non_matching_keys_preserved():
    result = prune_env(ENV, pattern=r"<.*>")
    assert "APP_NAME" in result.pruned
    assert "DEBUG" in result.pruned


def test_was_changed_true_when_keys_removed():
    result = prune_env(ENV, keys=["DEBUG"])
    assert result.was_changed() is True


def test_was_changed_false_when_nothing_removed():
    result = prune_env(ENV, keys=["NONEXISTENT"])
    assert result.was_changed() is False


def test_original_not_mutated():
    env_copy = dict(ENV)
    prune_env(ENV, keys=["DEBUG"])
    assert ENV == env_copy


def test_summary_lists_removed_keys():
    result = prune_env(ENV, keys=["DEBUG", "APP_NAME"])
    assert "DEBUG" in result.summary()
    assert "APP_NAME" in result.summary()


def test_summary_no_pruned():
    result = prune_env(ENV, keys=["NONEXISTENT"])
    assert result.summary() == "No keys pruned."


def test_no_criterion_raises():
    with pytest.raises(ValueError):
        prune_env(ENV)


def test_render_pruned_ends_with_newline():
    result = prune_env(ENV, keys=["DEBUG"])
    rendered = render_pruned(result.pruned)
    assert rendered.endswith("\n")


def test_render_pruned_contains_remaining_keys():
    result = prune_env(ENV, keys=["DEBUG"])
    rendered = render_pruned(result.pruned)
    assert "APP_NAME=myapp" in rendered
    assert "DEBUG" not in rendered
