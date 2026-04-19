import pytest
from envguard.grouper import group_env, GroupResult


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_ACCESS_KEY": "abc",
    "AWS_SECRET": "xyz",
    "APP_NAME": "envguard",
    "DEBUG": "true",
}


def test_auto_group_by_prefix():
    result = group_env(ENV)
    assert "DB" in result.groups
    assert "AWS" in result.groups
    assert "APP" in result.groups


def test_auto_group_keys_assigned_correctly():
    result = group_env(ENV)
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT"}
    assert set(result.groups["AWS"]) == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_no_underscore_goes_to_ungrouped():
    result = group_env(ENV)
    assert "DEBUG" in result.ungrouped


def test_explicit_prefixes_filter_correctly():
    result = group_env(ENV, prefixes=["DB_", "AWS_"])
    assert "DB" in result.groups or "DB_" in result.groups
    # normalised to upper of the supplied prefix
    keys_flat = [k for keys in result.groups.values() for k in keys]
    assert "DB_HOST" in keys_flat
    assert "AWS_ACCESS_KEY" in keys_flat
    assert "APP_NAME" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_explicit_prefixes_case_insensitive():
    result = group_env({"db_host": "h", "db_port": "5"}, prefixes=["DB_"])
    keys_flat = [k for keys in result.groups.values() for k in keys]
    assert "db_host" in keys_flat


def test_empty_env_returns_empty_result():
    result = group_env({})
    assert result.groups == {}
    assert result.ungrouped == []


def test_group_names_sorted():
    result = group_env(ENV)
    assert result.group_names() == sorted(result.group_names())


def test_summary_contains_prefix():
    result = group_env(ENV)
    s = result.summary()
    assert "DB" in s
    assert "AWS" in s


def test_summary_no_keys_message():
    result = GroupResult()
    assert result.summary() == "No keys found."


def test_all_keys_no_underscore_all_ungrouped():
    env = {"FOO": "1", "BAR": "2"}
    result = group_env(env)
    assert result.groups == {}
    assert set(result.ungrouped) == {"FOO", "BAR"}
