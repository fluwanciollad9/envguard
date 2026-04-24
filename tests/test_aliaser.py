"""Tests for envguard.aliaser."""
from __future__ import annotations

import pytest

from envguard.aliaser import AliasResult, alias_env, summary, was_changed


BASE_ENV = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123", "DEBUG": "true"}


def test_alias_creates_new_key():
    result = alias_env(BASE_ENV, {"DATABASE_URL": "DB_URL"})
    assert "DB_URL" in result.env
    assert result.env["DB_URL"] == BASE_ENV["DATABASE_URL"]


def test_original_key_preserved_by_default():
    result = alias_env(BASE_ENV, {"DATABASE_URL": "DB_URL"})
    assert "DATABASE_URL" in result.env


def test_remove_original_drops_source_key():
    result = alias_env(BASE_ENV, {"DATABASE_URL": "DB_URL"}, keep_original=False)
    assert "DATABASE_URL" not in result.env
    assert "DB_URL" in result.env


def test_missing_source_key_is_skipped():
    result = alias_env(BASE_ENV, {"NONEXISTENT": "ALIAS_KEY"})
    assert "NONEXISTENT" in result.skipped
    assert "ALIAS_KEY" not in result.env


def test_existing_alias_key_is_conflict_without_overwrite():
    env = {**BASE_ENV, "DB_URL": "existing"}
    result = alias_env(env, {"DATABASE_URL": "DB_URL"}, overwrite=False)
    assert "DB_URL" in result.conflicts
    assert result.env["DB_URL"] == "existing"  # unchanged


def test_existing_alias_key_overwritten_when_flag_set():
    env = {**BASE_ENV, "DB_URL": "existing"}
    result = alias_env(env, {"DATABASE_URL": "DB_URL"}, overwrite=True)
    assert "DB_URL" in result.applied
    assert result.env["DB_URL"] == BASE_ENV["DATABASE_URL"]


def test_multiple_aliases_applied():
    alias_map = {"DATABASE_URL": "DB_URL", "SECRET_KEY": "APP_SECRET"}
    result = alias_env(BASE_ENV, alias_map)
    assert "DB_URL" in result.applied
    assert "APP_SECRET" in result.applied
    assert len(result.applied) == 2


def test_was_changed_true_when_alias_applied():
    result = alias_env(BASE_ENV, {"DEBUG": "APP_DEBUG"})
    assert was_changed(result) is True


def test_was_changed_false_when_nothing_applied():
    result = alias_env(BASE_ENV, {"MISSING_KEY": "SOME_ALIAS"})
    assert was_changed(result) is False


def test_summary_mentions_applied_count():
    result = alias_env(BASE_ENV, {"DEBUG": "APP_DEBUG"})
    assert "1 applied" in summary(result)


def test_summary_mentions_skipped_count():
    result = alias_env(BASE_ENV, {"MISSING": "ALIAS"})
    assert "skipped" in summary(result)


def test_summary_mentions_conflicts():
    env = {**BASE_ENV, "DB_URL": "existing"}
    result = alias_env(env, {"DATABASE_URL": "DB_URL"})
    assert "conflict" in summary(result)


def test_empty_alias_map_returns_original_env():
    result = alias_env(BASE_ENV, {})
    assert result.env == BASE_ENV
    assert result.applied == []
    assert result.skipped == []
    assert result.conflicts == []


def test_original_env_dict_not_mutated():
    original = dict(BASE_ENV)
    alias_env(BASE_ENV, {"DATABASE_URL": "DB_URL"}, keep_original=False)
    assert BASE_ENV == original
