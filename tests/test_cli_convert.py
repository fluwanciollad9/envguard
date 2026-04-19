"""Integration tests for the convert CLI command."""
import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from envguard.cli_convert import convert_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_convert_to_json_stdout(runner, tmp_path):
    env_file = write_env(tmp_path, "APP=myapp\nDEBUG=true\n")
    result = runner.invoke(convert_cmd, [env_file, "--to", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["APP"] == "myapp"


def test_convert_to_shell_stdout(runner, tmp_path):
    env_file = write_env(tmp_path, "HOST=localhost\n")
    result = runner.invoke(convert_cmd, [env_file, "--to", "shell"])
    assert result.exit_code == 0
    assert "export HOST=" in result.output


def test_convert_to_dotenv_stdout(runner, tmp_path):
    env_file = write_env(tmp_path, "KEY=value\n")
    result = runner.invoke(convert_cmd, [env_file, "--to", "dotenv"])
    assert result.exit_code == 0
    assert "KEY=" in result.output


def test_convert_writes_to_output_file(runner, tmp_path):
    env_file = write_env(tmp_path, "A=1\nB=2\n")
    out_file = str(tmp_path / "out.json")
    result = runner.invoke(convert_cmd, [env_file, "--to", "json", "-o", out_file])
    assert result.exit_code == 0
    assert Path(out_file).exists()
    parsed = json.loads(Path(out_file).read_text())
    assert parsed["A"] == "1"


def test_convert_json_format_flag(runner, tmp_path):
    env_file = write_env(tmp_path, "X=42\n")
    result = runner.invoke(
        convert_cmd, [env_file, "--to", "yaml", "--format", "json"]
    )
    assert result.exit_code == 0
    meta = json.loads(result.output)
    assert meta["target_format"] == "yaml"
    assert "output" in meta


def test_convert_yaml_stdout(runner, tmp_path):
    env_file = write_env(tmp_path, "PORT=8080\n")
    result = runner.invoke(convert_cmd, [env_file, "--to", "yaml"])
    assert result.exit_code == 0
    assert "PORT:" in result.output
