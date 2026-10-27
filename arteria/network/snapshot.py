"""Pinned OSM snapshot (roadmap P2.1, ADR 0016).

`cities/<city>/network/osm-snapshot.yaml` records which regional PBF and which
clipped extracts a network build came from (URL, data timestamp from the PBF
header, size, sha256), so a rebuild can prove it starts from the same bytes.
Only metadata is committed; the PBFs stay in the gitignored `raw/` directory
(ADR 0004). Geofabrik's `*-latest` URL moves daily, so the sha256 of the
cached file, not the URL, is what pins the snapshot.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from arteria.data_safety import sha256_of

SNAPSHOT_FILENAME = "osm-snapshot.yaml"


class SnapshotMismatchError(RuntimeError):
    pass


class FileFingerprint(BaseModel):
    sha256: str
    size_bytes: int


class SourceSnapshot(FileFingerprint):
    file: str
    url: str
    data_timestamp: str | None = None  # from the PBF header, e.g. 2026-10-25T21:21:21Z


class ExtractSnapshot(FileFingerprint):
    file: str
    candidate: str


class NetReference(BaseModel):
    """The network a rebuild from this snapshot produced when it was pinned.
    `content_sha256` ignores netconvert's timestamp comment (`net_content_sha256`)."""

    content_sha256: str
    netconvert_version: str
    patches: list[str] = Field(default_factory=list)


class OsmSnapshot(BaseModel):
    city: str
    source: SourceSnapshot
    extracts: dict[str, ExtractSnapshot] = Field(default_factory=dict)
    network: NetReference | None = None


def fingerprint(path: Path) -> FileFingerprint:
    return FileFingerprint(sha256=sha256_of(path), size_bytes=path.stat().st_size)


def pbf_data_timestamp(
    path: Path, *, run: Callable[..., subprocess.CompletedProcess] = subprocess.run
) -> str | None:
    """Data timestamp from the PBF header (`osmium fileinfo`), or None if unavailable."""
    try:
        result = run(
            ["osmium", "fileinfo", "-g", "header.option.timestamp", str(path)],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def load_snapshot(path: Path) -> OsmSnapshot | None:
    if not path.exists():
        return None
    return OsmSnapshot.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def save_snapshot(snapshot: OsmSnapshot, path: Path) -> None:
    path.write_text(
        "# Pinned OSM snapshot (roadmap P2.1). Metadata only; the PBFs live in raw/ (gitignored).\n"
        "# Re-pin deliberately with `arteria osm fetch ... --update-snapshot`.\n"
        + yaml.safe_dump(snapshot.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )


def _check(label: str, path: Path, pinned: FileFingerprint) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    actual_size = path.stat().st_size
    actual_sha = None if actual_size != pinned.size_bytes else sha256_of(path)
    if actual_sha != pinned.sha256:
        raise SnapshotMismatchError(
            f"{label} {path} does not match the pinned OSM snapshot "
            f"(pinned sha256={pinned.sha256}, size={pinned.size_bytes}; "
            f"actual size={actual_size}"
            + (f", sha256={actual_sha}" if actual_sha else "")
            + "). Restore the pinned file, or re-pin on purpose with --update-snapshot."
        )


def verify_source(snapshot: OsmSnapshot, path: Path) -> None:
    _check("source PBF", path, snapshot.source)


def verify_extract(snapshot: OsmSnapshot, candidate: str, path: Path) -> None:
    pinned = snapshot.extracts.get(candidate)
    if pinned is None:
        raise SnapshotMismatchError(
            f"candidate {candidate!r} is not in the pinned OSM snapshot "
            f"(pinned: {', '.join(sorted(snapshot.extracts)) or 'none'}). "
            "Add it with --update-snapshot."
        )
    _check(f"extract {candidate!r}", path, pinned)
