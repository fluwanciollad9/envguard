"""Tests for envguard.freezer."""
import pytest
from envguard.freezer import freeze_env, check_freeze, FreezeViolation


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"}


def test_freeze_env_returns_copy():
    frozen = freeze_env(BASE)
    assert frozen == BASE
    assert frozen is not BASE


def test_no_violations_when_identical():
    frozen = freeze_env(BASE)
    result = check_freeze(frozen, dict(BASE))
    assert not result.has_violations()
    assert result.summary() == "no violations"


def test_value_change_detected():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["DB_HOST"] = "remotehost"
    result = check_freeze(frozen, current)
    assert result.has_violations()
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.key == "DB_HOST"
    assert v.original == "localhost"
    assert v.current == "remotehost"


def test_new_key_detected():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["NEW_VAR"] = "hello"
    result = check_freeze(frozen, current)
    assert result.has_violations()
    assert "NEW_VAR" in result.new_keys
    assert result.violations == []


def test_removed_key_detected():
    frozen = freeze_env(BASE)
    current = {k: v for k, v in BASE.items() if k != "DB_PORT"}
    result = check_freeze(frozen, current)
    assert result.has_violations()
    assert "DB_PORT" in result.removed_keys


def test_multiple_violations_counted():
    frozen = freeze_env(BASE)
    current = {"DB_HOST": "other", "SECRET_KEY": "xyz"}  # DB_PORT removed
    result = check_freeze(frozen, current)
    assert len(result.violations) == 2
    assert len(result.removed_keys) == 1
    assert "2 value change(s)" in result.summary()
    assert "1 removed key(s)" in result.summary()


def test_freeze_violation_str():
    v = FreezeViolation(key="FOO", original="bar", current="baz")
    assert "FOO" in str(v)
    assert "bar" in str(v)
    assert "baz" in str(v)


def test_empty_env_no_violations():
    result = check_freeze({}, {})
    assert not result.has_violations()


def test_new_keys_sorted():
    frozen = freeze_env({})
    current = {"Z_KEY": "1", "A_KEY": "2", "M_KEY": "3"}
    result = check_freeze(frozen, current)
    assert result.new_keys == ["A_KEY", "M_KEY", "Z_KEY"]
