"""Check which keys from a schema are missing or present in an env file."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envguard.schema import load_schema, required_keys, optional_keys


@dataclass
class RequireResult:
    missing_required: List[str] = field(default_factory=list)
    present_optional: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)

    def has_missing_required(self) -> bool:
        return bool(self.missing_required)

    def summary(self) -> str:
        parts = []
        if self.missing_required:
            parts.append(f"Missing required ({len(self.missing_required)}): {', '.join(self.missing_required)}")
        if self.missing_optional:
            parts.append(f"Missing optional ({len(self.missing_optional)}): {', '.join(self.missing_optional)}")
        if not parts:
            return "All required keys present."
        return " | ".join(parts)


def check_requirements(env: Dict[str, str], schema_path: str) -> RequireResult:
    schema = load_schema(schema_path)
    req = required_keys(schema)
    opt = optional_keys(schema)

    missing_required = [k for k in req if k not in env]
    present_optional = [k for k in opt if k in env]
    missing_optional = [k for k in opt if k not in env]

    return RequireResult(
        missing_required=missing_required,
        present_optional=present_optional,
        missing_optional=missing_optional,
    )
