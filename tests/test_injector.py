import pytest
from envguard.injector import inject_env, render_injected, was_changed


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_new_key_is_injected():
    result = inject_env(BASE, {"NEW_KEY": "value"})
    assert "NEW_KEY" in result.env
    assert result.injected == ["NEW_KEY"]
    assert result.overwritten == []


def test_existing_key_overwritten_by_default():
    result = inject_env(BASE, {"PORT": "9999"})
    assert result.env["PORT"] == "9999"
    assert result.overwritten == ["PORT"]
    assert result.injected == []


def test_existing_key_skipped_when_no_overwrite():
    result = inject_env(BASE, {"PORT": "9999"}, allow_overwrite=False)
    assert result.env["PORT"] == "5432"
    assert result.overwritten == []
    assert result.injected == []


def test_new_key_still_injected_when_no_overwrite():
    result = inject_env(BASE, {"BRAND_NEW": "yes"}, allow_overwrite=False)
    assert "BRAND_NEW" in result.env
    assert result.injected == ["BRAND_NEW"]


def test_was_changed_true_on_inject():
    result = inject_env(BASE, {"X": "1"})
    assert was_changed(result)


def test_was_changed_true_on_overwrite():
    result = inject_env(BASE, {"PORT": "1"})
    assert was_changed(result)


def test_was_changed_false_when_nothing_done():
    result = inject_env(BASE, {"PORT": "1"}, allow_overwrite=False)
    assert not was_changed(result)


def test_base_env_not_mutated():
    original = dict(BASE)
    inject_env(BASE, {"PORT": "0", "Z": "z"})
    assert BASE == original


def test_render_injected_produces_sorted_dotenv():
    result = inject_env({"B": "2", "A": "1"}, {"C": "3"})
    text = render_injected(result)
    lines = text.strip().splitlines()
    assert lines[0] == "A=1"
    assert lines[1] == "B=2"
    assert lines[2] == "C=3"


def test_empty_overrides_unchanged():
    result = inject_env(BASE, {})
    assert result.env == dict(BASE)
    assert not was_changed(result)
