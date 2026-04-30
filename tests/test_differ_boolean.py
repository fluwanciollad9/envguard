"""Tests for envguard.differ_boolean."""
import pytest
from envguard.differ_boolean import (
    BoolDiffEntry,
    BoolDiffResult,
    _is_bool,
    _to_bool,
    diff_boolean,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make(source: dict, target: dict) -> BoolDiffResult:
    return diff_boolean(source, target)


# ---------------------------------------------------------------------------
# _is_bool / _to_bool
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("v", ["true", "True", "TRUE", "1", "yes", "on"])
def test_is_bool_true_variants(v):
    assert _is_bool(v) is True


@pytest.mark.parametrize("v", ["false", "False", "FALSE", "0", "no", "off"])
def test_is_bool_false_variants(v):
    assert _is_bool(v) is True


@pytest.mark.parametrize("v", ["hello", "2", "", "enabled", "nope"])
def test_non_bool_values(v):
    assert _is_bool(v) is False


def test_to_bool_true():
    assert _to_bool("yes") is True


def test_to_bool_false():
    assert _to_bool("0") is False


def test_to_bool_non_bool_returns_none():
    assert _to_bool("hello") is None


# ---------------------------------------------------------------------------
# diff_boolean
# ---------------------------------------------------------------------------

def test_no_differences_when_identical():
    env = {"DEBUG": "true", "VERBOSE": "false"}
    result = diff_boolean(env, env)
    assert not result.has_differences()
    assert result.changed == []


def test_changed_key_detected():
    result = _make({"DEBUG": "true"}, {"DEBUG": "false"})
    assert len(result.changed) == 1
    entry = result.changed[0]
    assert entry.key == "DEBUG"
    assert entry.source_bool is True
    assert entry.target_bool is False


def test_semantic_change_true_to_one_is_not_semantic():
    # "true" and "1" both parse to True — no semantic change
    result = _make({"FLAG": "true"}, {"FLAG": "1"})
    assert len(result.changed) == 1
    assert not result.changed[0].is_semantic_change()


def test_only_in_source_populated():
    result = _make({"DEBUG": "true", "VERBOSE": "yes"}, {"DEBUG": "true"})
    assert "VERBOSE" in result.only_in_source
    assert result.only_in_target == []


def test_only_in_target_populated():
    result = _make({"DEBUG": "true"}, {"DEBUG": "true", "CACHE": "off"})
    assert "CACHE" in result.only_in_target
    assert result.only_in_source == []


def test_non_bool_keys_skipped():
    result = _make({"DB_HOST": "localhost", "DEBUG": "true"}, {"DB_HOST": "prod", "DEBUG": "true"})
    assert not result.has_differences()


def test_has_differences_true_when_changed():
    result = _make({"FLAG": "on"}, {"FLAG": "off"})
    assert result.has_differences()


def test_summary_no_differences():
    env = {"A": "true"}
    result = diff_boolean(env, env)
    assert result.summary() == "no boolean differences"


def test_summary_with_changes():
    result = _make({"A": "true", "B": "yes"}, {"A": "false", "C": "on"})
    s = result.summary()
    assert "changed" in s


def test_entry_str_representation():
    entry = BoolDiffEntry("DEBUG", "true", "false", True, False)
    s = str(entry)
    assert "DEBUG" in s
    assert "true" in s
    assert "false" in s


def test_semantic_changes_filters_correctly():
    result = _make({"A": "true", "B": "true"}, {"A": "false", "B": "1"})
    sem = result.semantic_changes()
    keys = [e.key for e in sem]
    assert "A" in keys
    assert "B" not in keys
