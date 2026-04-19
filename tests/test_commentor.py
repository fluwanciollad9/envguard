import pytest
from envguard.commentor import add_comments, remove_comments, list_comments, was_changed


def lines(*args):
    return list(args)


ENV = lines(
    "HOST=localhost",
    "PORT=5432  # database port",
    "SECRET=abc123",
    "",
    "# full line comment",
    "DEBUG=true",
)


def test_add_comment_to_key_without_comment():
    result = add_comments(ENV, {"HOST": "hostname"})
    assert any("HOST=localhost  # hostname" in l for l in result.lines)
    assert "HOST" in result.added


def test_replace_existing_comment():
    result = add_comments(ENV, {"PORT": "pg port"})
    matching = [l for l in result.lines if l.startswith("PORT=")]
    assert len(matching) == 1
    assert matching[0].endswith("# pg port")
    assert "PORT" in result.added


def test_add_comment_preserves_other_lines():
    result = add_comments(ENV, {"DEBUG": "toggle"})
    assert "SECRET=abc123" in result.lines
    assert "" in result.lines
    assert "# full line comment" in result.lines


def test_was_changed_true_on_add():
    result = add_comments(ENV, {"HOST": "note"})
    assert was_changed(result)


def test_was_changed_false_when_no_keys_match():
    result = add_comments(ENV, {"NONEXISTENT": "note"})
    assert not was_changed(result)


def test_remove_comment_from_specific_key():
    result = remove_comments(ENV, keys=["PORT"])
    matching = [l for l in result.lines if l.startswith("PORT=")]
    assert matching[0] == "PORT=5432"
    assert "PORT" in result.removed


def test_remove_comments_all_keys():
    result = remove_comments(ENV)
    for line in result.lines:
        assert " #" not in line or line.startswith("#")


def test_remove_comment_key_without_comment_unchanged():
    result = remove_comments(ENV, keys=["HOST"])
    assert "HOST" not in result.removed
    assert "HOST=localhost" in result.lines


def test_list_comments_returns_only_keys_with_comments():
    comments = list_comments(ENV)
    assert "PORT" in comments
    assert comments["PORT"] == "# database port"
    assert "HOST" not in comments
    assert "SECRET" not in comments


def test_list_comments_empty_env():
    comments = list_comments([])
    assert comments == {}


def test_add_comments_result_contains_comment_map():
    result = add_comments(ENV, {"HOST": "my host"})
    assert result.comments.get("HOST") == "my host"
    assert result.comments.get("PORT") == "# database port"
