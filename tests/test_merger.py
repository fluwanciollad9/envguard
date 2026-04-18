"""Tests for envguard.merger."""
import pytest
from envguard.merger import merge_envs, MergeResult


def test_merge_no_overlap():
    sources = [("base", {"A": "1", "B": "2"}), ("prod", {"C": "3"})]
    result = merge_envs(sources)
    assert result.merged == {"A": "1", "B": "2", "C": "3"}
    assert result.override_count == 0


def test_merge_later_overrides_earlier():
    sources = [("base", {"A": "1", "B": "old"}), ("prod", {"B": "new", "C": "3"})]
    result = merge_envs(sources)
    assert result.merged["B"] == "new"
    assert result.merged["A"] == "1"
    assert result.override_count == 1
    key, old_src, new_src, new_val = result.overrides[0]
    assert key == "B"
    assert old_src == "base"
    assert new_src == "prod"
    assert new_val == "new"


def test_merge_multiple_overrides():
    sources = [
        ("base", {"X": "a", "Y": "b"}),
        ("staging", {"X": "c"}),
        ("prod", {"X": "d", "Y": "e"}),
    ]
    result = merge_envs(sources)
    assert result.merged["X"] == "d"
    assert result.merged["Y"] == "e"
    assert result.override_count == 3


def test_merge_empty_sources():
    result = merge_envs([])
    assert result.merged == {}
    assert result.override_count == 0


def test_merge_single_source():
    result = merge_envs([("only", {"K": "v"})])
    assert result.merged == {"K": "v"}
    assert result.override_count == 0
