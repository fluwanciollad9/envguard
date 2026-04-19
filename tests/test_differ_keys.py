"""Unit tests for envguard.differ_keys."""
import pytest
from envguard.differ_keys import diff_keys, KeyDiffResult


DEV = {"APP_NAME": "myapp", "DEBUG": "true", "DB_URL": "sqlite://"}
PROD = {"APP_NAME": "myapp", "DB_URL": "postgres://", "SECRET_KEY": "s3cr3t"}


def test_common_keys_detected():
    r = diff_keys(DEV, PROD)
    assert "APP_NAME" in r.common
    assert "DB_URL" in r.common


def test_only_in_source():
    r = diff_keys(DEV, PROD)
    assert "DEBUG" in r.only_in_source
    assert "SECRET_KEY" not in r.only_in_source


def test_only_in_target():
    r = diff_keys(DEV, PROD)
    assert "SECRET_KEY" in r.only_in_target
    assert "DEBUG" not in r.only_in_target


def test_has_differences_true():
    r = diff_keys(DEV, PROD)
    assert r.has_differences() is True


def test_has_differences_false_when_identical():
    env = {"A": "1", "B": "2"}
    r = diff_keys(env, env.copy())
    assert r.has_differences() is False


def test_summary_no_differences():
    env = {"X": "1"}
    r = diff_keys(env, env.copy())
    assert "No key differences" in r.summary()


def test_summary_mentions_source_name():
    r = diff_keys(DEV, PROD, source_name="dev", target_name="prod")
    assert "dev" in r.summary()


def test_empty_source():
    r = diff_keys({}, PROD)
    assert r.only_in_target == set(PROD.keys())
    assert not r.only_in_source


def test_empty_target():
    r = diff_keys(DEV, {})
    assert r.only_in_source == set(DEV.keys())
    assert not r.only_in_target


def test_names_stored():
    r = diff_keys({}, {}, source_name="a", target_name="b")
    assert r.source_name == "a"
    assert r.target_name == "b"
