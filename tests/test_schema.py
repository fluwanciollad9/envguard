"""Tests for envguard.schema."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from envguard.schema import SchemaError, load_schema, optional_keys, required_keys


@pytest.fixture()
def json_schema(tmp_path: Path) -> Path:
    schema = {
        "required": ["DATABASE_URL", "SECRET_KEY"],
        "optional": ["DEBUG", "LOG_LEVEL"],
        "allow_unknown": False,
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return p


def test_load_json_schema(json_schema: Path):
    schema = load_schema(json_schema)
    assert required_keys(schema) == ["DATABASE_URL", "SECRET_KEY"]
    assert "DEBUG" in optional_keys(schema)
    assert schema["allow_unknown"] is False


def test_missing_schema_file(tmp_path: Path):
    with pytest.raises(SchemaError, match="not found"):
        load_schema(tmp_path / "nonexistent.json")


def test_unsupported_schema_format(tmp_path: Path):
    p = tmp_path / "schema.yaml"
    p.write_text("required: []")
    with pytest.raises(SchemaError, match="Unsupported"):
        load_schema(p)


def test_invalid_required_type(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"required": "NOT_A_LIST"}))
    with pytest.raises(SchemaError, match="list of strings"):
        load_schema(p)


def test_defaults_when_keys_absent(tmp_path: Path):
    p = tmp_path / "minimal.json"
    p.write_text(json.dumps({}))
    schema = load_schema(p)
    assert required_keys(schema) == []
    assert optional_keys(schema) == []
    assert schema["allow_unknown"] is True
