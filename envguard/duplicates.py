from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    duplicates: Dict[str, List[int]] = field(default_factory=dict)  # key -> list of line numbers

    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.duplicates:
            return "No duplicate keys found."
        lines = []
        for key, linenos in self.duplicates.items():
            lines.append(f"  {key}: lines {', '.join(str(n) for n in linenos)}")
        return "Duplicate keys found:\n" + "\n".join(lines)


def find_duplicates(env_path: str) -> DuplicateResult:
    """Scan a .env file and report keys that appear more than once."""
    seen: Dict[str, List[int]] = {}
    with open(env_path, "r") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            if not key:
                continue
            seen.setdefault(key, []).append(lineno)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    return DuplicateResult(duplicates=duplicates)
