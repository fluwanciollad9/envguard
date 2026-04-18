"""Integration tests for the `require` CLI command."""
import json
from pathlib import Path
from click.testing import CliRunner
from envguard.cli_require import require_cmd


def write_env(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def write_schema(tmp_path, schema: dict):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return str(p)


def test_all_present_exits_zero(tmp_path):
    env = write_env(tmp_path, ".env", "DB_URL=x\nSECRET_KEY=y\n")
    schema = write_schema(tmp_path, {"required": ["DB_URL", "SECRET_KEY"], "optional": []})
    result = CliRunner().invoke(require_cmd, [env, "--schema", schema])
    assert result.exit_code == 0


def test_missing_required_exits_one(tmp_path):
    env = write_env(tmp_path, ".env", "DB_URL=x\n")
    schema = write_schema(tmp_path, {"required": ["DB_URL", "SECRET_KEY"], "optional": []})
    result = CliRunner().invoke(require_cmd, [env, "--schema", schema])
    assert result.exit_code == 1
    assert "SECRET_KEY" in result.output


def test_json_output_structure(tmp_path):
    env = write_env(tmp_path, ".env", "DB_URL=x\n")
    schema = write_schema(tmp_path, {"required": ["DB_URL", "SECRET_KEY"], "optional": ["DEBUG"]})
    result = CliRunner().invoke(require_cmd, [env, "--schema", schema, "--format", "json"])
    data = json.loads(result.output)
    assert "missing_required" in data
    assert "SECRET_KEY" in data["missing_required"]
    assert "DEBUG" in data["missing_optional"]


def test_strict_exits_one_on_missing_optional(tmp_path):
    env = write_env(tmp_path, ".env", "DB_URL=x\nSECRET_KEY=y\n")
    schema = write_schema(tmp_path, {"required": ["DB_URL", "SECRET_KEY"], "optional": ["DEBUG"]})
    result = CliRunner().invoke(require_cmd, [env, "--schema", schema, "--strict"])
    assert result.exit_code == 1


def test_strict_exits_zero_when_all_present(tmp_path):
    env = write_env(tmp_path, ".env", "DB_URL=x\nSECRET_KEY=y\nDEBUG=true\n")
    schema = write_schema(tmp_path, {"required": ["DB_URL", "SECRET_KEY"], "optional": ["DEBUG"]})
    result = CliRunner().invoke(require_cmd, [env, "--schema", schema, "--strict"])
    assert result.exit_code == 0
