import pytest
from envguard.patcher import patch_env, render_patched


ENV = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_patch_single_key():
    result = patch_env(ENV, {"PORT": "9999"})
    assert result.patched["PORT"] == "9999"
    assert result.was_changed()


def test_original_unchanged():
    result = patch_env(ENV, {"PORT": "9999"})
    assert result.original["PORT"] == "5432"


def test_unpatched_keys_preserved():
    result = patch_env(ENV, {"PORT": "9999"})
    assert result.patched["HOST"] == "localhost"
    assert result.patched["DEBUG"] == "true"


def test_multiple_patches():
    result = patch_env(ENV, {"HOST": "db.prod", "DEBUG": "false"})
    assert len(result.applied) == 2
    assert result.patched["HOST"] == "db.prod"
    assert result.patched["DEBUG"] == "false"


def test_not_found_recorded():
    result = patch_env(ENV, {"MISSING_KEY": "value"})
    assert "MISSING_KEY" in result.not_found
    assert "MISSING_KEY" not in result.patched


def test_not_found_does_not_count_as_changed():
    result = patch_env(ENV, {"MISSING_KEY": "value"})
    assert not result.was_changed()


def test_applied_tuple_contains_old_and_new():
    result = patch_env(ENV, {"PORT": "8080"})
    assert result.applied[0] == ("PORT", "5432", "8080")


def test_summary_with_not_found():
    result = patch_env(ENV, {"PORT": "1", "GHOST": "x"})
    s = result.summary()
    assert "1 patch" in s
    assert "not found" in s


def test_render_patched_produces_env_text():
    result = patch_env({"A": "1", "B": "2"}, {"A": "99"})
    text = render_patched(result)
    assert "A=99" in text
    assert "B=2" in text


def test_empty_patches_no_change():
    result = patch_env(ENV, {})
    assert not result.was_changed()
    assert result.patched == ENV
