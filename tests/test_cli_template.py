"""Integration tests for the `envguard template` CLI command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envguard.cli_template import template_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def schema_file(tmp_path: Path) -> Path:
    schema = {
        "required": ["APP_SECRET", "DATABASE_URL"],
        "optional": ["DEBUG"],
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return p


def test_dotenv_output_contains_keys(runner: CliRunner, schema_file: Path) -> None:
    result = runner.invoke(template_cmd, [str(schema_file)])
    assert result.exit_code == 0
    assert "APP_SECRET=" in result.output
    assert "DATABASE_URL=" in result.output


def test_json_format_is_valid_json(runner: CliRunner, schema_file: Path) -> None:
    result = runner.invoke(template_cmd, [str(schema_file), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "APP_SECRET" in data
    assert "DATABASE_URL" in data


def test_output_written_to_file(runner: CliRunner, schema_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "generated.env"
    result = runner.invoke(template_cmd, [str(schema_file), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "APP_SECRET=" in content


def test_summary_flag_prints_to_stderr(runner: CliRunner, schema_file: Path) -> None:
    result = runner.invoke(template_cmd, [str(schema_file), "--summary"])
    assert result.exit_code == 0
    # CliRunner mixes stderr into output by default unless mix_stderr=False
    assert "Required" in result.output or "required" in result.output.lower()


def test_missing_schema_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(template_cmd, [str(tmp_path / "nonexistent.json")])
    assert result.exit_code != 0
