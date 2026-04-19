"""Convert .env files between formats (dotenv, json, shell, yaml)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

SUPPORTED_FORMATS = ("dotenv", "json", "shell", "yaml")


class ConvertError(Exception):
    pass


@dataclass
class ConvertResult:
    source_format: str
    target_format: str
    env: Dict[str, str]
    output: str

    def summary(self) -> str:
        return (
            f"Converted {len(self.env)} key(s) "
            f"from {self.source_format} to {self.target_format}."
        )


def _to_dotenv(env: Dict[str, str]) -> str:
    lines = []
    for k, v in env.items():
        escaped = v.replace('"', '\\"')
        lines.append(f'{k}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def _to_json(env: Dict[str, str]) -> str:
    import json
    return json.dumps(env, indent=2) + "\n"


def _to_shell(env: Dict[str, str]) -> str:
    lines = []
    for k, v in env.items():
        escaped = v.replace('"', '\\"')
        lines.append(f'export {k}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def _to_yaml(env: Dict[str, str]) -> str:
    lines = []
    for k, v in env.items():
        safe_v = v.replace('"', '\\"')
        lines.append(f'{k}: "{safe_v}"')
    return "\n".join(lines) + ("\n" if lines else "")


_RENDERERS = {
    "dotenv": _to_dotenv,
    "json": _to_json,
    "shell": _to_shell,
    "yaml": _to_yaml,
}


def convert_env(
    env: Dict[str, str],
    target_format: str,
    source_format: str = "dotenv",
) -> ConvertResult:
    target_format = target_format.lower()
    if target_format not in SUPPORTED_FORMATS:
        raise ConvertError(
            f"Unsupported target format '{target_format}'. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    output = _RENDERERS[target_format](env)
    return ConvertResult(
        source_format=source_format,
        target_format=target_format,
        env=env,
        output=output,
    )
