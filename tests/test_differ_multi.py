"""Tests for envguard.differ_multi."""
import pytest
from envguard.differ_multi import diff_multiple


ENV_DEV = {"APP_NAME": "myapp", "DEBUG": "true", "DB_HOST": "localhost"}
ENV_STAGING = {"APP_NAME": "myapp", "DEBUG": "false", "DB_HOST": "staging.db"}
ENV_PROD = {"APP_NAME": "myapp", "DEBUG": "false", "DB_HOST": "prod.db", "SENTRY_DSN": "https://x"}


def test_all_keys_union():
    result = diff_multiple({"dev": ENV_DEV, "prod": ENV_PROD})
    assert "SENTRY_DSN" in result.all_keys
    assert "DEBUG" in result.all_keys


def test_common_keys_all_present():
    result = diff_multiple({"dev": ENV_DEV, "staging": ENV_STAGING, "prod": ENV_PROD})
    common = result.common_keys()
    assert "APP_NAME" in common
    assert "DEBUG" in common
    assert "DB_HOST" in common
    assert "SENTRY_DSN" not in common


def test_missing_in_dev_detects_sentry():
    result = diff_multiple({"dev": ENV_DEV, "prod": ENV_PROD})
    missing = result.missing_in("dev")
    assert "SENTRY_DSN" in missing


def test_missing_in_prod_is_empty_for_shared_keys():
    result = diff_multiple({"dev": ENV_DEV, "prod": ENV_PROD})
    missing = result.missing_in("prod")
    assert "APP_NAME" not in missing


def test_value_differences_detects_debug_mismatch():
    result = diff_multiple({"dev": ENV_DEV, "staging": ENV_STAGING})
    diffs = result.value_differences()
    assert "DEBUG" in diffs
    assert diffs["DEBUG"]["dev"] == "true"
    assert diffs["DEBUG"]["staging"] == "false"


def test_value_differences_missing_shown_as_placeholder():
    result = diff_multiple({"dev": ENV_DEV, "prod": ENV_PROD})
    diffs = result.value_differences()
    assert "SENTRY_DSN" in diffs
    assert diffs["SENTRY_DSN"]["dev"] == "<MISSING>"


def test_no_differences_when_identical():
    env = {"KEY": "val"}
    result = diff_multiple({"a": env, "b": dict(env)})
    assert not result.has_differences()


def test_has_differences_true_on_mismatch():
    result = diff_multiple({"dev": ENV_DEV, "prod": ENV_PROD})
    assert result.has_differences()


def test_empty_envs():
    result = diff_multiple({})
    assert result.all_keys == set()
    assert result.common_keys() == []
    assert not result.has_differences()
