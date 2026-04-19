import pytest
from envguard.tagger import tag_env, filter_by_tag


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "API_KEY": "secret",
    "DEBUG": "true",
}

TAG_MAP = {
    "database": ["DB_HOST", "DB_PORT"],
    "secret": ["API_KEY"],
    "feature": ["DEBUG", "API_KEY"],
}


def test_tagged_count():
    result = tag_env(ENV, TAG_MAP)
    assert result.tagged_count == 4


def test_untagged_keys_empty_when_all_tagged():
    result = tag_env(ENV, TAG_MAP)
    assert result.untagged_keys == []


def test_untagged_key_detected():
    env = {**ENV, "ORPHAN": "value"}
    result = tag_env(env, TAG_MAP)
    assert "ORPHAN" in result.untagged_keys


def test_tags_for_key_single():
    result = tag_env(ENV, TAG_MAP)
    assert result.tags_for_key("DB_HOST") == {"database"}


def test_tags_for_key_multiple():
    result = tag_env(ENV, TAG_MAP)
    assert result.tags_for_key("API_KEY") == {"secret", "feature"}


def test_keys_for_tag_database():
    result = tag_env(ENV, TAG_MAP)
    assert set(result.keys_for_tag("database")) == {"DB_HOST", "DB_PORT"}


def test_keys_for_unknown_tag_empty():
    result = tag_env(ENV, TAG_MAP)
    assert result.keys_for_tag("nonexistent") == []


def test_filter_by_tag_returns_subset():
    result = tag_env(ENV, TAG_MAP)
    subset = filter_by_tag(ENV, result, "database")
    assert subset == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_filter_by_tag_empty_for_unknown():
    result = tag_env(ENV, TAG_MAP)
    subset = filter_by_tag(ENV, result, "missing")
    assert subset == {}


def test_tag_key_not_in_env_is_skipped():
    result = tag_env(ENV, {"ghost": ["GHOST_KEY"]})
    assert "GHOST_KEY" not in result.tags


def test_summary_contains_tagged_count():
    result = tag_env(ENV, TAG_MAP)
    assert "Tagged keys: 4" in result.summary()
