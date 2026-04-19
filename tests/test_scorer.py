import pytest
from envguard.scorer import score_env, ScoreResult


def test_perfect_score_clean_env():
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"}
    result = score_env(env)
    assert result.total == 100
    assert result.grade == "A"


def test_empty_value_penalises():
    env = {"KEY": ""}
    result = score_env(env)
    assert result.total < 100
    assert "empty value" in " ".join(result.penalties)


def test_multiple_empty_values_cumulative_penalty():
    env = {f"KEY{i}": "" for i in range(4)}
    result = score_env(env)
    assert result.total <= 80


def test_placeholder_value_penalises():
    env = {"API_URL": "<your_api_url>"}
    result = score_env(env)
    assert result.total < 100
    assert result.breakdown["placeholders"] == 1


def test_short_secret_penalises():
    env = {"API_KEY": "abc"}
    result = score_env(env)
    assert result.breakdown["short_secrets"] == 1
    assert result.total < 100


def test_long_secret_no_penalty():
    env = {"API_KEY": "supersecretvalue123"}
    result = score_env(env)
    assert result.breakdown["short_secrets"] == 0


def test_lowercase_key_no_penalty_without_strict():
    env = {"mykey": "value"}
    result = score_env(env)
    assert result.total == 100


def test_lowercase_key_penalised_in_strict_mode():
    env = {"mykey": "value"}
    result = score_env(env, strict=True)
    assert result.total < 100
    assert result.breakdown["lowercase_keys"] == 1


def test_grade_boundaries():
    assert ScoreResult(total=95, breakdown={}, penalties={}).grade == "A"
    assert ScoreResult(total=80, breakdown={}, penalties={}).grade == "B"
    assert ScoreResult(total=65, breakdown={}, penalties={}).grade == "C"
    assert ScoreResult(total=45, breakdown={}, penalties={}).grade == "D"
    assert ScoreResult(total=30, breakdown={}, penalties={}).grade == "F"


def test_summary_contains_score():
    env = {"KEY": ""}
    result = score_env(env)
    assert "Score:" in result.summary()
    assert "Grade:" in result.summary()


def test_score_never_negative():
    env = {f"key{i}": "" for i in range(20)}
    result = score_env(env, strict=True)
    assert result.total >= 0
