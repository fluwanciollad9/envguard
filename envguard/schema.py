"""Load and parse a simple TOML/JSON schema that declares required/optional keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


SCHEMA_KEYS = ("required", "optional", "allow_unknown")


class SchemaError(ValueError):
    pass


def _load_toml(path: Path) -> Dict[str, Any]:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            raise SchemaError(
                "TOML schema support requires Python 3.11+ or 'tomli' package."
            )
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_schema(path: str | Path) -> Dict[str, Any]:
    """Load a JSON or TOML schema file and return a normalised dict."""
    p = Path(path)
    if not p.exists():
        raise SchemaError(f"Schema file not found: {p}")

    if p.suffix == ".json":
        with p.open() as fh:
            raw: Dict[str, Any] = json.load(fh)
    elif p.suffix in (".toml",):
        raw = _load_toml(p)
    else:
        raise SchemaError(f"Unsupported schema format: {p.suffix}")

    schema: Dict[str, Any] = {
        "required": [],
        "optional": [],
        "allow_unknown": True,
    }
    for key in SCHEMA_KEYS:
        if key in raw:
            schema[key] = raw[key]

    required = schema["required"]
    if not isinstance(required, list) or not all(isinstance(k, str) for k in required):
        raise SchemaError("'required' must be a list of strings.")

    return schema


def required_keys(schema: Dict[str, Any]) -> List[str]:
    return schema.get("required", [])


def optional_keys(schema: Dict[str, Any]) -> List[str]:
    return schema.get("optional", [])
