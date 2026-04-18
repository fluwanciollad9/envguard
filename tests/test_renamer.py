"""Tests for envguard.renamer."""
import pytest
from envguard.renamer import rename_env, render_renamed, was_changed


BASE_ENV = {"OLD_KEY": "value1", "KEEP": "value2", "ANOTHER_OLD": "value3"}


def test_rename_single_key():
    result = rename_env(BASE_ENV, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in result.renamed
    assert "OLD_KEY" not in result.renamed
    assert result.renamed["NEW_KEY"] == "value1"


def test_untouched_keys_preserved():
    result = rename_env(BASE_ENV, {"OLD_KEY": "NEW_KEY"})
    assert result.renamed["KEEP"] == "value2"
    assert result.renamed["ANOTHER_OLD"] == "value3"


def test_multiple_renames():
    result = rename_env(BASE_ENV, {"OLD_KEY": "NEW_KEY", "ANOTHER_OLD": "ANOTHER_NEW"})
    assert "NEW_KEY" in result.renamed
    assert "ANOTHER_NEW" in result.renamed
    assert len(result.changes) == 2


def test_not_found_recorded():
    result = rename_env(BASE_ENV, {"MISSING_KEY": "SOMETHING"})
    assert "MISSING_KEY" in result.not_found
    assert len(result.changes) == 0


def test_was_changed_true():
    result = rename_env(BASE_ENV, {"OLD_KEY": "NEW_KEY"})
    assert was_changed(result) is True


def test_was_changed_false_when_not_found():
    result = rename_env(BASE_ENV, {"MISSING": "NEW"})
    assert was_changed(result) is False


def test_empty_renames():
    result = rename_env(BASE_ENV, {})
    assert result.renamed == BASE_ENV
    assert result.changes == []


def test_render_renamed_output():
    result = rename_env({"OLD": "val"}, {"OLD": "NEW"})
    output = render_renamed(result)
    assert "NEW=val" in output
    assert "OLD=" not in output


def test_changes_tuple_content():
    result = rename_env(BASE_ENV, {"OLD_KEY": "NEW_KEY"})
    assert ("OLD_KEY", "NEW_KEY") in result.changes
