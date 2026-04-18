"""Tests for envguard.exporter."""
import json
import pytest
from envguard.exporter import export_env, ExportError, SUPPORTED_FORMATS


ENV = {"APP_NAME": "myapp", "DB_PASS": 'sec"ret', "PORT": "8080"}


def test_json_format_is_valid_json():
    output = export_env(ENV, "json")
    parsed = json.loads(output)
    assert parsed["APP_NAME"] == "myapp"
    assert parsed["PORT"] == "8080"


def test_json_preserves_all_keys():
    output = export_env(ENV, "json")
    parsed = json.loads(output)
    assert set(parsed.keys()) == set(ENV.keys())


def test_shell_export_prefix():
    output = export_env({"FOO": "bar"}, "shell")
    assert output == 'export FOO="bar"'


def test_shell_escapes_double_quotes():
    output = export_env({"X": 'say "hi"'}, "shell")
    assert '\\"' in output


def test_dotenv_simple_value_no_quotes():
    output = export_env({"KEY": "value"}, "dotenv")
    assert output == "KEY=value"


def test_dotenv_value_with_space_quoted():
    output = export_env({"MSG": "hello world"}, "dotenv")
    assert output == 'MSG="hello world"'


def test_dotenv_value_with_hash_quoted():
    output = export_env({"V": "foo#bar"}, "dotenv")
    assert '"' in output


def test_unsupported_format_raises():
    with pytest.raises(ExportError, match="Unsupported format"):
        export_env({"A": "1"}, "xml")


def test_empty_env_all_formats():
    for fmt in SUPPORTED_FORMATS:
        result = export_env({}, fmt)
        assert result == "" or result == "{}"
