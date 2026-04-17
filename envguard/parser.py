"""Parser for .env files."""
import re
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_RE = re.compile(r'^\s*#.*$')


def parse_env_file(path: str) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    - Ignores blank lines and comments.
    - Strips inline comments after values.
    - Handles quoted values (single or double quotes).
    """
    result: Dict[str, Optional[str]] = {}

    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line.strip() or COMMENT_RE.match(line):
                continue
            match = ENV_LINE_RE.match(line)
            if match:
                key = match.group('key')
                value = match.group('value').strip()
                value = _strip_inline_comment(value)
                value = _unquote(value)
                result[key] = value

    return result


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comment from an unquoted value."""
    if value and value[0] not in ('"', "'"):
        idx = value.find(' #')
        if idx != -1:
            value = value[:idx].rstrip()
    return value


def _unquote(value: str) -> str:
    """Remove surrounding quotes from a value if present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
