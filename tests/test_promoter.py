import pytest
from envguard.promoter import promote_env, render_promoted


SOURCE = {"DB_HOST": "prod-db", "DB_PASS": "s3cr3t", "API_KEY": "abc123"}
TARGET = {"DB_HOST": "staging-db", "APP_ENV": "staging"}


def test_promoted_keys_appear_in_result():
    r = promote_env(SOURCE, TARGET, keys=["API_KEY"])
    assert "API_KEY" in r.promoted
    assert r.promoted["API_KEY"] == "abc123"


def test_existing_key_skipped_without_overwrite():
    r = promote_env(SOURCE, TARGET, keys=["DB_HOST"])
    assert "DB_HOST" in r.skipped
    assert "DB_HOST" not in r.promoted


def test_existing_key_overwritten_when_flag_set():
    r = promote_env(SOURCE, TARGET, keys=["DB_HOST"], overwrite=True)
    assert "DB_HOST" in r.overwritten
    assert r.promoted["DB_HOST"] == "prod-db"


def test_key_missing_from_source_ignored():
    r = promote_env(SOURCE, TARGET, keys=["NONEXISTENT"])
    assert "NONEXISTENT" not in r.promoted
    assert "NONEXISTENT" not in r.skipped


def test_was_changed_true_when_promoted():
    r = promote_env(SOURCE, TARGET, keys=["API_KEY"])
    assert r.was_changed()


def test_was_changed_false_when_all_skipped():
    r = promote_env(SOURCE, TARGET, keys=["DB_HOST"])
    assert not r.was_changed()


def test_summary_mentions_counts():
    r = promote_env(SOURCE, TARGET, keys=["API_KEY", "DB_HOST"], overwrite=False)
    s = r.summary()
    assert "1" in s
    assert "Skipped" in s


def test_render_promoted_merges_into_target():
    r = promote_env(SOURCE, TARGET, keys=["API_KEY"])
    out = render_promoted(TARGET, r)
    assert "API_KEY=abc123" in out
    assert "APP_ENV=staging" in out


def test_render_promoted_overwrite_replaces_value():
    r = promote_env(SOURCE, TARGET, keys=["DB_HOST"], overwrite=True)
    out = render_promoted(TARGET, r)
    assert "DB_HOST=prod-db" in out
    assert "DB_HOST=staging-db" not in out


def test_labels_stored_on_result():
    r = promote_env(SOURCE, TARGET, keys=[], source_label="prod", target_label="staging")
    assert r.source_env == "prod"
    assert r.target_env == "staging"
