"""Tests for envguard parser and differ."""
import textwrap
import pytest
from pathlib import Path
from envguard.parser import parse_env_file
from envguard.differ import diff_envs


@pytest.fixture
def write_env(tmp_path):
    def _write(filename: str, content: str) -> str:
        p = tmp_path / filename
        p.write_text(textwrap.dedent(content))
        return str(p)
    return _write


class TestParseEnvFile:
    def test_basic_key_value(self, write_env):
        path = write_env('basic.env', """
            KEY=value
            PORT=8080
        """)
        result = parse_env_file(path)
        assert result == {'KEY': 'value', 'PORT': '8080'}

    def test_ignores_comments_and_blanks(self, write_env):
        path = write_env('comments.env', """
            # this is a comment
            KEY=hello

            # another comment
            OTHER=world
        """)
        result = parse_env_file(path)
        assert result == {'KEY': 'hello', 'OTHER': 'world'}

    def test_quoted_values(self, write_env):
        path = write_env('quoted.env', """
            SINGLE='hello world'
            DOUBLE="foo bar"
        """)
        result = parse_env_file(path)
        assert result['SINGLE'] == 'hello world'
        assert result['DOUBLE'] == 'foo bar'

    def test_inline_comment_stripped(self, write_env):
        path = write_env('inline.env', "KEY=value # comment\n")
        result = parse_env_file(path)
        assert result['KEY'] == 'value'


class TestDiffEnvs:
    def test_no_differences(self):
        base = {'A': '1', 'B': '2'}
        result = diff_envs(base, base.copy())
        assert not result.has_differences

    def test_missing_keys(self):
        base = {'A': '1', 'B': '2'}
        target = {'A': '1'}
        result = diff_envs(base, target)
        assert result.missing_keys == ['B']
        assert result.extra_keys == []

    def test_extra_keys(self):
        base = {'A': '1'}
        target = {'A': '1', 'C': '3'}
        result = diff_envs(base, target)
        assert result.extra_keys == ['C']
        assert result.missing_keys == []

    def test_changed_values(self):
        base = {'A': 'old'}
        target = {'A': 'new'}
        result = diff_envs(base, target)
        assert 'A' in result.changed_keys
        assert result.changed_keys['A'] == ('old', 'new')
