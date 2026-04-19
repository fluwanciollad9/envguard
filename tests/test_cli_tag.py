import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from envguard.cli_tag import tag_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write_env(tmp_path, content):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def write_tag_map(tmp_path, data):
    p = tmp_path / "tags.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_show_text_output(tmp_path, runner):
    env_file = write_env(tmp_path, "DB_HOST=localhost\nAPI_KEY=secret\n")
    tag_file = write_tag_map(tmp_path, {"database": ["DB_HOST"], "secret": ["API_KEY"]})
    result = runner.invoke(tag_cmd, ["show", env_file, tag_file])
    assert result.exit_code == 0
    assert "DB_HOST: database" in result.output
    assert "API_KEY: secret" in result.output


def test_show_json_output(tmp_path, runner):
    env_file = write_env(tmp_path, "DB_HOST=localhost\n")
    tag_file = write_tag_map(tmp_path, {"database": ["DB_HOST"]})
    result = runner.invoke(tag_cmd, ["show", "--format", "json", env_file, tag_file])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["DB_HOST"] == ["database"]


def test_show_untagged_label(tmp_path, runner):
    env_file = write_env(tmp_path, "ORPHAN=value\n")
    tag_file = write_tag_map(tmp_path, {})
    result = runner.invoke(tag_cmd, ["show", env_file, tag_file])
    assert "(untagged)" in result.output


def test_filter_returns_matching_keys(tmp_path, runner):
    env_file = write_env(tmp_path, "DB_HOST=localhost\nDEBUG=true\n")
    tag_file = write_tag_map(tmp_path, {"database": ["DB_HOST"]})
    result = runner.invoke(tag_cmd, ["filter", env_file, tag_file, "database"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DEBUG" not in result.output


def test_filter_json_output(tmp_path, runner):
    env_file = write_env(tmp_path, "DB_HOST=localhost\n")
    tag_file = write_tag_map(tmp_path, {"database": ["DB_HOST"]})
    result = runner.invoke(tag_cmd, ["filter", "--format", "json", env_file, tag_file, "database"])
    data = json.loads(result.output)
    assert data == {"DB_HOST": "localhost"}


def test_filter_unknown_tag_exits_one(tmp_path, runner):
    env_file = write_env(tmp_path, "DB_HOST=localhost\n")
    tag_file = write_tag_map(tmp_path, {"database": ["DB_HOST"]})
    result = runner.invoke(tag_cmd, ["filter", env_file, tag_file, "ghost"])
    assert result.exit_code == 1


def test_missing_tag_map_exits_one(tmp_path, runner):
    env_file = write_env(tmp_path, "DB_HOST=localhost\n")
    result = runner.invoke(tag_cmd, ["show", env_file, str(tmp_path / "nope.json")])
    assert result.exit_code == 1
