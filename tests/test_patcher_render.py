"""Edge-case tests focused on render_patched output format."""
from envguard.patcher import patch_env, render_patched


def test_render_ends_with_newline():
    result = patch_env({"A": "1"}, {})
    assert render_patched(result).endswith("\n")


def test_render_empty_env_is_empty_string():
    result = patch_env({}, {})
    assert render_patched(result) == ""


def test_render_preserves_all_keys():
    env = {"X": "a", "Y": "b", "Z": "c"}
    result = patch_env(env, {"Y": "patched"})
    text = render_patched(result)
    assert "X=a" in text
    assert "Y=patched" in text
    assert "Z=c" in text


def test_render_value_with_equals_sign():
    env = {"URL": "http://x.com"}
    result = patch_env(env, {"URL": "http://y.com?a=1"})
    text = render_patched(result)
    assert "URL=http://y.com?a=1" in text


def test_render_empty_value():
    env = {"EMPTY": "something"}
    result = patch_env(env, {"EMPTY": ""})
    text = render_patched(result)
    assert "EMPTY=" in text
