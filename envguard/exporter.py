"""Export parsed env data to various formats (shell, JSON, dotenv)."""
from __future__ import annotations
import json
from typing import Dict

SUPPORTED_FORMATS = ("shell", "json", "dotenv")


class ExportError(ValueError):
    pass


def export_env(env: Dict[str, str], fmt: str) -> str:
    """Serialize *env* dict to the requested format string."""
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported format {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "json":
        return json.dumps(env, indent=2)
    if fmt == "shell":
        lines = []
        for key, value in env.items():
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'export {key}="{escaped}"')
        return "\n".join(lines)
    # dotenv
    lines = []
    for key, value in env.items():
        needs_quotes = any(c in value for c in (" ", "\t", "#", "'", '"'))
        if needs_quotes:
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)
