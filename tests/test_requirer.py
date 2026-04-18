"""Tests for envguard.requirer."""
import json
import pytest
from pathlib import Path
from envguard.requirer import check_requirements, RequireResult


@pytest.fixture()
def schema_file(tmp_path):
    schema = {
        "required": ["DB_URL", "SECRET_KEY"],
        "optional": ["DEBUG", "LOG_LEVEL"],
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return str(p)


def test_all_required_present(schema_file):
    env = {"DB_URL": "postgres://", "SECRET_KEY": "abc"}
    result = check_requirements(env, schema_file)
    assert not result.has_missing_required()
    assert result.missing_required == []


def test_missing_required_detected(schema_file):
    env = {"DB_URL": "postgres://"}
    result = check_requirements(env, schema_file)
    assert result.has_missing_required()
    assert "SECRET_KEY" in result.missing_required


def test_present_optional_tracked(schema_file):
    env = {"DB_URL": "x", "SECRET_KEY": "y", "DEBUG": "true"}
    result = check_requirements(env, schema_file)
    assert "DEBUG" in result.present_optional


def test_missing_optional_tracked(schema_file):
    env = {"DB_URL": "x", "SECRET_KEY": "y"}
    result = check_requirements(env, schema_file)
    assert "DEBUG" in result.missing_optional
    assert "LOG_LEVEL" in result.missing_optional


def test_summary_all_present(schema_file):
    env = {"DB_URL": "x", "SECRET_KEY": "y"}
    result = check_requirements(env, schema_file)
    assert result.summary() == "All required keys present."


def test_summary_missing_required(schema_file):
    env = {}
    result = check_requirements(env, schema_file)
    summary = result.summary()
    assert "Missing required" in summary
    assert "DB_URL" in summary
