"""Archive an .env file with a timestamp-based filename."""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ArchiveResult:
    source: Path
    archive_path: Path
    timestamp: str
    size_bytes: int
    existed: bool  # True when the archive file already existed and was overwritten

    def summary(self) -> str:
        status = "overwritten" if self.existed else "created"
        return (
            f"Archived '{self.source}' -> '{self.archive_path}' "
            f"({self.size_bytes} bytes, {status}, ts={self.timestamp})"
        )


def _make_timestamp(dt: datetime | None = None) -> str:
    """Return a filesystem-safe UTC timestamp string."""
    if dt is None:
        dt = datetime.now(tz=timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def archive_env(
    source: Path | str,
    archive_dir: Path | str | None = None,
    *,
    suffix: str = ".bak",
    dt: datetime | None = None,
) -> ArchiveResult:
    """Copy *source* into *archive_dir* with a timestamp appended.

    Parameters
    ----------
    source:
        Path to the .env file to archive.
    archive_dir:
        Directory where the archive is written.  Defaults to the same
        directory as *source*.
    suffix:
        File suffix appended after the timestamp (default ``.bak``).
    dt:
        Override the current UTC time (useful in tests).
    """
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    archive_dir = Path(archive_dir) if archive_dir is not None else source.parent
    archive_dir.mkdir(parents=True, exist_ok=True)

    ts = _make_timestamp(dt)
    archive_name = f"{source.stem}.{ts}{suffix}"
    archive_path = archive_dir / archive_name

    existed = archive_path.exists()
    shutil.copy2(source, archive_path)

    return ArchiveResult(
        source=source,
        archive_path=archive_path,
        timestamp=ts,
        size_bytes=archive_path.stat().st_size,
        existed=existed,
    )
