"""stringer.py – render an env dict as various string formats."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Literal

Format = Literal["dotenv", "exports", "json", "yaml", "ini"]


@dataclass
class StringResult:
    fmt: str
    output: str
    key_count: int

    def summary(self) -> str:
        return f"{self.key_count} key(s) rendered as {self.fmt}"


def _escape_value(value: str) -> str:
    """Wrap value in double-quotes if it contains spaces or special chars."""
    needs_quoting = any(c in value for c in (' ', '\t', '"', "'", '#', '$', '\\'))
    if needs_quoting:
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _to_dotenv(env: Dict[str, str]) -> str:
    lines = [f"{k}={_escape_value(v)}" for k, v in env.items()]
    return "\n".join(lines) + ("\n" if lines else "")


def _to_exports(env: Dict[str, str]) -> str:
    lines = [f"export {k}={_escape_value(v)}" for k, v in env.items()]
    return "\n".join(lines) + ("\n" if lines else "")


def _to_json(env: Dict[str, str]) -> str:
    import json
    return json.dumps(env, indent=2) + "\n"


def _to_yaml(env: Dict[str, str]) -> str:
    lines = []
    for k, v in env.items():
        needs_quoting = any(c in v for c in (':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '>', '!', "'", '"'))
        formatted_v = f'"{v}"' if needs_quoting else v
        lines.append(f"{k}: {formatted_v}")
    return "\n".join(lines) + ("\n" if lines else "")


def _to_ini(env: Dict[str, str]) -> str:
    lines = ["[env]"]
    lines += [f"{k} = {v}" for k, v in env.items()]
    return "\n".join(lines) + "\n"


_RENDERERS = {
    "dotenv": _to_dotenv,
    "exports": _to_exports,
    "json": _to_json,
    "yaml": _to_yaml,
    "ini": _to_ini,
}


def stringify_env(env: Dict[str, str], fmt: Format = "dotenv") -> StringResult:
    """Render *env* as a string in the requested *fmt*."""
    if fmt not in _RENDERERS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(_RENDERERS)}.")
    output = _RENDERERS[fmt](env)
    return StringResult(fmt=fmt, output=output, key_count=len(env))
