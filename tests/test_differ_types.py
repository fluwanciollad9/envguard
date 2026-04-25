"""Tests for envguard.differ_types."""
from __future__ import annotations

import pytest

from envguard.differ_types import TypeDiffEntry, TypeDiffResult, _infer_type, diff_types


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------

def test_infer_type_empty():
    assert _infer_type("") == "empty"


def test_infer_type_bool_true():
    assert _infer_type("true") == "bool"
    assert _infer_type("True") == "bool"
    assert _infer_type("TRUE") == "bool"


def test_infer_type_bool_false():
    assert _infer_type("false") == "bool"


def test_infer_type_int():
    assert _infer_type("42") == "int"
    assert _infer_type("-7") == "int"


def test_infer_type_float():
    assert _infer_type("3.14") == "float"


def test_infer_type_url():
    assert _infer_type("https://example.com") == "url"
    assert _infer_type("http://localhost:8080") == "url"


def test_infer_type_str():
    assert _infer_type("hello") == "str"
    assert _infer_type("some-value_123") == "str"


# ---------------------------------------------------------------------------
# diff_types
# ---------------------------------------------------------------------------

def test_no_changes_when_identical():
    env = {"PORT": "8080", "DEBUG": "true"}
    result = diff_types(env, env)
    assert not result.has_differences()
    assert result.changed == []
    assert result.only_in_source == []
    assert result.only_in_target == []


def test_type_change_detected():
    src = {"PORT": "8080"}
    tgt = {"PORT": "auto"}
    result = diff_types(src, tgt)
    assert len(result.changed) == 1
    entry = result.changed[0]
    assert entry.key == "PORT"
    assert entry.source_type == "int"
    assert entry.target_type == "str"


def test_only_in_source_detected():
    src = {"A": "1", "B": "2"}
    tgt = {"A": "1"}
    result = diff_types(src, tgt)
    assert "B" in result.only_in_source
    assert result.only_in_target == []


def test_only_in_target_detected():
    src = {"A": "1"}
    tgt = {"A": "1", "C": "hello"}
    result = diff_types(src, tgt)
    assert "C" in result.only_in_target
    assert result.only_in_source == []


def test_unchanged_type_not_in_changed():
    env = {"FLAG": "true", "COUNT": "5"}
    result = diff_types(env, env)
    assert result.changed == []


def test_summary_no_differences():
    env = {"X": "1"}
    result = diff_types(env, env)
    assert result.summary() == "no type differences"


def test_summary_with_changes():
    src = {"X": "1"}
    tgt = {"X": "hello"}
    result = diff_types(src, tgt)
    assert "type change" in result.summary()


def test_labels_stored_on_result():
    result = diff_types({}, {}, source_label="dev", target_label="prod")
    assert result.source_label == "dev"
    assert result.target_label == "prod"


def test_entry_str_representation():
    entry = TypeDiffEntry(key="PORT", source_type="int", target_type="str")
    assert str(entry) == "PORT: int -> str"
