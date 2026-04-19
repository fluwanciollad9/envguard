"""Coerce env values to typed Python objects based on a type hint map."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

SUPPORTED_TYPES = {"str", "int", "float", "bool"}

BOOL_TRUE = {"true", "1", "yes", "on"}
BOOL_FALSE = {"false", "0", "no", "off"}


@dataclass
class CoerceError:
    key: str
    raw: str
    target_type: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: cannot coerce {self.raw!r} to {self.target_type} — {self.reason}"


@dataclass
class CoerceResult:
    coerced: Dict[str, Any] = field(default_factory=dict)
    errors: List[CoerceError] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def summary(self) -> str:
        parts = [f"{len(self.coerced)} coerced"]
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts)


def _coerce_value(key: str, raw: str, target: str) -> Tuple[Any, CoerceError | None]:
    if target == "str":
        return raw, None
    if target == "int":
        try:
            return int(raw), None
        except ValueError:
            return None, CoerceError(key, raw, target, "not a valid integer")
    if target == "float":
        try:
            return float(raw), None
        except ValueError:
            return None, CoerceError(key, raw, target, "not a valid float")
    if target == "bool":
        low = raw.lower()
        if low in BOOL_TRUE:
            return True, None
        if low in BOOL_FALSE:
            return False, None
        return None, CoerceError(key, raw, target, "not a recognised boolean")
    return None, CoerceError(key, raw, target, f"unsupported type '{target}'")


def coerce_env(env: Dict[str, str], type_map: Dict[str, str]) -> CoerceResult:
    """Coerce *env* values according to *type_map* {key: type_name}."""
    result = CoerceResult()
    for key, raw in env.items():
        target = type_map.get(key)
        if target is None:
            result.skipped.append(key)
            result.coerced[key] = raw
            continue
        value, err = _coerce_value(key, raw, target)
        if err:
            result.errors.append(err)
        else:
            result.coerced[key] = value
    return result
