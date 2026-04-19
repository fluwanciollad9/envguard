"""Tests for envguard.encryptor."""
import pytest
from envguard.encryptor import encrypt_env, decrypt_env, EncryptResult

PASS = "supersecret"

BASE_ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "hunter2",
    "API_KEY": "abc123",
    "PORT": "8080",
    "AUTH_TOKEN": "tok_xyz",
}


def test_sensitive_keys_are_encrypted():
    result = encrypt_env(BASE_ENV, PASS)
    assert result.encrypted["DB_PASSWORD"].startswith("enc:")
    assert result.encrypted["API_KEY"].startswith("enc:")
    assert result.encrypted["AUTH_TOKEN"].startswith("enc:")


def test_non_sensitive_keys_unchanged():
    result = encrypt_env(BASE_ENV, PASS)
    assert result.encrypted["APP_NAME"] == "myapp"
    assert result.encrypted["PORT"] == "8080"


def test_encrypt_count():
    result = encrypt_env(BASE_ENV, PASS)
    assert result.encrypt_count == 3


def test_skipped_contains_non_sensitive():
    result = encrypt_env(BASE_ENV, PASS)
    assert "APP_NAME" in result.skipped
    assert "PORT" in result.skipped


def test_already_encrypted_not_double_encrypted():
    first = encrypt_env(BASE_ENV, PASS)
    second = encrypt_env(first.encrypted, PASS)
    assert second.encrypt_count == 0
    assert second.encrypted["DB_PASSWORD"] == first.encrypted["DB_PASSWORD"]


def test_decrypt_restores_original():
    encrypted = encrypt_env(BASE_ENV, PASS).encrypted
    decrypted = decrypt_env(encrypted, PASS)
    assert decrypted["DB_PASSWORD"] == "hunter2"
    assert decrypted["API_KEY"] == "abc123"
    assert decrypted["AUTH_TOKEN"] == "tok_xyz"


def test_decrypt_leaves_non_sensitive_unchanged():
    encrypted = encrypt_env(BASE_ENV, PASS).encrypted
    decrypted = decrypt_env(encrypted, PASS)
    assert decrypted["APP_NAME"] == "myapp"
    assert decrypted["PORT"] == "8080"


def test_summary_message():
    result = encrypt_env(BASE_ENV, PASS)
    assert "3" in result.summary()


def test_empty_env():
    result = encrypt_env({}, PASS)
    assert result.encrypt_count == 0
    assert result.encrypted == {}
