"""Snapshot current .env state to a JSON file for later comparison."""
from __future__ import annotations

import json
import datetime
from pathlib import Path
from typing import Dict, Optional

from envguard.parser import parse_env_file


class Snapshot:
    def __init__(self, env: Dict[str, str], source: str, timestamp: str):
        self.env = env
        self.source = source
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {"source": self.source, "timestamp": self.timestamp, "env": self.env}

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            env=data["env"],
            source=data["source"],
            timestamp=data["timestamp"],
        )


def take_snapshot(env_path: str) -> Snapshot:
    env = parse_env_file(env_path)
    timestamp = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return Snapshot(env=env, source=env_path, timestamp=timestamp)


def save_snapshot(snapshot: Snapshot, output_path: str) -> None:
    Path(output_path).write_text(json.dumps(snapshot.to_dict(), indent=2))


def load_snapshot(snapshot_path: str) -> Snapshot:
    data = json.loads(Path(snapshot_path).read_text())
    return Snapshot.from_dict(data)


def diff_with_snapshot(
    current_env_path: str, snapshot_path: str
) -> "envguard.differ.DiffResult":
    from envguard.differ import diff_envs

    snap = load_snapshot(snapshot_path)
    current = parse_env_file(current_env_path)
    return diff_envs(snap.env, current)
