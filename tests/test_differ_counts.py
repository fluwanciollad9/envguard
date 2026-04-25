"""Tests for envguard.differ_counts."""
import pytest
from envguard.differ_counts import diff_counts, CountDiffResult


SOURCE = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://localhost/db"}
TARGET = {"APP_HOST": "prod.example.com", "APP_PORT": "443", "SECRET_KEY": "abc123"}


def test_source_count():
    result = diff_counts(SOURCE, TARGET)
    assert result.source_count == 3


def test_target_count():
    result = diff_counts(SOURCE, TARGET)
    assert result.target_count == 3


def test_common_count():
    result = diff_counts(SOURCE, TARGET)
    assert result.common_count == 2  # APP_HOST, APP_PORT


def test_only_in_source():
    result = diff_counts(SOURCE, TARGET)
    assert result.only_in_source == 1  # DB_URL


def test_only_in_target():
    result = diff_counts(SOURCE, TARGET)
    assert result.only_in_target == 1  # SECRET_KEY


def test_key_count_delta_zero_when_same_size():
    result = diff_counts(SOURCE, TARGET)
    assert result.key_count_delta == 0


def test_key_count_delta_positive_when_target_larger():
    result = diff_counts({"A": "1"}, {"A": "1", "B": "2"})
    assert result.key_count_delta == 1


def test_key_count_delta_negative_when_target_smaller():
    result = diff_counts({"A": "1", "B": "2"}, {"A": "1"})
    assert result.key_count_delta == -1


def test_has_differences_true_when_keys_differ():
    result = diff_counts(SOURCE, TARGET)
    assert result.has_differences() is True


def test_has_differences_false_when_identical():
    env = {"KEY": "value"}
    result = diff_counts(env, env.copy())
    assert result.has_differences() is False


def test_avg_value_len_source():
    env = {"A": "12", "B": "1234"}  # avg = 3.0
    result = diff_counts(env, {})
    assert result.source_avg_value_len == pytest.approx(3.0)


def test_avg_value_len_empty_env():
    result = diff_counts({}, {})
    assert result.source_avg_value_len == 0.0
    assert result.target_avg_value_len == 0.0


def test_longest_key_source():
    env = {"SHORT": "x", "MUCH_LONGER_KEY": "y"}
    result = diff_counts(env, {})
    assert result.longest_key_source == "MUCH_LONGER_KEY"


def test_longest_key_target():
    result = diff_counts({}, {"ALPHA": "1", "BETA_GAMMA": "2"})
    assert result.longest_key_target == "BETA_GAMMA"


def test_longest_key_empty_env():
    result = diff_counts({}, {})
    assert result.longest_key_source == ""
    assert result.longest_key_target == ""


def test_summary_contains_counts():
    result = diff_counts(SOURCE, TARGET)
    s = result.summary()
    assert "Source keys: 3" in s
    assert "Target keys: 3" in s


def test_summary_contains_delta():
    result = diff_counts({"A": "1"}, {"A": "1", "B": "2"})
    assert "+1" in result.summary()
