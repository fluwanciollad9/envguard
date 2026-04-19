from envguard.tagger import tag_env, filter_by_tag


def test_empty_env_no_tags():
    result = tag_env({}, {"db": ["DB_HOST"]})
    assert result.tagged_count == 0
    assert result.untagged_keys == []


def test_empty_tag_map_all_untagged():
    env = {"A": "1", "B": "2"}
    result = tag_env(env, {})
    assert result.tagged_count == 0
    assert set(result.untagged_keys) == {"A", "B"}


def test_same_key_multiple_tags():
    env = {"SECRET": "val"}
    result = tag_env(env, {"sensitive": ["SECRET"], "audit": ["SECRET"]})
    assert result.tags_for_key("SECRET") == {"sensitive", "audit"}
    assert result.tagged_count == 1


def test_filter_all_keys_for_broad_tag():
    env = {"A": "1", "B": "2", "C": "3"}
    tag_map = {"all": ["A", "B", "C"]}
    result = tag_env(env, tag_map)
    subset = filter_by_tag(env, result, "all")
    assert subset == env


def test_summary_mentions_untagged_when_present():
    env = {"A": "1", "B": "2"}
    result = tag_env(env, {"x": ["A"]})
    s = result.summary()
    assert "Untagged keys: 1" in s


def test_summary_no_untagged_line_when_all_tagged():
    env = {"A": "1"}
    result = tag_env(env, {"x": ["A"]})
    assert "Untagged" not in result.summary()
