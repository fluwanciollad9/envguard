"""Generate a .env file from a schema template with placeholder values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.schema import load_schema, required_keys, optional_keys


@dataclass
class TemplateResult:
    rendered: Dict[str, str]
    required: List[str]
    optional: List[str]
    schema_path: str

    def summary(self) -> str:
        lines = [
            f"Template generated from: {self.schema_path}",
            f"  Required keys : {len(self.required)}",
            f"  Optional keys : {len(self.optional)}",
            f"  Total         : {len(self.rendered)}",
        ]
        return "\n".join(lines)


def _placeholder_for(key: str, required: bool) -> str:
    """Return a sensible placeholder string for a given key."""
    lower = key.lower()
    if any(tok in lower for tok in ("password", "secret", "token", "key", "pass")):
        return "<your-secret-here>"
    if any(tok in lower for tok in ("url", "host", "endpoint")):
        return "https://example.com"
    if any(tok in lower for tok in ("port",)):
        return "8080"
    if any(tok in lower for tok in ("debug", "enabled", "flag")):
        return "false"
    if required:
        return "<required>"
    return "<optional>"


def generate_template(
    schema_path: str,
    defaults: Optional[Dict[str, str]] = None,
) -> TemplateResult:
    """Build a template env dict from a schema file."""
    schema = load_schema(schema_path)
    req = required_keys(schema)
    opt = optional_keys(schema)
    defaults = defaults or {}

    rendered: Dict[str, str] = {}
    for key in req:
        rendered[key] = defaults.get(key, _placeholder_for(key, required=True))
    for key in opt:
        rendered[key] = defaults.get(key, _placeholder_for(key, required=False))

    return TemplateResult(
        rendered=rendered,
        required=req,
        optional=opt,
        schema_path=schema_path,
    )


def render_template(result: TemplateResult) -> str:
    """Render a TemplateResult to .env file text."""
    lines: List[str] = []
    if result.required:
        lines.append("# --- Required ---")
        for key in result.required:
            lines.append(f"{key}={result.rendered[key]}")
    if result.optional:
        lines.append("# --- Optional ---")
        for key in result.optional:
            lines.append(f"{key}={result.rendered[key]}")
    lines.append("")
    return "\n".join(lines)
