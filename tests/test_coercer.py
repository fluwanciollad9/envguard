"""Tests for envguard.coercer."""
import pytest
from envguard.coercer import coerce_env, CoerceResult


def test_str_type_unchanged():
    result = coerce_env({"NAME": "alice"}, {"NAME": "str"})
    assert result.coerced["NAME"] == "alice"
    assert not result.has_errors


def test_int_coercion():
    result = coerce_env({"PORT": "8080"}, {"PORT": "int"})
    assert result.coerced["PORT"] == 8080
    assert isinstance(result.coerced["PORT"], int)


def test_float_coercion():
    result = coerce_env({"RATIO": "0.75"}, {"RATIO": "float"})
    assert result.coerced["RATIO"] == pytest.approx(0.75)


def test_bool_true_variants():
    for val in ("true", "1", "yes", "on", "TRUE", "YES"):
        result = coerce_env({"FLAG": val}, {"FLAG": "bool"})
        assert result.coerced["FLAG"] is True, val


def test_bool_false_variants():
    for val in ("false", "0", "no", "off", "FALSE"):
        result = coerce_env({"FLAG": val}, {"FLAG": "bool"})
        assert result.coerced["FLAG"] is False, val


def test_invalid_int_produces_error():
    result = coerce_env({"PORT": "abc"}, {"PORT": "int"})
    assert result.has_errors
    assert result.errors[0].key == "PORT"
    assert "PORT" not in result.coerced


def test_invalid_bool_produces_error():
    result = coerce_env({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert result.has_errors
    assert "not a recognised boolean" in result.errors[0].reason


def test_key_not_in_type_map_is_skipped():
    result = coerce_env({"UNKNOWN": "value"}, {})
    assert "UNKNOWN" in result.skipped
    assert result.coerced["UNKNOWN"] == "value"


def test_unsupported_type_produces_error():
    result = coerce_env({"X": "1"}, {"X": "list"})
    assert result.has_errors
    assert "unsupported type" in result.errors[0].reason


def test_summary_string():
    result = coerce_env(
        {"PORT": "8080", "DEBUG": "yes", "OTHER": "foo"},
        {"PORT": "int", "DEBUG": "bool"},
    )
    s = result.summary()
    assert "coerced" in s
    assert "skipped" in s


def test_coerce_error_str():
    result = coerce_env({"PORT": "xyz"}, {"PORT": "int"})
    assert "PORT" in str(result.errors[0])
    assert "int" in str(result.errors[0])
