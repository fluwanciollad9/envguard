"""Tests for envguard.profiler."""
import pytest
from envguard.profiler import profile_env, _shannon_entropy


def test_total_keys_counted():
    env = {"A": "1", "B": "2", "C": "3"}
    result = profile_env(env)
    assert result.total_keys == 3


def test_empty_keys_detected():
    env = {"A": "", "B": "hello", "C": ""}
    result = profile_env(env)
    assert set(result.empty_keys) == {"A", "C"}


def test_no_empty_keys():
    env = {"A": "x", "B": "y"}
    result = profile_env(env)
    assert result.empty_keys == []


def test_long_values_detected():
    env = {"SHORT": "hi", "LONG": "x" * 200}
    result = profile_env(env, long_value_threshold=100)
    assert result.long_values == ["LONG"]


def test_long_values_none_above_threshold():
    env = {"A": "abc", "B": "def"}
    result = profile_env(env, long_value_threshold=100)
    assert result.long_values == []


def test_avg_value_length():
    env = {"A": "ab", "B": "abcd"}  # lengths 2 and 4 -> avg 3.0
    result = profile_env(env)
    assert result.avg_value_length == pytest.approx(3.0)


def test_avg_value_length_empty_env():
    result = profile_env({})
    assert result.avg_value_length == 0.0


def test_entropy_scores_present_for_all_keys():
    env = {"A": "hello", "B": "world"}
    result = profile_env(env)
    assert set(result.entropy_scores.keys()) == {"A", "B"}


def test_entropy_empty_value_is_zero():
    assert _shannon_entropy("") == 0.0


def test_entropy_single_char_is_zero():
    assert _shannon_entropy("aaaa") == pytest.approx(0.0)


def test_entropy_high_for_diverse_string():
    score = _shannon_entropy("abcdefgh")
    assert score > 2.0


def test_summary_contains_total_keys():
    env = {"X": "1", "Y": ""}
    result = profile_env(env)
    assert "2" in result.summary()
