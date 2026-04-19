"""Tests for envguard.differ_env."""
import pytest
from envguard.differ_env import diff_env_files, EnvDiff


def test_no_differences_when_identical():
    env = {"A": "1", "B": "2"}
    result = diff_env_files(env, env.copy())
    assert not result.has_differences()
    assert result.unchanged == env


def test_added_key_detected():
    src = {"A": "1"}
    tgt = {"A": "1", "B": "new"}
    result = diff_env_files(src, tgt)
    assert "B" in result.added
    assert result.added["B"] == "new"


def test_removed_key_detected():
    src = {"A": "1", "B": "old"}
    tgt = {"A": "1"}
    result = diff_env_files(src, tgt)
    assert "B" in result.removed
    assert result.removed["B"] == "old"


def test_modified_key_detected():
    src = {"A": "old"}
    tgt = {"A": "new"}
    result = diff_env_files(src, tgt)
    assert "A" in result.modified
    assert result.modified["A"] == ("old", "new")


def test_unchanged_key_not_in_changes():
    env = {"X": "same"}
    result = diff_env_files(env, env.copy())
    assert "X" not in result.added
    assert "X" not in result.removed
    assert "X" not in result.modified
    assert "X" in result.unchanged


def test_has_differences_true_on_add():
    result = diff_env_files({}, {"K": "v"})
    assert result.has_differences()


def test_summary_no_differences():
    result = diff_env_files({"A": "1"}, {"A": "1"})
    assert result.summary() == "No differences found."


def test_summary_with_changes():
    result = diff_env_files({"A": "old", "B": "x"}, {"A": "new", "C": "y"})
    s = result.summary()
    assert "added" in s
    assert "removed" in s
    assert "modified" in s


def test_source_and_target_labels_stored():
    result = diff_env_files({}, {}, source_file="dev.env", target_file="prod.env")
    assert result.source_file == "dev.env"
    assert result.target_file == "prod.env"
