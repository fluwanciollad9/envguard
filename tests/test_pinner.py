"""Tests for envguard.pinner."""
import json
import pytest
from pathlib import Path
from envguard.pinner import pin_env, check_drift, save_lock, load_lock, PinResult


ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


def test_pin_env_returns_copy():
    lock = pin_env(ENV)
    assert lock == ENV
    assert lock is not ENV


def test_no_drift_when_identical():
    lock = pin_env(ENV)
    result = check_drift(ENV, lock)
    assert not result.has_drift()
    assert result.summary() == "no drift detected"


def test_drifted_key_detected():
    lock = pin_env(ENV)
    modified = {**ENV, "DB_PORT": "9999"}
    result = check_drift(modified, lock)
    assert "DB_PORT" in result.drifted
    assert result.has_drift()


def test_new_key_detected():
    lock = pin_env(ENV)
    extended = {**ENV, "NEW_KEY": "hello"}
    result = check_drift(extended, lock)
    assert "NEW_KEY" in result.new_keys


def test_removed_key_detected():
    lock = pin_env(ENV)
    shrunk = {k: v for k, v in ENV.items() if k != "SECRET"}
    result = check_drift(shrunk, lock)
    assert "SECRET" in result.removed_keys


def test_summary_shows_counts():
    lock = {"A": "1", "B": "2"}
    env = {"A": "changed", "C": "new"}
    result = check_drift(env, lock)
    s = result.summary()
    assert "drifted" in s
    assert "new" in s
    assert "removed" in s


def test_save_and_load_roundtrip(tmp_path):
    lock_path = tmp_path / "env.lock"
    save_lock(ENV, lock_path)
    loaded = load_lock(lock_path)
    assert loaded == ENV


def test_save_writes_valid_json(tmp_path):
    lock_path = tmp_path / "env.lock"
    save_lock(ENV, lock_path)
    data = json.loads(lock_path.read_text())
    assert isinstance(data, dict)


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_lock(tmp_path / "missing.lock")
