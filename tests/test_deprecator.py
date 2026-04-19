"""Tests for envguard.deprecator."""
import pytest
from envguard.deprecator import check_deprecations, DeprecateResult


DEPRECATIONS = {
    "OLD_API_KEY": {"message": "Renamed.", "replacement": "API_KEY"},
    "LEGACY_HOST": {"message": "No longer used."},
}


def test_no_issues_for_clean_env():
    env = {"API_KEY": "abc", "HOST": "localhost"}
    result = check_deprecations(env, DEPRECATIONS)
    assert not result.has_issues()
    assert result.checked == 2


def test_deprecated_key_detected():
    env = {"OLD_API_KEY": "secret"}
    result = check_deprecations(env, DEPRECATIONS)
    assert result.has_issues()
    assert len(result.issues) == 1
    assert result.issues[0].key == "OLD_API_KEY"


def test_replacement_present_when_provided():
    env = {"OLD_API_KEY": "x"}
    result = check_deprecations(env, DEPRECATIONS)
    assert result.issues[0].replacement == "API_KEY"


def test_no_replacement_when_absent():
    env = {"LEGACY_HOST": "old.host"}
    result = check_deprecations(env, DEPRECATIONS)
    assert result.issues[0].replacement is None


def test_multiple_deprecated_keys():
    env = {"OLD_API_KEY": "a", "LEGACY_HOST": "b", "GOOD_KEY": "c"}
    result = check_deprecations(env, DEPRECATIONS)
    assert len(result.issues) == 2
    assert result.checked == 3


def test_summary_no_issues():
    env = {"FINE": "value"}
    result = check_deprecations(env, DEPRECATIONS)
    assert "No deprecated" in result.summary()
    assert "1 checked" in result.summary()


def test_summary_with_issues():
    env = {"OLD_API_KEY": "x"}
    result = check_deprecations(env, DEPRECATIONS)
    summary = result.summary()
    assert "1 deprecated" in summary
    assert "OLD_API_KEY" in summary
    assert "API_KEY" in summary


def test_str_issue_without_replacement():
    env = {"LEGACY_HOST": "h"}
    result = check_deprecations(env, DEPRECATIONS)
    s = str(result.issues[0])
    assert "LEGACY_HOST" in s
    assert "use" not in s


def test_empty_env_no_issues():
    result = check_deprecations({}, DEPRECATIONS)
    assert not result.has_issues()
    assert result.checked == 0
