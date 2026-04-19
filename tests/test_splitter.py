"""Tests for envguard.splitter."""
import pytest
from envguard.splitter import split_env, render_split


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "REDIS_URL": "redis://localhost",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_groups_created_for_matching_prefixes():
    result = split_env(SAMPLE, ["DB_", "REDIS_"])
    assert "DB" in result.group_names()
    assert "REDIS" in result.group_names()


def test_unmatched_keys_go_to_ungrouped():
    result = split_env(SAMPLE, ["DB_", "REDIS_"])
    assert "APP_DEBUG" in result.ungrouped
    assert "SECRET_KEY" in result.ungrouped


def test_correct_keys_in_group():
    result = split_env(SAMPLE, ["DB_"])
    assert "DB_HOST" in result.groups["DB"]
    assert "DB_PORT" in result.groups["DB"]


def test_strip_prefix_removes_prefix_from_keys():
    result = split_env(SAMPLE, ["DB_"], strip_prefix=True)
    assert "HOST" in result.groups["DB"]
    assert "PORT" in result.groups["DB"]
    assert "DB_HOST" not in result.groups["DB"]


def test_strip_prefix_false_keeps_full_key():
    result = split_env(SAMPLE, ["DB_"], strip_prefix=False)
    assert "DB_HOST" in result.groups["DB"]


def test_case_insensitive_matching_by_default():
    env = {"db_host": "localhost", "DB_PORT": "5432"}
    result = split_env(env, ["DB_"])
    assert len(result.groups["DB"]) == 2


def test_case_sensitive_matching_excludes_lowercase():
    env = {"db_host": "localhost", "DB_PORT": "5432"}
    result = split_env(env, ["DB_"], case_sensitive=True)
    assert "DB_PORT" in result.groups["DB"]
    assert "db_host" in result.ungrouped


def test_total_keys_counts_all():
    result = split_env(SAMPLE, ["DB_", "REDIS_"])
    assert result.total_keys() == len(SAMPLE)


def test_empty_env_returns_empty_result():
    result = split_env({}, ["DB_"])
    assert result.groups == {}
    assert result.ungrouped == {}
    assert result.total_keys() == 0


def test_summary_lists_groups():
    result = split_env(SAMPLE, ["DB_", "REDIS_"])
    s = result.summary()
    assert "DB" in s
    assert "REDIS" in s
    assert "ungrouped" in s


def test_render_split_produces_dotenv_format():
    env = {"FOO": "bar", "BAZ": "qux"}
    output = render_split(env)
    assert "FOO=bar" in output
    assert "BAZ=qux" in output
    assert output.endswith("\n")


def test_render_split_empty_env_is_empty_string():
    assert render_split({}) == ""
