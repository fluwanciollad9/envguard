"""Tests for envguard.differ_structure."""
import pytest

from envguard.differ_structure import StructureDiffResult, diff_structure, _infer_type


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------

def test_infer_type_empty():
    assert _infer_type("") == "empty"


def test_infer_type_bool_true():
    assert _infer_type("true") == "bool"


def test_infer_type_bool_false():
    assert _infer_type("False") == "bool"


def test_infer_type_int():
    assert _infer_type("42") == "int"


def test_infer_type_float():
    assert _infer_type("3.14") == "float"


def test_infer_type_str():
    assert _infer_type("hello") == "str"


# ---------------------------------------------------------------------------
# diff_structure
# ---------------------------------------------------------------------------

def test_identical_envs_no_differences():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = diff_structure(env, env.copy())
    assert not result.has_differences()


def test_key_counts_correct():
    src = {"A": "1", "B": "2"}
    tgt = {"A": "1"}
    result = diff_structure(src, tgt)
    assert result.source_key_count == 2
    assert result.target_key_count == 1


def test_only_in_source_detected():
    src = {"A": "1", "B": "2"}
    tgt = {"A": "1"}
    result = diff_structure(src, tgt)
    assert "B" in result.only_in_source
    assert result.only_in_target == []


def test_only_in_target_detected():
    src = {"A": "1"}
    tgt = {"A": "1", "C": "3"}
    result = diff_structure(src, tgt)
    assert "C" in result.only_in_target
    assert result.only_in_source == []


def test_empty_keys_detected_in_source():
    src = {"A": "", "B": "val"}
    tgt = {"A": "filled", "B": "val"}
    result = diff_structure(src, tgt)
    assert "A" in result.source_empty_keys
    assert result.target_empty_keys == []


def test_empty_keys_detected_in_target():
    src = {"A": "filled"}
    tgt = {"A": ""}
    result = diff_structure(src, tgt)
    assert "A" in result.target_empty_keys
    assert result.source_empty_keys == []


def test_type_change_str_to_int():
    src = {"PORT": "not-a-number"}
    tgt = {"PORT": "8080"}
    result = diff_structure(src, tgt)
    assert "PORT" in result.type_changes
    assert result.type_changes["PORT"] == ("str", "int")


def test_type_change_int_to_bool():
    src = {"FLAG": "1"}
    tgt = {"FLAG": "true"}
    result = diff_structure(src, tgt)
    assert "FLAG" in result.type_changes
    assert result.type_changes["FLAG"] == ("int", "bool")


def test_no_type_change_for_identical_types():
    src = {"NAME": "alice"}
    tgt = {"NAME": "bob"}
    result = diff_structure(src, tgt)
    assert "NAME" not in result.type_changes


def test_has_differences_true_when_keys_differ():
    result = diff_structure({"A": "1"}, {"B": "2"})
    assert result.has_differences()


def test_has_differences_false_for_identical():
    env = {"X": "hello", "Y": "42"}
    result = diff_structure(env, env.copy())
    assert not result.has_differences()


def test_summary_no_differences():
    env = {"A": "1"}
    result = diff_structure(env, env.copy())
    assert result.summary() == "no structural differences"


def test_summary_mentions_only_in_source():
    result = diff_structure({"A": "1", "B": "2"}, {"A": "1"})
    assert "only in source" in result.summary()
    assert "B" in result.summary()


def test_summary_mentions_type_changes():
    result = diff_structure({"PORT": "abc"}, {"PORT": "9000"})
    assert "type changes" in result.summary()
