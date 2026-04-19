import pytest
from envguard.filterer import filter_env, FilterResult


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envguard",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
}


def test_matched_keys_returned():
    result = filter_env(ENV, r"^DB_")
    assert "DB_HOST" in result.matched
    assert "DB_PORT" in result.matched


def test_excluded_keys_not_in_matched():
    result = filter_env(ENV, r"^DB_")
    assert "APP_NAME" in result.excluded
    assert "DEBUG" in result.excluded


def test_invert_returns_non_matching():
    result = filter_env(ENV, r"^DB_", invert=True)
    assert "DB_HOST" not in result.matched
    assert "APP_NAME" in result.matched


def test_match_count():
    result = filter_env(ENV, r"^DB_")
    assert result.match_count() == 2


def test_pattern_stored_on_result():
    result = filter_env(ENV, r"SECRET")
    assert result.pattern == r"SECRET"


def test_key_and_value_matching():
    result = filter_env(ENV, r"localhost", key_only=False)
    assert "DB_HOST" in result.matched


def test_key_only_ignores_value():
    result = filter_env(ENV, r"localhost", key_only=True)
    assert "DB_HOST" not in result.matched


def test_no_matches_returns_empty_matched():
    result = filter_env(ENV, r"^NONEXISTENT")
    assert result.matched == {}
    assert len(result.excluded) == len(ENV)


def test_invalid_pattern_raises_value_error():
    with pytest.raises(ValueError, match="Invalid regex"):
        filter_env(ENV, r"[invalid")


def test_summary_contains_count_and_pattern():
    result = filter_env(ENV, r"^DB_")
    s = result.summary()
    assert "2" in s
    assert "^DB_" in s
