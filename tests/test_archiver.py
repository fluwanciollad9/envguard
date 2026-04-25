"""Tests for envguard.archiver and envguard.cli_archive."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from envguard.archiver import ArchiveResult, archive_env, _make_timestamp
from envguard.cli_archive import archive_cmd

FIXED_DT = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
FIXED_TS = "20240615T120000Z"


def write_env(tmp_path: Path, name: str = ".env", content: str = "KEY=value\n") -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Unit tests for archiver module
# ---------------------------------------------------------------------------

def test_make_timestamp_uses_utc():
    ts = _make_timestamp(FIXED_DT)
    assert ts == FIXED_TS


def test_archive_creates_file(tmp_path: Path):
    src = write_env(tmp_path)
    result = archive_env(src, dt=FIXED_DT)
    assert result.archive_path.exists()


def test_archive_filename_contains_timestamp(tmp_path: Path):
    src = write_env(tmp_path)
    result = archive_env(src, dt=FIXED_DT)
    assert FIXED_TS in result.archive_path.name


def test_archive_default_suffix(tmp_path: Path):
    src = write_env(tmp_path)
    result = archive_env(src, dt=FIXED_DT)
    assert result.archive_path.name.endswith(".bak")


def test_archive_custom_suffix(tmp_path: Path):
    src = write_env(tmp_path)
    result = archive_env(src, suffix=".archive", dt=FIXED_DT)
    assert result.archive_path.name.endswith(".archive")


def test_archive_to_separate_dir(tmp_path: Path):
    src = write_env(tmp_path)
    out_dir = tmp_path / "backups"
    result = archive_env(src, archive_dir=out_dir, dt=FIXED_DT)
    assert result.archive_path.parent == out_dir
    assert result.archive_path.exists()


def test_archive_content_matches_source(tmp_path: Path):
    content = "FOO=bar\nBAZ=qux\n"
    src = write_env(tmp_path, content=content)
    result = archive_env(src, dt=FIXED_DT)
    assert result.archive_path.read_text() == content


def test_archive_size_bytes_reported(tmp_path: Path):
    content = "KEY=value\n"
    src = write_env(tmp_path, content=content)
    result = archive_env(src, dt=FIXED_DT)
    assert result.size_bytes == len(content.encode())


def test_archive_existed_false_for_new_file(tmp_path: Path):
    src = write_env(tmp_path)
    result = archive_env(src, dt=FIXED_DT)
    assert result.existed is False


def test_archive_missing_source_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        archive_env(tmp_path / "missing.env")


def test_summary_contains_source_and_dest(tmp_path: Path):
    src = write_env(tmp_path)
    result = archive_env(src, dt=FIXED_DT)
    s = result.summary()
    assert str(src) in s
    assert str(result.archive_path) in s


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_text_output(tmp_path: Path):
    src = write_env(tmp_path)
    runner = CliRunner()
    res = runner.invoke(archive_cmd, [str(src)])
    assert res.exit_code == 0
    assert "Archived" in res.output


def test_cli_json_output(tmp_path: Path):
    src = write_env(tmp_path)
    runner = CliRunner()
    res = runner.invoke(archive_cmd, [str(src), "--format", "json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert "archive_path" in data
    assert "timestamp" in data
    assert data["existed"] is False


def test_cli_custom_dir(tmp_path: Path):
    src = write_env(tmp_path)
    out_dir = tmp_path / "archives"
    runner = CliRunner()
    res = runner.invoke(archive_cmd, [str(src), "--dir", str(out_dir)])
    assert res.exit_code == 0
    assert out_dir.exists()
