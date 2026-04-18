"""Tests for envguard.reporter formatting helpers."""
import json

import pytest

from envguard.differ import DiffResult
from envguard.reporter import format_diff, format_validation
from envguard.validator import ValidationResult


def make_diff(**kwargs) -> DiffResult:
    defaults = {"missing_in_target": set(), "extra_in_target": set(), "changed_values": {}}
    defaults.update(kwargs)
    return DiffResult(**defaults)


def make_validation(**kwargs) -> ValidationResult:
    defaults = {"missing_required": set(), "empty_required": set(), "unknown_keys": set()}
    defaults.update(kwargs)
    return ValidationResult(**defaults)


def test_format_diff_no_differences():
    assert format_diff(make_diff()) == "No differences found."


def test_format_diff_text_missing():
    out = format_diff(make_diff(missing_in_target={"FOO"}))
    assert "MISSING" in out and "FOO" in out


def test_format_diff_text_extra():
    out = format_diff(make_diff(extra_in_target={"BAR"}))
    assert "EXTRA" in out and "BAR" in out


def test_format_diff_text_changed():
    out = format_diff(make_diff(changed_values={"KEY": ("old", "new")}))
    assert "CHANGED" in out and "KEY" in out


def test_format_diff_json():
    result = make_diff(missing_in_target={"A"}, extra_in_target={"B"})
    data = json.loads(format_diff(result, fmt="json"))
    assert "A" in data["missing_in_target"]
    assert "B" in data["extra_in_target"]


def test_format_validation_passed():
    assert format_validation(make_validation()) == "Validation passed."


def test_format_validation_text_missing():
    out = format_validation(make_validation(missing_required={"SECRET"}))
    assert "MISSING" in out and "SECRET" in out


def test_format_validation_text_empty():
    out = format_validation(make_validation(empty_required={"TOKEN"}))
    assert "EMPTY" in out and "TOKEN" in out


def test_format_validation_json():
    result = make_validation(unknown_keys={"EXTRA_VAR"})
    data = json.loads(format_validation(result, fmt="json"))
    assert "EXTRA_VAR" in data["unknown_keys"]
