"""Tests for envguard.interpolator."""
import os

import pytest

from envguard.interpolator import interpolate, InterpolationResult


def test_no_references_unchanged():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = interpolate(env)
    assert result.resolved == env
    assert not result.has_unresolved


def test_brace_reference_resolved():
    env = {"BASE": "/app", "LOG_DIR": "${BASE}/logs"}
    result = interpolate(env)
    assert result.resolved["LOG_DIR"] == "/app/logs"
    assert not result.has_unresolved


def test_bare_reference_resolved():
    env = {"HOME_DIR": "/home/user", "CONF": "$HOME_DIR/.config"}
    result = interpolate(env)
    assert result.resolved["CONF"] == "/home/user/.config"


def test_multiple_references_in_one_value():
    env = {"FIRST": "hello", "SECOND": "world", "MSG": "${FIRST} ${SECOND}"}
    result = interpolate(env)
    assert result.resolved["MSG"] == "hello world"


def test_unresolved_key_recorded():
    env = {"PATH_VAL": "${MISSING}/bin"}
    result = interpolate(env, allow_os=False)
    assert result.has_unresolved
    assert "PATH_VAL" in result.unresolved_keys
    # original placeholder preserved
    assert "${MISSING}" in result.resolved["PATH_VAL"]


def test_os_environ_fallback(monkeypatch):
    monkeypatch.setenv("SYS_VAR", "from-os")
    env = {"DERIVED": "${SYS_VAR}/extra"}
    result = interpolate(env, allow_os=True)
    assert result.resolved["DERIVED"] == "from-os/extra"
    assert not result.has_unresolved


def test_os_fallback_disabled(monkeypatch):
    monkeypatch.setenv("SYS_VAR", "from-os")
    env = {"DERIVED": "${SYS_VAR}/extra"}
    result = interpolate(env, allow_os=False)
    assert result.has_unresolved


def test_value_without_dollar_sign_untouched():
    env = {"KEY": "plain_value_123"}
    result = interpolate(env)
    assert result.resolved["KEY"] == "plain_value_123"


def test_empty_env():
    result = interpolate({})
    assert result.resolved == {}
    assert not result.has_unresolved
