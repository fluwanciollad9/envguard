"""Tests for envguard.cascader."""
from __future__ import annotations

import pytest

from envguard.cascader import CascadeResult, cascade_envs


def test_no_overlap_all_keys_present():
    a = {"A": "1", "B": "2"}
    b = {"C": "3"}
    result = cascade_envs([a, b])
    assert result.env == {"A": "1", "B": "2", "C": "3"}


def test_later_source_overrides_earlier():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    result = cascade_envs([a, b])
    assert result.env["KEY"] == "new"


def test_override_count_incremented():
    a = {"X": "1", "Y": "2"}
    b = {"X": "10", "Y": "20"}
    result = cascade_envs([a, b])
    assert result.override_count == 2


def test_no_overrides_when_disjoint():
    result = cascade_envs([{"A": "1"}, {"B": "2"}])
    assert result.override_count == 0


def test_origin_tracks_last_source():
    a = {"KEY": "from_a"}
    b = {"KEY": "from_b"}
    result = cascade_envs([a, b])
    assert result.source_for("KEY") == 1


def test_origin_tracks_only_source():
    result = cascade_envs([{"SOLO": "yes"}])
    assert result.source_for("SOLO") == 0


def test_empty_sources_returns_empty_env():
    result = cascade_envs([])
    assert result.env == {}
    assert result.override_count == 0


def test_single_source_no_overrides():
    src = {"A": "1", "B": "2"}
    result = cascade_envs([src])
    assert result.env == src
    assert result.override_count == 0


def test_three_sources_last_wins():
    a = {"K": "a"}
    b = {"K": "b"}
    c = {"K": "c"}
    result = cascade_envs([a, b, c])
    assert result.env["K"] == "c"
    assert result.source_for("K") == 2


def test_summary_string_contains_key_count():
    result = cascade_envs([{"A": "1"}, {"B": "2"}])
    assert "2 key(s)" in result.summary()


def test_summary_string_contains_override_count():
    result = cascade_envs([{"A": "1"}, {"A": "2"}])
    assert "1 override(s)" in result.summary()
