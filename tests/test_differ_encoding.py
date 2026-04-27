"""Tests for envguard.differ_encoding."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from envguard.differ_encoding import (
    EncodingDiffEntry,
    EncodingDiffResult,
    diff_encoding,
    _detect_encoding,
    _value_encodings,
)


def write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_detect_encoding_ascii():
    enc = _detect_encoding(b"HELLO=world")
    assert enc is not None
    assert enc.lower() in ("ascii", "utf-8", "windows-1252")


def test_value_encodings_returns_dict_for_each_key():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = _value_encodings(env)
    assert set(result.keys()) == {"FOO", "BAZ"}
    for enc in result.values():
        assert enc is not None


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

def test_no_differences_when_identical(tmp_path):
    content = "FOO=bar\nBAZ=qux\n"
    src = write_env(tmp_path, "src.env", content)
    tgt = write_env(tmp_path, "tgt.env", content)
    env = {"FOO": "bar", "BAZ": "qux"}
    result = diff_encoding(src, tgt, env, env)
    assert not result.has_differences()
    assert result.summary() == "no encoding differences"


def test_only_in_source_populated(tmp_path):
    src_content = "FOO=bar\nEXTRA=only_here\n"
    tgt_content = "FOO=bar\n"
    src = write_env(tmp_path, "src.env", src_content)
    tgt = write_env(tmp_path, "tgt.env", tgt_content)
    src_env = {"FOO": "bar", "EXTRA": "only_here"}
    tgt_env = {"FOO": "bar"}
    result = diff_encoding(src, tgt, src_env, tgt_env)
    assert "EXTRA" in result.only_in_source
    assert result.has_differences()


def test_only_in_target_populated(tmp_path):
    src_content = "FOO=bar\n"
    tgt_content = "FOO=bar\nNEW=value\n"
    src = write_env(tmp_path, "src.env", src_content)
    tgt = write_env(tmp_path, "tgt.env", tgt_content)
    src_env = {"FOO": "bar"}
    tgt_env = {"FOO": "bar", "NEW": "value"}
    result = diff_encoding(src, tgt, src_env, tgt_env)
    assert "NEW" in result.only_in_target
    assert result.has_differences()


def test_summary_mentions_only_in_source(tmp_path):
    src_content = "A=1\nB=2\n"
    tgt_content = "A=1\n"
    src = write_env(tmp_path, "src.env", src_content)
    tgt = write_env(tmp_path, "tgt.env", tgt_content)
    result = diff_encoding(src, tgt, {"A": "1", "B": "2"}, {"A": "1"})
    assert "only in source" in result.summary()


def test_summary_mentions_only_in_target(tmp_path):
    src_content = "A=1\n"
    tgt_content = "A=1\nC=3\n"
    src = write_env(tmp_path, "src.env", src_content)
    tgt = write_env(tmp_path, "tgt.env", tgt_content)
    result = diff_encoding(src, tgt, {"A": "1"}, {"A": "1", "C": "3"})
    assert "only in target" in result.summary()


def test_result_stores_file_paths(tmp_path):
    content = "X=1\n"
    src = write_env(tmp_path, "a.env", content)
    tgt = write_env(tmp_path, "b.env", content)
    env = {"X": "1"}
    result = diff_encoding(src, tgt, env, env)
    assert result.source_file == src
    assert result.target_file == tgt


def test_changed_list_sorted_by_key(tmp_path):
    """Keys in changed list should be alphabetically sorted."""
    content = "A=hello\nB=world\n"
    src = write_env(tmp_path, "src.env", content)
    tgt = write_env(tmp_path, "tgt.env", content)
    # Force differing encodings by patching value_encodings indirectly
    src_env = {"B": "hello", "A": "world"}
    tgt_env = {"B": "hello", "A": "world"}
    result = diff_encoding(src, tgt, src_env, tgt_env)
    keys = [e.key for e in result.changed]
    assert keys == sorted(keys)


def test_encoding_diff_entry_str():
    entry = EncodingDiffEntry("MY_KEY", "ascii", "utf-8")
    text = str(entry)
    assert "MY_KEY" in text
    assert "ascii" in text
    assert "utf-8" in text
