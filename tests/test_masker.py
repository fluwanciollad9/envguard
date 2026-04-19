"""Tests for envguard.masker."""
import pytest
from envguard.masker import mask_env, DEFAULT_MASK, _is_sensitive


def test_non_sensitive_keys_unchanged():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = mask_env(env)
    assert result.masked == env
    assert result.masked_keys == []


def test_password_key_masked():
    env = {"DB_PASSWORD": "s3cr3t", "HOST": "localhost"}
    result = mask_env(env)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["HOST"] == "localhost"
    assert "DB_PASSWORD" in result.masked_keys


def test_token_key_masked():
    env = {"GITHUB_TOKEN": "abc123"}
    result = mask_env(env)
    assert result.masked["GITHUB_TOKEN"] == DEFAULT_MASK


def test_api_key_masked():
    env = {"STRIPE_API_KEY": "sk_live_xyz"}
    result = mask_env(env)
    assert result.masked["STRIPE_API_KEY"] == DEFAULT_MASK


def test_custom_mask_string():
    env = {"SECRET_KEY": "topsecret"}
    result = mask_env(env, mask="[REDACTED]")
    assert result.masked["SECRET_KEY"] == "[REDACTED]"


def test_explicit_extra_keys_masked():
    env = {"MY_CUSTOM": "value", "OTHER": "ok"}
    result = mask_env(env, keys=["MY_CUSTOM"])
    assert result.masked["MY_CUSTOM"] == DEFAULT_MASK
    assert result.masked["OTHER"] == "ok"
    assert "MY_CUSTOM" in result.masked_keys


def test_was_masked_true_when_sensitive():
    env = {"AUTH_TOKEN": "xyz"}
    result = mask_env(env)
    assert result.was_masked() is True


def test_was_masked_false_when_clean():
    env = {"PORT": "3000"}
    result = mask_env(env)
    assert result.was_masked() is False


def test_summary_no_sensitive():
    env = {"PORT": "3000"}
    result = mask_env(env)
    assert result.summary() == "No sensitive keys found."


def test_summary_with_sensitive():
    env = {"DB_PASSWORD": "x", "API_KEY": "y"}
    result = mask_env(env)
    assert "2 key(s) masked" in result.summary()


def test_original_env_not_mutated():
    env = {"SECRET": "real_value"}
    result = mask_env(env)
    assert result.original["SECRET"] == "real_value"
    assert result.masked["SECRET"] == DEFAULT_MASK


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("db_Password") is True
    assert _is_sensitive("APIKEY") is True
    assert _is_sensitive("PORT") is False


def test_empty_env_returns_empty_result():
    """mask_env should handle an empty dict without errors."""
    result = mask_env({})
    assert result.masked == {}
    assert result.masked_keys == []
    assert result.was_masked() is False
    assert result.summary() == "No sensitive keys found."
