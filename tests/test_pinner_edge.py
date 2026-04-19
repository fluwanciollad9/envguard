"""Edge-case tests for envguard.pinner."""
from envguard.pinner import check_drift, pin_env, PinResult


def test_empty_env_no_drift():
    result = check_drift({}, {})
    assert not result.has_drift()


def test_all_keys_removed():
    lock = {"A": "1", "B": "2"}
    result = check_drift({}, lock)
    assert set(result.removed_keys) == {"A", "B"}
    assert result.has_drift()


def test_all_keys_new():
    result = check_drift({"X": "1", "Y": "2"}, {})
    assert set(result.new_keys) == {"X", "Y"}
    assert result.has_drift()


def test_pin_env_empty():
    assert pin_env({}) == {}


def test_summary_only_new():
    result = check_drift({"Z": "val"}, {})
    assert "new" in result.summary()
    assert "drifted" not in result.summary()
    assert "removed" not in result.summary()


def test_summary_only_removed():
    result = check_drift({}, {"Z": "val"})
    assert "removed" in result.summary()


def test_multiple_drift_types():
    lock = {"A": "old", "B": "same", "C": "gone"}
    env = {"A": "new", "B": "same", "D": "added"}
    result = check_drift(env, lock)
    assert "A" in result.drifted
    assert "B" not in result.drifted
    assert "D" in result.new_keys
    assert "C" in result.removed_keys
