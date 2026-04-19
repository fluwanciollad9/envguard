import json
import pytest
from click.testing import CliRunner
from envguard.cli_filter import filter_cmd


def write_env(tmp_path, content: str):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


@pytest.fixture
def runner():
    return CliRunner()


ENV_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=envguard\nDEBUG=true\n"


def test_dotenv_output_matched_keys(runner, tmp_path):
    f = write_env(tmp_path, ENV_CONTENT)
    result = runner.invoke(filter_cmd, [f, r"^DB_"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DB_PORT=5432" in result.output
    assert "APP_NAME" not in result.output


def test_text_format_prints_keys_only(runner, tmp_path):
    f = write_env(tmp_path, ENV_CONTENT)
    result = runner.invoke(filter_cmd, [f, r"^DB_", "--format", "text"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "localhost" not in result.output


def test_json_format_structure(runner, tmp_path):
    f = write_env(tmp_path, ENV_CONTENT)
    result = runner.invoke(filter_cmd, [f, r"^DB_", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "matched" in data
    assert "excluded" in data
    assert data["match_count"] == 2


def test_invert_flag_excludes_matched(runner, tmp_path):
    f = write_env(tmp_path, ENV_CONTENT)
    result = runner.invoke(filter_cmd, [f, r"^DB_", "--invert"])
    assert result.exit_code == 0
    assert "APP_NAME=envguard" in result.output
    assert "DB_HOST" not in result.output


def test_invalid_pattern_exits_nonzero(runner, tmp_path):
    f = write_env(tmp_path, ENV_CONTENT)
    result = runner.invoke(filter_cmd, [f, r"[bad"])
    assert result.exit_code != 0
