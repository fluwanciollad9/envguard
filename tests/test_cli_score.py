import json
import pytest
from click.testing import CliRunner
from envguard.cli_score import score_cmd


def write_env(tmp_path, content: str):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


@pytest.fixture
def runner():
    return CliRunner()


def test_clean_env_exits_zero(runner, tmp_path):
    path = write_env(tmp_path, "DATABASE_URL=postgres://localhost/db\nPORT=8080\n")
    result = runner.invoke(score_cmd, [path])
    assert result.exit_code == 0
    assert "Score:" in result.output


def test_json_output_structure(runner, tmp_path):
    path = write_env(tmp_path, "KEY=value\n")
    result = runner.invoke(score_cmd, [path, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "score" in data
    assert "grade" in data
    assert "breakdown" in data
    assert "penalties" in data


def test_min_score_exits_nonzero_when_below(runner, tmp_path):
    path = write_env(tmp_path, "KEY=\n")
    result = runner.invoke(score_cmd, [path, "--min-score", "99"])
    assert result.exit_code == 1


def test_min_score_exits_zero_when_above(runner, tmp_path):
    path = write_env(tmp_path, "KEY=solidvalue\n")
    result = runner.invoke(score_cmd, [path, "--min-score", "50"])
    assert result.exit_code == 0


def test_strict_flag_accepted(runner, tmp_path):
    path = write_env(tmp_path, "mykey=value\n")
    result = runner.invoke(score_cmd, [path, "--strict"])
    assert result.exit_code == 0
    assert "Score:" in result.output


def test_grade_shown_in_text_output(runner, tmp_path):
    path = write_env(tmp_path, "GOOD=value\n")
    result = runner.invoke(score_cmd, [path])
    assert "Grade:" in result.output
