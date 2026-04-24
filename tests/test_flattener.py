"""Tests for envguard.flattener."""
import pytest
from envguard.flattener import FlattenResult, flatten_env, expand_env


# ---------------------------------------------------------------------------
# flatten_env
# ---------------------------------------------------------------------------

def test_keys_without_separator_are_ungrouped():
    env = {"APP_NAME": "myapp", "DEBUG": "true"}
    result = flatten_env(env)
    assert set(result.ungrouped) == {"APP_NAME", "DEBUG"}
    assert result.groups == {}


def test_keys_with_separator_are_grouped():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432", "APP_NAME": "x"}
    result = flatten_env(env)
    assert "DB" in result.groups
    assert set(result.groups["DB"]) == {"DB__HOST", "DB__PORT"}
    assert result.ungrouped == ["APP_NAME"]


def test_multiple_prefixes_grouped_separately():
    env = {
        "DB__HOST": "localhost",
        "CACHE__URL": "redis://",
        "CACHE__TTL": "300",
        "DEBUG": "false",
    }
    result = flatten_env(env)
    assert set(result.groups.keys()) == {"DB", "CACHE"}
    assert result.groups["CACHE"] == ["CACHE__URL", "CACHE__TTL"] or \
           set(result.groups["CACHE"]) == {"CACHE__URL", "CACHE__TTL"}


def test_explicit_prefixes_filter_correctly():
    env = {"DB__HOST": "h", "CACHE__URL": "u", "DEBUG": "1"}
    result = flatten_env(env, prefixes=["DB"])
    assert "DB" in result.groups
    assert "CACHE" not in result.groups
    # CACHE__URL has separator but prefix not in filter -> ungrouped
    assert "CACHE__URL" in result.ungrouped


def test_explicit_prefixes_case_insensitive():
    env = {"DB__HOST": "h"}
    result = flatten_env(env, prefixes=["db"])
    assert "DB" in result.groups


def test_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432"}
    result = flatten_env(env, separator=".")
    assert "DB" in result.groups
    assert result.ungrouped == []


def test_was_grouped_true_when_groups_exist():
    env = {"DB__HOST": "h"}
    assert flatten_env(env).was_grouped() is True


def test_was_grouped_false_when_no_groups():
    env = {"DEBUG": "true"}
    assert flatten_env(env).was_grouped() is False


def test_group_count():
    env = {"A__X": "1", "B__Y": "2", "B__Z": "3"}
    assert flatten_env(env).group_count() == 2


def test_summary_contains_key_count():
    env = {"DB__HOST": "h", "DEBUG": "1"}
    s = flatten_env(env).summary()
    assert "2 keys" in s


# ---------------------------------------------------------------------------
# expand_env
# ---------------------------------------------------------------------------

def test_expand_single_level():
    env = {"DB__HOST": "localhost"}
    nested = expand_env(env)
    assert nested == {"DB": {"HOST": "localhost"}}


def test_expand_multiple_keys_same_prefix():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432"}
    nested = expand_env(env)
    assert nested["DB"] == {"HOST": "localhost", "PORT": "5432"}


def test_expand_keys_without_separator_stay_top_level():
    env = {"DEBUG": "true", "DB__HOST": "h"}
    nested = expand_env(env)
    assert nested["DEBUG"] == "true"
    assert isinstance(nested["DB"], dict)


def test_expand_deep_nesting():
    env = {"A__B__C": "deep"}
    nested = expand_env(env)
    assert nested == {"A": {"B": {"C": "deep"}}}


def test_expand_empty_env():
    assert expand_env({}) == {}
