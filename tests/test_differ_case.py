"""Tests for envguard.differ_case."""
import pytest
from envguard.differ_case import CaseDiffEntry, CaseDiffResult, diff_case


def test_no_differences_when_keys_identical():
    src = {"APP_HOST": "localhost", "APP_PORT": "8080"}
    tgt = {"APP_HOST": "localhost", "APP_PORT": "8080"}
    result = diff_case(src, tgt)
    assert not result.has_differences()
    assert result.case_conflicts == []
    assert result.only_in_source == []
    assert result.only_in_target == []


def test_case_conflict_detected():
    src = {"app_host": "localhost"}
    tgt = {"APP_HOST": "localhost"}
    result = diff_case(src, tgt)
    assert result.has_differences()
    assert len(result.case_conflicts) == 1
    entry = result.case_conflicts[0]
    assert entry.source_key == "app_host"
    assert entry.target_key == "APP_HOST"


def test_only_in_source_populated():
    src = {"DB_URL": "postgres://", "SECRET": "abc"}
    tgt = {"DB_URL": "postgres://"}
    result = diff_case(src, tgt)
    assert result.only_in_source == ["SECRET"]
    assert result.only_in_target == []


def test_only_in_target_populated():
    src = {"DB_URL": "postgres://"}
    tgt = {"DB_URL": "postgres://", "API_KEY": "xyz"}
    result = diff_case(src, tgt)
    assert result.only_in_target == ["API_KEY"]
    assert result.only_in_source == []


def test_multiple_case_conflicts():
    src = {"debug": "true", "log_level": "info"}
    tgt = {"DEBUG": "true", "LOG_LEVEL": "info"}
    result = diff_case(src, tgt)
    assert len(result.case_conflicts) == 2
    keys = {(e.source_key, e.target_key) for e in result.case_conflicts}
    assert ("debug", "DEBUG") in keys
    assert ("log_level", "LOG_LEVEL") in keys


def test_mixed_case_no_conflict_when_same_casing():
    src = {"MyKey": "val"}
    tgt = {"MyKey": "val"}
    result = diff_case(src, tgt)
    assert not result.has_differences()


def test_summary_no_differences():
    result = CaseDiffResult()
    assert result.summary() == "no case differences"


def test_summary_with_conflicts():
    result = CaseDiffResult(
        case_conflicts=[CaseDiffEntry("foo", "FOO")],
        only_in_source=["BAR"],
    )
    s = result.summary()
    assert "1 case conflict" in s
    assert "1 only in source" in s


def test_entry_str():
    entry = CaseDiffEntry(source_key="my_key", target_key="MY_KEY")
    assert "my_key" in str(entry)
    assert "MY_KEY" in str(entry)


def test_empty_envs_no_differences():
    result = diff_case({}, {})
    assert not result.has_differences()


def test_case_conflict_mixed_casing():
    src = {"Api_Key": "secret"}
    tgt = {"API_KEY": "secret"}
    result = diff_case(src, tgt)
    assert len(result.case_conflicts) == 1
    assert result.case_conflicts[0].source_key == "Api_Key"
    assert result.case_conflicts[0].target_key == "API_KEY"
