"""Tests for envguard.differ_age."""
from __future__ import annotations

import json
import pytest

from envguard.differ_age import diff_age, AgeDiffEntry, AgeDiffResult, _load_timestamps


def write_ts(tmp_path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def test_no_differences_when_identical(tmp_path):
    ts = {"KEY_A": 1000.0, "KEY_B": 2000.0}
    src = write_ts(tmp_path, "src.json", ts)
    tgt = write_ts(tmp_path, "tgt.json", ts)
    result = diff_age(src, tgt)
    assert not result.has_differences()
    assert result.changed == []
    assert result.only_in_source == []
    assert result.only_in_target == []


def test_modified_timestamp_detected(tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 1500.0})
    result = diff_age(src, tgt)
    assert result.has_differences()
    assert len(result.changed) == 1
    entry = result.changed[0]
    assert entry.key == "KEY_A"
    assert entry.is_newer
    assert not entry.is_older
    assert entry.delta_seconds == pytest.approx(500.0)


def test_only_in_source_detected(tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0, "KEY_B": 2000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 1000.0})
    result = diff_age(src, tgt)
    assert "KEY_B" in result.only_in_source
    assert result.has_differences()


def test_only_in_target_detected(tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 1000.0, "KEY_B": 9999.0})
    result = diff_age(src, tgt)
    assert "KEY_B" in result.only_in_target


def test_threshold_filters_small_deltas(tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 1001.0})
    result = diff_age(src, tgt, threshold=5.0)
    assert not result.has_differences()


def test_threshold_allows_large_deltas(tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 1010.0})
    result = diff_age(src, tgt, threshold=5.0)
    assert result.has_differences()


def test_summary_no_differences(tmp_path):
    ts = {"KEY_A": 1000.0}
    src = write_ts(tmp_path, "src.json", ts)
    tgt = write_ts(tmp_path, "tgt.json", ts)
    result = diff_age(src, tgt)
    assert result.summary() == "no age differences"


def test_summary_with_changes(tmp_path):
    src = write_ts(tmp_path, "src.json", {"KEY_A": 1000.0})
    tgt = write_ts(tmp_path, "tgt.json", {"KEY_A": 2000.0})
    result = diff_age(src, tgt)
    assert "1 key(s) with differing timestamps" in result.summary()


def test_missing_timestamp_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        diff_age(str(tmp_path / "missing.json"), str(tmp_path / "also_missing.json"))


def test_age_diff_entry_str():
    entry = AgeDiffEntry(key="DB_PASS", source_mtime=1000.0, target_mtime=1600.0)
    text = str(entry)
    assert "DB_PASS" in text
    assert "newer" in text
    assert "600.0" in text


def test_load_timestamps_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not-json")
    with pytest.raises(Exception):
        _load_timestamps(str(bad))
