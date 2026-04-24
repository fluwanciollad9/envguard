"""Tests for envguard.referencer and envguard.cli_reference."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envguard.referencer import find_references, _extract_refs
from envguard.cli_reference import reference_cmd


# ---------------------------------------------------------------------------
# Unit tests for find_references
# ---------------------------------------------------------------------------

def test_no_references_in_plain_env():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = find_references(env)
    assert result.references == {}
    assert result.undefined == set()
    assert result.unreferenced == {"HOST", "PORT"}


def test_brace_reference_detected():
    env = {"BASE": "http://localhost", "URL": "${BASE}/api"}
    result = find_references(env)
    assert result.references == {"URL": ["BASE"]}
    assert "BASE" not in result.undefined


def test_bare_reference_detected():
    env = {"HOST": "localhost", "DSN": "postgres://$HOST/db"}
    result = find_references(env)
    assert "DSN" in result.references
    assert "HOST" in result.references["DSN"]


def test_undefined_reference_flagged():
    env = {"URL": "${MISSING_VAR}/path"}
    result = find_references(env)
    assert "MISSING_VAR" in result.undefined


def test_unreferenced_key_detected():
    env = {"A": "hello", "B": "${A}"}
    result = find_references(env)
    assert "A" in result.unreferenced or "A" not in result.undefined
    # A is defined and referenced by B, so it should NOT be in unreferenced
    assert "A" not in result.unreferenced
    assert "B" in result.unreferenced


def test_has_undefined_true():
    env = {"X": "$GHOST"}
    result = find_references(env)
    assert result.has_undefined() is True


def test_has_undefined_false():
    env = {"A": "val", "B": "${A}"}
    result = find_references(env)
    assert result.has_undefined() is False


def test_summary_contains_counts():
    env = {"A": "x", "B": "${A} ${MISSING}"}
    result = find_references(env)
    s = result.summary()
    assert "reference" in s
    assert "undefined" in s


def test_extract_refs_deduplicates():
    refs = _extract_refs("${A} ${A} $A")
    assert refs.count("A") == 1


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_cli_no_references_exits_zero(tmp_path):
    f = write_env(tmp_path, "HOST=localhost\nPORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(reference_cmd, [str(f)])
    assert result.exit_code == 0
    assert "No variable references found" in result.output


def test_cli_shows_reference(tmp_path):
    f = write_env(tmp_path, "BASE=http://localhost\nURL=${BASE}/api\n")
    runner = CliRunner()
    result = runner.invoke(reference_cmd, [str(f)])
    assert result.exit_code == 0
    assert "URL" in result.output
    assert "BASE" in result.output


def test_cli_strict_exits_nonzero_on_undefined(tmp_path):
    f = write_env(tmp_path, "URL=${GHOST}/api\n")
    runner = CliRunner()
    result = runner.invoke(reference_cmd, [str(f), "--strict"])
    assert result.exit_code == 1


def test_cli_json_output_structure(tmp_path):
    f = write_env(tmp_path, "BASE=x\nURL=${BASE}/path\n")
    runner = CliRunner()
    result = runner.invoke(reference_cmd, [str(f), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "references" in data
    assert "undefined" in data
    assert "unreferenced" in data
    assert "summary" in data
