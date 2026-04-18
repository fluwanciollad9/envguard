"""Tests for envguard.typecheck."""
import pytest
from envguard.typecheck import typecheck_env, TypeCheckResult, TypeIssue


def test_no_issues_for_valid_types():
    env = {"PORT": "8080", "DEBUG": "true", "RATIO": "3.14"}
    result = typecheck_env(env, {"PORT": "int", "DEBUG": "bool", "RATIO": "float"})
    assert not result.has_issues()


def test_invalid_int_flagged():
    result = typecheck_env({"PORT": "abc"}, {"PORT": "int"})
    assert result.has_issues()
    assert result.issues[0].key == "PORT"
    assert result.issues[0].expected == "int"


def test_invalid_bool_flagged():
    result = typecheck_env({"DEBUG": "maybe"}, {"DEBUG": "bool"})
    assert result.has_issues()


def test_valid_bool_variants():
    for val in ("true", "false", "1", "0", "yes", "no", "True", "FALSE"):
        result = typecheck_env({"FLAG": val}, {"FLAG": "bool"})
        assert not result.has_issues(), f"Expected {val!r} to pass bool check"


def test_valid_url():
    result = typecheck_env({"API": "https://example.com/path"}, {"API": "url"})
    assert not result.has_issues()


def test_invalid_url_flagged():
    result = typecheck_env({"API": "not-a-url"}, {"API": "url"})
    assert result.has_issues()


def test_valid_email():
    result = typecheck_env({"ADMIN": "admin@example.com"}, {"ADMIN": "email"})
    assert not result.has_issues()


def test_invalid_email_flagged():
    result = typecheck_env({"ADMIN": "not-an-email"}, {"ADMIN": "email"})
    assert result.has_issues()


def test_missing_key_in_env_skipped():
    result = typecheck_env({}, {"PORT": "int"})
    assert not result.has_issues()


def test_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown type"):
        typecheck_env({"X": "val"}, {"X": "uuid"})


def test_summary_no_issues():
    result = TypeCheckResult()
    assert "All values" in result.summary()


def test_summary_with_issues():
    result = TypeCheckResult(issues=[TypeIssue(key="PORT", expected="int", actual_value="abc")])
    assert "1 type issue" in result.summary()
    assert "PORT" in result.summary()


def test_multiple_issues():
    env = {"PORT": "abc", "DEBUG": "maybe", "NAME": "valid"}
    result = typecheck_env(env, {"PORT": "int", "DEBUG": "bool"})
    assert len(result.issues) == 2
