"""Roundtrip and edge-case tests for encryptor."""
import pytest
from envguard.encryptor import encrypt_env, decrypt_env


def roundtrip(env, passphrase):
    encrypted = encrypt_env(env, passphrase).encrypted
    return decrypt_env(encrypted, passphrase)


def test_roundtrip_multiple_sensitive_keys():
    env = {"DB_PASSWORD": "p@ss!", "SECRET_KEY": "s3cr3t", "APP": "web"}
    assert roundtrip(env, "mypass")["DB_PASSWORD"] == "p@ss!"
    assert roundtrip(env, "mypass")["SECRET_KEY"] == "s3cr3t"


def test_different_passphrases_produce_different_ciphertext():
    env = {"API_KEY": "value123"}
    enc1 = encrypt_env(env, "pass1").encrypted["API_KEY"]
    enc2 = encrypt_env(env, "pass2").encrypted["API_KEY"]
    assert enc1 != enc2


def test_wrong_passphrase_gives_wrong_plaintext():
    env = {"DB_PASSWORD": "correct"}
    encrypted = encrypt_env(env, "rightpass").encrypted
    decrypted = decrypt_env(encrypted, "wrongpass")
    assert decrypted["DB_PASSWORD"] != "correct"


def test_empty_value_encrypted_and_restored():
    env = {"DB_PASSWORD": ""}
    assert roundtrip(env, "pass")["DB_PASSWORD"] == ""


def test_special_chars_in_value():
    env = {"AUTH_TOKEN": "t0k!@#$%^&*()"}
    assert roundtrip(env, "p")["AUTH_TOKEN"] == "t0k!@#$%^&*()"


def test_unicode_value_roundtrip():
    env = {"API_KEY": "caf\u00e9"}
    assert roundtrip(env, "pass")["API_KEY"] == "caf\u00e9"
