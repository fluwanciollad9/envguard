"""Tests for envguard.linter."""
import pytest
from pathlib import Path
from envguard.linter import lint_env, LintResult


def write_env(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_clean_env_no_issues(tmp_path):
    path = write_env(tmp_path, "APP_NAME=myapp\nDEBUG=false\n")
    result = lint_env(path)
    assert not result.has_issues


def test_blank_lines_and_comments_ignored(tmp_path):
    path = write_env(tmp_path, "# comment\n\nAPP=1\n")
    result = lint_env(path)
    assert not result.has_issues


def test_missing_equals_is_error(tmp_path):
    path = write_env(tmp_path, "BADLINE\n")
    result = lint_env(path)
    assert len(result.errors) == 1
    assert "no '='" in result.errors[0].message


def test_lowercase_key_is_warning(tmp_path):
    path = write_env(tmp_path, "app_name=myapp\n")
    result = lint_env(path)
    assert len(result.warnings) == 1
    assert "UPPER_SNAKE_CASE" in result.warnings[0].message


def test_mixed_case_key_is_warning(tmp_path):
    path = write_env(tmp_path, "AppName=myapp\n")
    result = lint_env(path)
    warnings = [w for w in result.warnings if "UPPER_SNAKE_CASE" in w.message]
    assert warnings


def test_trailing_whitespace_is_warning(tmp_path):
    path = write_env(tmp_path, "APP=value   \n")
    result = lint_env(path)
    assert any("Trailing whitespace" in w.message for w in result.warnings)


def test_empty_key_is_error(tmp_path):
    path = write_env(tmp_path, "=value\n")
    result = lint_env(path)
    assert any("Empty key" in e.message for e in result.errors)


def test_multiple_issues_reported(tmp_path):
    content = "BADLINE\nlower=val\nGOOD=ok\n"
    path = write_env(tmp_path, content)
    result = lint_env(path)
    assert len(result.errors) >= 1
    assert len(result.warnings) >= 1


def test_line_numbers_correct(tmp_path):
    path = write_env(tmp_path, "GOOD=ok\nBADLINE\n")
    result = lint_env(path)
    assert result.errors[0].line == 2
