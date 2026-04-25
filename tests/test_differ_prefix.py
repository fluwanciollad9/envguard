"""Tests for envguard.differ_prefix."""
from __future__ import annotations

from envguard.differ_prefix import diff_prefixes, _extract_prefix, _prefix_map


# ---------------------------------------------------------------------------
# _extract_prefix helpers
# ---------------------------------------------------------------------------

def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_underscore():
    assert _extract_prefix("PORT") == "PORT"


def test_extract_prefix_multiple_underscores():
    assert _extract_prefix("AWS_S3_BUCKET") == "AWS"


# ---------------------------------------------------------------------------
# _prefix_map helpers
# ---------------------------------------------------------------------------

def test_prefix_map_groups_correctly():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "PORT": "8080"}
    pm = _prefix_map(env)
    assert set(pm["DB"]) == {"DB_HOST", "DB_PORT"}
    assert pm["PORT"] == ["PORT"]


# ---------------------------------------------------------------------------
# diff_prefixes
# ---------------------------------------------------------------------------

def test_identical_envs_no_differences():
    env = {"DB_HOST": "a", "DB_PORT": "b", "PORT": "8080"}
    result = diff_prefixes(env, env.copy())
    assert not result.has_differences()


def test_only_in_source_detected():
    source = {"DB_HOST": "a", "REDIS_URL": "r"}
    target = {"DB_HOST": "b"}
    result = diff_prefixes(source, target)
    assert "REDIS" in result.only_in_source
    assert "REDIS" not in result.only_in_target


def test_only_in_target_detected():
    source = {"APP_NAME": "x"}
    target = {"APP_NAME": "x", "SMTP_HOST": "mail"}
    result = diff_prefixes(source, target)
    assert "SMTP" in result.only_in_target
    assert "SMTP" not in result.only_in_source


def test_common_prefixes_populated():
    source = {"DB_HOST": "a", "APP_ENV": "prod"}
    target = {"DB_PORT": "5432", "APP_ENV": "staging"}
    result = diff_prefixes(source, target)
    assert "DB" in result.common
    assert "APP" in result.common


def test_has_differences_false_when_same_prefixes():
    source = {"DB_HOST": "a"}
    target = {"DB_PORT": "5432"}
    result = diff_prefixes(source, target)
    # Both have prefix DB — no difference in prefix sets
    assert not result.has_differences()


def test_summary_identical():
    env = {"KEY": "val"}
    result = diff_prefixes(env, env.copy())
    assert result.summary() == "prefixes identical"


def test_summary_mentions_source_only_prefix():
    source = {"CACHE_TTL": "60"}
    target = {"APP_NAME": "x"}
    result = diff_prefixes(source, target)
    assert "CACHE" in result.summary()
    assert "APP" in result.summary()


def test_empty_envs_no_differences():
    result = diff_prefixes({}, {})
    assert not result.has_differences()
    assert result.summary() == "prefixes identical"


def test_source_map_populated():
    source = {"AWS_KEY": "k", "AWS_SECRET": "s"}
    result = diff_prefixes(source, {})
    assert set(result.source_map["AWS"]) == {"AWS_KEY", "AWS_SECRET"}
