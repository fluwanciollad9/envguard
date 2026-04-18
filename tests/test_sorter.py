import pytest
from envguard.sorter import sort_env, render_sorted


ENV = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


def test_alphabetical_sort_basic():
    result = sort_env(ENV)
    assert result.order == ["APPLE", "MANGO", "ZEBRA"]


def test_sorted_env_matches_order():
    result = sort_env(ENV)
    assert list(result.sorted_env.keys()) == result.order


def test_was_changed_true_when_unsorted():
    result = sort_env(ENV)
    assert result.was_changed is True


def test_was_changed_false_when_already_sorted():
    already = {"APPLE": "2", "MANGO": "3", "ZEBRA": "1"}
    result = sort_env(already)
    assert result.was_changed is False


def test_group_order_respected():
    groups = [["ZEBRA", "MANGO"], ["APPLE"]]
    result = sort_env(ENV, groups=groups)
    assert result.order == ["ZEBRA", "MANGO", "APPLE"]


def test_group_missing_keys_ignored():
    groups = [["ZEBRA", "MISSING"]]
    result = sort_env(ENV, groups=groups)
    assert "MISSING" not in result.order
    assert "ZEBRA" in result.order


def test_ungrouped_keys_appended_alphabetically():
    groups = [["ZEBRA"]]
    result = sort_env(ENV, groups=groups)
    assert result.order == ["ZEBRA", "APPLE", "MANGO"]


def test_render_sorted_output():
    result = sort_env({"B": "2", "A": "1"})
    text = render_sorted(result)
    assert text == "A=1\nB=2\n"


def test_empty_env():
    result = sort_env({})
    assert result.order == []
    assert result.was_changed is False
