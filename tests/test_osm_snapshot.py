import subprocess
from pathlib import Path

import pytest

from arteria.network.osm_fetch import fetch_candidate
from arteria.network.snapshot import SnapshotMismatchError, load_snapshot

STUDY_AREAS = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": "a"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
        }
    ],
}


def _city(tmp_path: Path) -> Path:
    import json

    city_dir = tmp_path / "cities" / "toy"
    (city_dir / "network" / "raw").mkdir(parents=True)
    (city_dir / "study-areas.geojson").write_text(json.dumps(STUDY_AREAS))
    return city_dir


def _fake_run(clip_bytes: bytes):
    def run(cmd, **kwargs):
        if cmd[:2] == ["osmium", "extract"]:
            Path(cmd[cmd.index("--output") + 1]).write_bytes(clip_bytes)
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        # osmium fileinfo -g header.option.timestamp
        return subprocess.CompletedProcess(cmd, 0, stdout="2026-01-02T03:04:05Z\n", stderr="")

    return run


def _fetch(city_dir: Path, source: Path, clip: bytes = b"clip-v1", **kwargs):
    return fetch_candidate(
        city="toy",
        city_dir=city_dir,
        candidate="a",
        pbf_path=source,
        source_url="https://example.test/region-latest.osm.pbf",
        run=_fake_run(clip),
        **kwargs,
    )


def test_first_fetch_pins_a_snapshot(tmp_path: Path):
    city_dir = _city(tmp_path)
    source = tmp_path / "region.osm.pbf"
    source.write_bytes(b"source-v1")

    _fetch(city_dir, source)

    snapshot = load_snapshot(city_dir / "network" / "osm-snapshot.yaml")
    assert snapshot is not None
    assert snapshot.source.size_bytes == len(b"source-v1")
    assert snapshot.source.data_timestamp == "2026-01-02T03:04:05Z"
    assert snapshot.extracts["a"].file == "toy-a.osm.pbf"


def test_second_fetch_with_same_bytes_passes(tmp_path: Path):
    city_dir = _city(tmp_path)
    source = tmp_path / "region.osm.pbf"
    source.write_bytes(b"source-v1")
    _fetch(city_dir, source)

    _fetch(city_dir, source)  # does not raise


def test_changed_source_fails_with_clear_message_and_keeps_the_pin(tmp_path: Path):
    city_dir = _city(tmp_path)
    source = tmp_path / "region.osm.pbf"
    source.write_bytes(b"source-v1")
    _fetch(city_dir, source)
    pinned = (city_dir / "network" / "osm-snapshot.yaml").read_text()

    source.write_bytes(b"source-v2")
    with pytest.raises(SnapshotMismatchError, match="--update-snapshot"):
        _fetch(city_dir, source)
    assert (city_dir / "network" / "osm-snapshot.yaml").read_text() == pinned


def test_changed_extract_fails(tmp_path: Path):
    city_dir = _city(tmp_path)
    source = tmp_path / "region.osm.pbf"
    source.write_bytes(b"source-v1")
    _fetch(city_dir, source)

    with pytest.raises(SnapshotMismatchError, match="extract 'a'"):
        _fetch(city_dir, source, clip=b"clip-v2")


def test_update_snapshot_repins(tmp_path: Path):
    city_dir = _city(tmp_path)
    source = tmp_path / "region.osm.pbf"
    source.write_bytes(b"source-v1")
    _fetch(city_dir, source)

    source.write_bytes(b"source-v2-longer")
    _fetch(city_dir, source, clip=b"clip-v2", update_snapshot=True)

    snapshot = load_snapshot(city_dir / "network" / "osm-snapshot.yaml")
    assert snapshot is not None
    assert snapshot.source.size_bytes == len(b"source-v2-longer")
    _fetch(city_dir, source, clip=b"clip-v2")  # now matches
