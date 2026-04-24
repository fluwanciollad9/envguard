"""Unit tests for envguard.rotator."""
import pytest
from envguard.rotator import (
    rotate_env,
    render_rotated,
    summary,
    was_changed,
)


BASE_ENV = {"OLD_DB_URL": "postgres://localhost", "APP_SECRET": "s3cr3t", "PORT": "8080"}


def test_single_key_renamed():
    result = rotate_env(BASE_ENV, {"OLD_DB_URL": "DATABASE_URL"})
    assert "DATABASE_URL" in result.rotated
    assert "OLD_DB_URL" not in result.rotated
    assert result.rotated["DATABASE_URL"] == "postgres://localhost"


def test_untouched_keys_preserved():
    result = rotate_env(BASE_ENV, {"OLD_DB_URL": "DATABASE_URL"})
    assert result.rotated["APP_SECRET"] == "s3cr3t"
    assert result.rotated["PORT"] == "8080"


def test_renamed_list_populated():
    result = rotate_env(BASE_ENV, {"OLD_DB_URL": "DATABASE_URL"})
    assert ("OLD_DB_URL", "DATABASE_URL") in result.renamed


def test_not_found_recorded():
    result = rotate_env(BASE_ENV, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.not_found
    assert result.renamed == []


def test_conflict_skipped_by_default():
    env = {"OLD_KEY": "old_val", "NEW_KEY": "existing_val"}
    result = rotate_env(env, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in result.conflicts
    assert result.rotated["NEW_KEY"] == "existing_val"  # original preserved
    assert "OLD_KEY" in result.rotated  # not removed


def test_conflict_overwritten_when_flag_set():
    env = {"OLD_KEY": "old_val", "NEW_KEY": "existing_val"}
    result = rotate_env(env, {"OLD_KEY": "NEW_KEY"}, overwrite_conflicts=True)
    assert result.rotated["NEW_KEY"] == "old_val"
    assert "OLD_KEY" not in result.rotated
    assert result.conflicts == []


def test_multiple_renames():
    result = rotate_env(BASE_ENV, {"OLD_DB_URL": "DATABASE_URL", "PORT": "APP_PORT"})
    assert "DATABASE_URL" in result.rotated
    assert "APP_PORT" in result.rotated
    assert len(result.renamed) == 2


def test_was_changed_true_on_rename():
    result = rotate_env(BASE_ENV, {"OLD_DB_URL": "DATABASE_URL"})
    assert was_changed(result) is True


def test_was_changed_false_when_nothing_renamed():
    result = rotate_env(BASE_ENV, {"MISSING": "NEW"})
    assert was_changed(result) is False


def test_original_env_not_mutated():
    env = {"A": "1", "B": "2"}
    rotate_env(env, {"A": "C"})
    assert "A" in env


def test_summary_shows_renamed_count():
    result = rotate_env(BASE_ENV, {"OLD_DB_URL": "DATABASE_URL"})
    assert "1 key(s) rotated" in summary(result)


def test_summary_shows_not_found():
    result = rotate_env(BASE_ENV, {"MISSING": "NEW"})
    assert "not found" in summary(result)


def test_render_rotated_produces_dotenv_lines():
    result = rotate_env({"KEY": "value"}, {"KEY": "NEW_KEY"})
    rendered = render_rotated(result)
    assert "NEW_KEY=value" in rendered


def test_render_ends_with_newline():
    result = rotate_env({"A": "1"}, {})
    assert render_rotated(result).endswith("\n")
