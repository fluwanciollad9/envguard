import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from envguard.cli_comment import comment_cmd


def write_env(tmp_path, content):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


@pytest.fixture
def runner():
    return CliRunner()


def test_add_comment_prints_updated_line(runner, tmp_path):
    f = write_env(tmp_path, "HOST=localhost\nPORT=5432\n")
    result = runner.invoke(comment_cmd, ["add", f, "--key", "HOST=my host"])
    assert result.exit_code == 0
    assert "HOST=localhost  # my host" in result.output


def test_add_comment_in_place_writes_file(runner, tmp_path):
    f = write_env(tmp_path, "HOST=localhost\n")
    runner.invoke(comment_cmd, ["add", f, "--key", "HOST=written", "--in-place"])
    content = Path(f).read_text()
    assert "# written" in content


def test_add_comment_json_output(runner, tmp_path):
    f = write_env(tmp_path, "HOST=localhost\n")
    result = runner.invoke(comment_cmd, ["add", f, "--key", "HOST=note", "--format", "json"])
    data = json.loads(result.output.strip())
    assert "HOST" in data["added"]
    assert data["comments"]["HOST"] == "note"


def test_add_no_keys_exits_nonzero(runner, tmp_path):
    f = write_env(tmp_path, "HOST=localhost\n")
    result = runner.invoke(comment_cmd, ["add", f])
    assert result.exit_code != 0


def test_remove_comment_prints_clean_line(runner, tmp_path):
    f = write_env(tmp_path, "PORT=5432  # db port\n")
    result = runner.invoke(comment_cmd, ["remove", f, "--key", "PORT"])
    assert result.exit_code == 0
    assert "PORT=5432" in result.output
    assert "# db port" not in result.output


def test_remove_comment_in_place(runner, tmp_path):
    f = write_env(tmp_path, "PORT=5432  # db port\n")
    runner.invoke(comment_cmd, ["remove", f, "--in-place"])
    assert "# db port" not in Path(f).read_text()


def test_list_comments_text(runner, tmp_path):
    f = write_env(tmp_path, "PORT=5432  # db port\nHOST=localhost\n")
    result = runner.invoke(comment_cmd, ["list", f])
    assert "PORT" in result.output
    assert "db port" in result.output


def test_list_comments_json(runner, tmp_path):
    f = write_env(tmp_path, "PORT=5432  # db port\n")
    result = runner.invoke(comment_cmd, ["list", f, "--format", "json"])
    data = json.loads(result.output.strip())
    assert "PORT" in data


def test_list_no_comments_message(runner, tmp_path):
    f = write_env(tmp_path, "HOST=localhost\n")
    result = runner.invoke(comment_cmd, ["list", f])
    assert "No inline comments" in result.output
