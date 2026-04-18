from __future__ import annotations
import pytest
from pathlib import Path
from envguard.duplicates import find_duplicates, DuplicateResult


def write_env(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_no_duplicates_clean_file(tmp_path):
    path = write_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = find_duplicates(path)
    assert not result.has_duplicates()
    assert result.duplicates == {}


def test_single_duplicate_key(tmp_path):
    path = write_env(tmp_path, "FOO=first\nBAR=ok\nFOO=second\n")
    result = find_duplicates(path)
    assert result.has_duplicates()
    assert "FOO" in result.duplicates
    assert result.duplicates["FOO"] == [1, 3]


def test_multiple_duplicate_keys(tmp_path):
    path = write_env(tmp_path, "A=1\nB=2\nA=3\nB=4\nC=5\n")
    result = find_duplicates(path)
    assert result.has_duplicates()
    assert set(result.duplicates.keys()) == {"A", "B"}


def test_comments_and_blanks_ignored(tmp_path):
    content = "# FOO=comment\n\nFOO=real\nBAR=val\n"
    path = write_env(tmp_path, content)
    result = find_duplicates(path)
    assert not result.has_duplicates()


def test_summary_no_duplicates(tmp_path):
    path = write_env(tmp_path, "X=1\n")
    result = find_duplicates(path)
    assert result.summary() == "No duplicate keys found."


def test_summary_with_duplicates(tmp_path):
    path = write_env(tmp_path, "KEY=a\nKEY=b\n")
    result = find_duplicates(path)
    summary = result.summary()
    assert "KEY" in summary
    assert "1" in summary
    assert "2" in summary


def test_triplicate_key(tmp_path):
    path = write_env(tmp_path, "FOO=1\nFOO=2\nFOO=3\n")
    result = find_duplicates(path)
    assert result.duplicates["FOO"] == [1, 2, 3]
