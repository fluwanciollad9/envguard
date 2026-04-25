"""Integration tests for the section-diff CLI command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envguard.cli_differ_sections import section_diff_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


SOURCE = """# Database
DB_HOST=localhost
DB_PORT=5432
# App
DEBUG=true
"""

TARGET_MODIFIED = """# Database
DB_HOST=prod.example.com
DB_PORT=5432
# App
DEBUG=false
"""

TARGET_EXTRA_SECTION = """# Database
DB_HOST=localhost
DB_PORT=5432
# App
DEBUG=true
# Extras
FEATURE_FLAG=on
"""


def test_identical_files_exits_zero(runner, tmp_path):
    src = write_env(tmp_path, "a.env", SOURCE)
    result = runner.invoke(section_diff_cmd, [src, src])
    assert result.exit_code == 0
    assert "No section differences" in result.output


def test_modified_value_shown_in_text(runner, tmp_path):
    src = write_env(tmp_path, "source.env", SOURCE)
    tgt = write_env(tmp_path, "target.env", TARGET_MODIFIED)
    result = runner.invoke(section_diff_cmd, [src, tgt])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "->" in result.output


def test_strict_exits_nonzero_on_diff(runner, tmp_path):
    src = write_env(tmp_path, "source.env", SOURCE)
    tgt = write_env(tmp_path, "target.env", TARGET_MODIFIED)
    result = runner.invoke(section_diff_cmd, ["--strict", src, tgt])
    assert result.exit_code == 1


def test_strict_exits_zero_when_identical(runner, tmp_path):
    src = write_env(tmp_path, "source.env", SOURCE)
    result = runner.invoke(section_diff_cmd, ["--strict", src, src])
    assert result.exit_code == 0


def test_json_output_structure(runner, tmp_path):
    src = write_env(tmp_path, "source.env", SOURCE)
    tgt = write_env(tmp_path, "target.env", TARGET_MODIFIED)
    result = runner.invoke(section_diff_cmd, ["--format", "json", src, tgt])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "has_differences" in data
    assert "diffs" in data
    assert data["has_differences"] is True


def test_section_only_in_target_shown(runner, tmp_path):
    src = write_env(tmp_path, "source.env", SOURCE)
    tgt = write_env(tmp_path, "target.env", TARGET_EXTRA_SECTION)
    result = runner.invoke(section_diff_cmd, [src, tgt])
    assert "# Extras" in result.output
    assert "only in target" in result.output


def test_json_sections_only_in_target(runner, tmp_path):
    src = write_env(tmp_path, "source.env", SOURCE)
    tgt = write_env(tmp_path, "target.env", TARGET_EXTRA_SECTION)
    result = runner.invoke(section_diff_cmd, ["--format", "json", src, tgt])
    data = json.loads(result.output)
    assert "# Extras" in data["sections_only_in_target"]
