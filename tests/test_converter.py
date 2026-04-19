"""Tests for envguard.converter."""
import json
import pytest
from envguard.converter import convert_env, ConvertError, SUPPORTED_FORMATS


ENV = {"APP_NAME": "myapp", "DEBUG": "true", "SECRET": 'pass"word'}


def test_dotenv_output_format():
    result = convert_env(ENV, "dotenv")
    assert 'APP_NAME="myapp"' in result.output
    assert result.target_format == "dotenv"


def test_json_output_is_valid_json():
    result = convert_env(ENV, "json")
    parsed = json.loads(result.output)
    assert parsed["APP_NAME"] == "myapp"
    assert parsed["DEBUG"] == "true"


def test_json_preserves_all_keys():
    result = convert_env(ENV, "json")
    parsed = json.loads(result.output)
    assert set(parsed.keys()) == set(ENV.keys())


def test_shell_export_prefix():
    result = convert_env(ENV, "shell")
    assert result.output.startswith("export ")
    for line in result.output.strip().splitlines():
        assert line.startswith("export ")


def test_yaml_output_format():
    result = convert_env({"HOST": "localhost"}, "yaml")
    assert 'HOST: "localhost"' in result.output


def test_dotenv_escapes_double_quotes():
    result = convert_env({"K": 'say "hi"'}, "dotenv")
    assert '\\"' in result.output


def test_shell_escapes_double_quotes():
    result = convert_env({"K": 'say "hi"'}, "shell")
    assert '\\"' in result.output


def test_unsupported_format_raises():
    with pytest.raises(ConvertError, match="Unsupported"):
        convert_env(ENV, "xml")


def test_summary_contains_key_count():
    result = convert_env(ENV, "json")
    assert str(len(ENV)) in result.summary()


def test_summary_mentions_formats():
    result = convert_env(ENV, "shell", source_format="dotenv")
    assert "dotenv" in result.summary()
    assert "shell" in result.summary()


def test_empty_env_produces_empty_output():
    result = convert_env({}, "dotenv")
    assert result.output == ""


def test_all_supported_formats_work():
    for fmt in SUPPORTED_FORMATS:
        result = convert_env({"A": "1"}, fmt)
        assert result.output
