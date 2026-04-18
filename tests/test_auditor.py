"""Tests for envguard.auditor."""
import pytest
from envguard.auditor import audit_env, AuditResult


def test_no_issues_for_clean_env():
    env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "false"}
    result = audit_env(env)
    assert not result.has_issues


def test_empty_secret_is_error():
    result = audit_env({"API_KEY": ""})
    assert len(result.errors) == 1
    assert result.errors[0].key == "API_KEY"
    assert "empty" in result.errors[0].message


def test_placeholder_value_is_warning():
    result = audit_env({"DATABASE_URL": "changeme"})
    assert len(result.warnings) == 1
    assert "placeholder" in result.warnings[0].message.lower()


def test_short_secret_is_warning():
    result = audit_env({"TOKEN": "abc"})
    warnings = [w for w in result.warnings if "short" in w.message]
    assert warnings, "Expected a short-secret warning"


def test_secret_with_sufficient_length_no_warning():
    result = audit_env({"PASSWORD": "supersecretvalue"})
    short_warnings = [w for w in result.warnings if "short" in w.message]
    assert not short_warnings


def test_whitespace_value_is_warning():
    result = audit_env({"SOME_VAR": "  value  "})
    ws_warnings = [w for w in result.warnings if "whitespace" in w.message]
    assert ws_warnings


def test_placeholder_case_insensitive():
    result = audit_env({"SOME_KEY": "TODO"})
    assert result.has_issues


def test_multiple_issues_accumulated():
    env = {
        "API_KEY": "",
        "SECRET": "x",
        "DB_PASS": "changeme",
    }
    result = audit_env(env)
    assert len(result.errors) >= 1
    assert len(result.warnings) >= 1


def test_has_issues_false_when_clean():
    result = audit_env({"REGION": "us-east-1"})
    assert result.has_issues is False


def test_errors_and_warnings_partition_issues():
    result = audit_env({"TOKEN": "", "SOME_VAR": "  hi  "})
    all_issues = result.errors + result.warnings
    assert set(i.key for i in all_issues) == set(i.key for i in result.issues)
