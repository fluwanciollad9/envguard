"""Tests for envguard.templater."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envguard.templater import generate_template, render_template


@pytest.fixture()
def json_schema(tmp_path: Path) -> Path:
    schema = {
        "required": ["DATABASE_URL", "SECRET_KEY", "PORT"],
        "optional": ["DEBUG", "LOG_LEVEL"],
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return p


def test_required_keys_in_rendered(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    for key in ["DATABASE_URL", "SECRET_KEY", "PORT"]:
        assert key in result.rendered


def test_optional_keys_in_rendered(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    for key in ["DEBUG", "LOG_LEVEL"]:
        assert key in result.rendered


def test_secret_key_gets_secret_placeholder(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    assert "secret" in result.rendered["SECRET_KEY"].lower()


def test_url_key_gets_url_placeholder(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    assert result.rendered["DATABASE_URL"].startswith("https://")


def test_port_key_gets_numeric_placeholder(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    assert result.rendered["PORT"].isdigit()


def test_required_list_matches_schema(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    assert set(result.required) == {"DATABASE_URL", "SECRET_KEY", "PORT"}


def test_optional_list_matches_schema(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    assert set(result.optional) == {"DEBUG", "LOG_LEVEL"}


def test_defaults_override_placeholders(json_schema: Path) -> None:
    result = generate_template(str(json_schema), defaults={"PORT": "5432"})
    assert result.rendered["PORT"] == "5432"


def test_render_contains_required_section(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    text = render_template(result)
    assert "# --- Required ---" in text


def test_render_contains_optional_section(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    text = render_template(result)
    assert "# --- Optional ---" in text


def test_render_ends_with_newline(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    text = render_template(result)
    assert text.endswith("\n")


def test_summary_mentions_schema_path(json_schema: Path) -> None:
    result = generate_template(str(json_schema))
    assert str(json_schema) in result.summary()
