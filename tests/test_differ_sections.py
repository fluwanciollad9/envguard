"""Tests for envguard.differ_sections."""
from __future__ import annotations

import pytest

from envguard.differ_sections import (
    SectionDiff,
    SectionDiffResult,
    _parse_sections,
    diff_sections,
)


SOURCE_LINES = [
    "# Database\n",
    "DB_HOST=localhost\n",
    "DB_PORT=5432\n",
    "# App\n",
    "DEBUG=true\n",
    "APP_NAME=myapp\n",
]

TARGET_LINES = [
    "# Database\n",
    "DB_HOST=prod.db.example.com\n",
    "DB_PORT=5432\n",
    "# App\n",
    "DEBUG=false\n",
    "APP_NAME=myapp\n",
]


def test_parse_sections_groups_by_comment_header():
    sections = _parse_sections(SOURCE_LINES)
    assert "# Database" in sections
    assert "# App" in sections


def test_parse_sections_default_bucket_for_headerless_keys():
    lines = ["FOO=bar\n", "# Section\n", "BAR=baz\n"]
    sections = _parse_sections(lines)
    assert "__default__" in sections
    assert sections["__default__"]["FOO"] == "bar"


def test_parse_sections_keys_assigned_to_correct_section():
    sections = _parse_sections(SOURCE_LINES)
    assert sections["# Database"]["DB_HOST"] == "localhost"
    assert sections["# App"]["DEBUG"] == "true"


def test_no_differences_when_identical():
    result = diff_sections(SOURCE_LINES, SOURCE_LINES)
    assert not result.has_differences


def test_modified_value_detected():
    result = diff_sections(SOURCE_LINES, TARGET_LINES)
    db_diff = result.diffs["# Database"]
    keys = [m[0] for m in db_diff.modified]
    assert "DB_HOST" in keys


def test_unmodified_value_not_in_modified():
    result = diff_sections(SOURCE_LINES, TARGET_LINES)
    db_diff = result.diffs["# Database"]
    keys = [m[0] for m in db_diff.modified]
    assert "DB_PORT" not in keys


def test_key_only_in_source_detected():
    extra = SOURCE_LINES + ["DB_SSL=true\n"]
    result = diff_sections(extra, TARGET_LINES)
    # DB_SSL added after last header (# App), so it lands in # App section
    assert result.has_differences


def test_key_only_in_target_detected():
    extra = TARGET_LINES + ["NEW_KEY=value\n"]
    result = diff_sections(SOURCE_LINES, extra)
    assert result.has_differences


def test_section_only_in_source_recorded():
    extra = SOURCE_LINES + ["# Extra\n", "X=1\n"]
    result = diff_sections(extra, TARGET_LINES)
    assert "# Extra" in result.sections_only_in_source


def test_section_only_in_target_recorded():
    extra = TARGET_LINES + ["# NewSection\n", "Y=2\n"]
    result = diff_sections(SOURCE_LINES, extra)
    assert "# NewSection" in result.sections_only_in_target


def test_section_diff_summary_identical():
    diff = SectionDiff(section="# DB")
    assert "identical" in diff.summary()


def test_section_diff_summary_shows_counts():
    diff = SectionDiff(
        section="# DB",
        only_in_source=["A"],
        modified=[("B", "old", "new")],
    )
    s = diff.summary()
    assert "only-in-source" in s
    assert "modified" in s


def test_result_summary_no_diff():
    result = diff_sections(SOURCE_LINES, SOURCE_LINES)
    assert "No section differences" in result.summary()


def test_result_summary_with_diff():
    result = diff_sections(SOURCE_LINES, TARGET_LINES)
    s = result.summary()
    assert "# Database" in s or "# App" in s
