"""Tests for envguard.differ_comments."""
from __future__ import annotations

from pathlib import Path

import pytest

from envguard.differ_comments import (
    CommentDiffEntry,
    CommentDiffResult,
    diff_comments,
)


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_no_differences_when_comments_identical(tmp_path):
    src = write_env(tmp_path, "src.env", "KEY=value # same comment\n")
    tgt = write_env(tmp_path, "tgt.env", "KEY=value # same comment\n")
    result = diff_comments(src, tgt)
    assert not result.has_differences()


def test_added_comment_detected(tmp_path):
    src = write_env(tmp_path, "src.env", "KEY=value\n")
    tgt = write_env(tmp_path, "tgt.env", "KEY=value # new comment\n")
    result = diff_comments(src, tgt)
    assert result.has_differences()
    assert len(result.changes) == 1
    entry = result.changes[0]
    assert entry.key == "KEY"
    assert entry.is_added()
    assert entry.source_comment is None
    assert entry.target_comment == "new comment"


def test_removed_comment_detected(tmp_path):
    src = write_env(tmp_path, "src.env", "KEY=value # old comment\n")
    tgt = write_env(tmp_path, "tgt.env", "KEY=value\n")
    result = diff_comments(src, tgt)
    assert result.has_differences()
    entry = result.changes[0]
    assert entry.is_removed()
    assert entry.source_comment == "old comment"
    assert entry.target_comment is None


def test_modified_comment_detected(tmp_path):
    src = write_env(tmp_path, "src.env", "KEY=value # before\n")
    tgt = write_env(tmp_path, "tgt.env", "KEY=value # after\n")
    result = diff_comments(src, tgt)
    assert result.has_differences()
    entry = result.changes[0]
    assert entry.is_modified()
    assert entry.source_comment == "before"
    assert entry.target_comment == "after"


def test_unchanged_key_not_in_changes(tmp_path):
    src = write_env(tmp_path, "src.env", "A=1 # note\nB=2\n")
    tgt = write_env(tmp_path, "tgt.env", "A=1 # note\nB=2 # added\n")
    result = diff_comments(src, tgt)
    keys_in_changes = [c.key for c in result.changes]
    assert "A" not in keys_in_changes
    assert "B" in keys_in_changes


def test_all_keys_union_populated(tmp_path):
    src = write_env(tmp_path, "src.env", "A=1\nB=2\n")
    tgt = write_env(tmp_path, "tgt.env", "B=2\nC=3\n")
    result = diff_comments(src, tgt)
    assert set(result.all_keys) == {"A", "B", "C"}


def test_summary_no_differences(tmp_path):
    src = write_env(tmp_path, "src.env", "X=1 # same\n")
    tgt = write_env(tmp_path, "tgt.env", "X=1 # same\n")
    result = diff_comments(src, tgt)
    assert "No comment differences" in result.summary()


def test_summary_mentions_added(tmp_path):
    src = write_env(tmp_path, "src.env", "KEY=val\n")
    tgt = write_env(tmp_path, "tgt.env", "KEY=val # hi\n")
    result = diff_comments(src, tgt)
    assert "added" in result.summary()


def test_str_representation_added():
    entry = CommentDiffEntry(key="FOO", source_comment=None, target_comment="desc")
    assert "FOO" in str(entry)
    assert "desc" in str(entry)


def test_str_representation_removed():
    entry = CommentDiffEntry(key="BAR", source_comment="old", target_comment=None)
    assert "BAR" in str(entry)
    assert "old" in str(entry)


def test_blank_lines_and_standalone_comments_ignored(tmp_path):
    src = write_env(tmp_path, "src.env", "# header\n\nKEY=val\n")
    tgt = write_env(tmp_path, "tgt.env", "# different header\n\nKEY=val\n")
    result = diff_comments(src, tgt)
    assert not result.has_differences()
