"""Tests for envguard.snapshotter."""
import json
import os
import tempfile
from pathlib import Path

import pytest

from envguard.snapshotter import (
    Snapshot,
    diff_with_snapshot,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


def write_env(path: str, content: str) -> None:
    Path(path).write_text(content)


def test_take_snapshot_captures_env(tmp_path):
    env_file = str(tmp_path / ".env")
    write_env(env_file, "FOO=bar\nBAZ=qux\n")
    snap = take_snapshot(env_file)
    assert snap.env == {"FOO": "bar", "BAZ": "qux"}
    assert snap.source == env_file
    assert snap.timestamp.endswith("Z")


def test_save_and_load_snapshot_roundtrip(tmp_path):
    env_file = str(tmp_path / ".env")
    snap_file = str(tmp_path / "snap.json")
    write_env(env_file, "KEY=value\n")
    snap = take_snapshot(env_file)
    save_snapshot(snap, snap_file)
    loaded = load_snapshot(snap_file)
    assert loaded.env == snap.env
    assert loaded.source == snap.source
    assert loaded.timestamp == snap.timestamp


def test_save_snapshot_writes_valid_json(tmp_path):
    env_file = str(tmp_path / ".env")
    snap_file = str(tmp_path / "snap.json")
    write_env(env_file, "A=1\n")
    snap = take_snapshot(env_file)
    save_snapshot(snap, snap_file)
    data = json.loads(Path(snap_file).read_text())
    assert "env" in data
    assert "timestamp" in data
    assert "source" in data


def test_diff_with_snapshot_detects_changes(tmp_path):
    env_file = str(tmp_path / ".env")
    snap_file = str(tmp_path / "snap.json")
    write_env(env_file, "FOO=old\nBAR=keep\n")
    snap = take_snapshot(env_file)
    save_snapshot(snap, snap_file)
    write_env(env_file, "FOO=new\nBAR=keep\nEXTRA=added\n")
    result = diff_with_snapshot(env_file, snap_file)
    assert "FOO" in result.changed
    assert "EXTRA" in result.extra
    assert result.missing == []


def test_diff_with_snapshot_detects_missing(tmp_path):
    env_file = str(tmp_path / ".env")
    snap_file = str(tmp_path / "snap.json")
    write_env(env_file, "FOO=bar\nGONE=yes\n")
    snap = take_snapshot(env_file)
    save_snapshot(snap, snap_file)
    write_env(env_file, "FOO=bar\n")
    result = diff_with_snapshot(env_file, snap_file)
    assert "GONE" in result.missing


def test_diff_with_snapshot_no_changes(tmp_path):
    """Diff against an identical env file should report no changes."""
    env_file = str(tmp_path / ".env")
    snap_file = str(tmp_path / "snap.json")
    write_env(env_file, "FOO=bar\nBAZ=qux\n")
    snap = take_snapshot(env_file)
    save_snapshot(snap, snap_file)
    result = diff_with_snapshot(env_file, snap_file)
    assert result.changed == []
    assert result.extra == []
    assert result.missing == []
