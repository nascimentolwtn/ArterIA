import json
import subprocess
from pathlib import Path

import pytest

from arteria.network.rebuild import RebuildError, rebuild_network
from arteria.network.snapshot import load_snapshot

FIXTURES = Path(__file__).parent / "fixtures"
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


def _setup(tmp_path: Path) -> Path:
    city_dir = tmp_path / "cities" / "toy"
    raw = city_dir / "network" / "raw"
    raw.mkdir(parents=True)
    (city_dir / "study-areas.geojson").write_text(json.dumps(STUDY_AREAS))
    (city_dir / "city.yaml").write_text("name: toy\ncrs: EPSG:32723\nsumo_version: '1.28.0'\n")
    (raw / "sudeste-latest.osm.pbf").write_bytes(b"source")
    return city_dir


def _run_factory(net_text: str):
    def run(cmd, **kwargs):
        if cmd[:2] == ["osmium", "extract"]:
            Path(cmd[cmd.index("--output") + 1]).write_bytes(b"clip")
        elif cmd[0] == "osmium" and cmd[1] == "cat":
            Path(cmd[cmd.index("-o") + 1]).write_text("<osm/>")
        elif cmd[0] == "netconvert" and "--version" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="Eclipse SUMO netconvert 1.28.0\n")
        elif cmd[0] == "netconvert":
            out = Path(cmd[cmd.index("--output-file") + 1])
            out.write_text(
                f"<?xml version='1.0'?>\n<!-- generated {out.name} {len(cmd)} -->\n{net_text}"
            )
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    return run


NET = (FIXTURES / "toy-net-valid.net.xml").read_text().split("\n", 1)[1]


def _rebuild(tmp_path: Path, city_dir: Path, net_text: str = NET, **kwargs):
    return rebuild_network(
        city="toy",
        city_dir=city_dir,
        repo_root=tmp_path,
        run=_run_factory(net_text),
        **kwargs,
    )


def test_rebuild_requires_a_pinned_snapshot_unless_updating(tmp_path: Path):
    city_dir = _setup(tmp_path)
    with pytest.raises(RebuildError, match="--update-snapshot"):
        _rebuild(tmp_path, city_dir)


def test_rebuild_pins_then_reproduces_then_flags_a_changed_net(tmp_path: Path):
    city_dir = _setup(tmp_path)
    # the fake clip is not the real envelope; pin it as the snapshot
    first = _rebuild(tmp_path, city_dir, update_snapshot=True)
    assert first.reproduced is None
    assert first.validation_blocking is False
    snapshot = load_snapshot(city_dir / "network" / "osm-snapshot.yaml")
    assert snapshot is not None and snapshot.network is not None
    assert snapshot.network.content_sha256 == first.content_sha256
    assert (Path(first.manifest_path)).exists()

    second = _rebuild(tmp_path, city_dir)
    assert second.reproduced is True
    assert second.diff_counts is not None
    assert all(v == {"added": 0, "removed": 0, "changed": 0} for v in second.diff_counts.values())

    changed = _rebuild(tmp_path, city_dir, net_text=NET.replace("13.89", "9.00"))
    assert changed.reproduced is False
    assert changed.diff_counts is not None and changed.diff_counts["lanes"]["changed"] == 1
