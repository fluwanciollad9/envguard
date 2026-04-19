"""Integration tests for cli_encrypt commands."""
import json
import pytest
from click.testing import CliRunner
from envguard.cli_encrypt import encrypt_cmd


def write_env(tmp_path, content):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


PASS = "testpass"


def test_run_prints_encrypted_output(tmp_path):
    path = write_env(tmp_path, "DB_PASSWORD=secret\nAPP_NAME=myapp\n")
    runner = CliRunner()
    result = runner.invoke(encrypt_cmd, ["run", path, "-p", PASS])
    assert result.exit_code == 0
    assert "enc:" in result.output
    assert "APP_NAME=myapp" in result.output


def test_run_in_place_writes_file(tmp_path):
    path = write_env(tmp_path, "API_KEY=abc123\nPORT=8080\n")
    runner = CliRunner()
    result = runner.invoke(encrypt_cmd, ["run", path, "-p", PASS, "--in-place"])
    assert result.exit_code == 0
    content = open(path).read()
    assert "enc:" in content


def test_run_json_output(tmp_path):
    path = write_env(tmp_path, "AUTH_TOKEN=tok\nHOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(encrypt_cmd, ["run", path, "-p", PASS, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "encrypted" in data
    assert data["count"] == 1


def test_decrypt_restores_values(tmp_path):
    path = write_env(tmp_path, "DB_PASSWORD=secret\nPORT=9000\n")
    runner = CliRunner()
    runner.invoke(encrypt_cmd, ["run", path, "-p", PASS, "--in-place"])
    result = runner.invoke(encrypt_cmd, ["decrypt", path, "-p", PASS])
    assert result.exit_code == 0
    assert "DB_PASSWORD=secret" in result.output


def test_dry_run_does_not_write(tmp_path):
    path = write_env(tmp_path, "API_KEY=xyz\n")
    original = open(path).read()
    runner = CliRunner()
    runner.invoke(encrypt_cmd, ["run", path, "-p", PASS, "--in-place", "--dry-run"])
    assert open(path).read() == original
