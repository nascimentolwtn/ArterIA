import json
import subprocess
from pathlib import Path

import pytest

from arteria.network.osm_fetch import (
    OsmExtractError,
    OsmFetchError,
    default_geofabrik_url,
    download_source_pbf,
    extract_candidate_polygon,
    extract_osm,
)

STUDY_AREAS = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": "a", "name": "Candidate A"},
            "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]]},
        },
        {
            "type": "Feature",
            "properties": {"id": "B", "name": "Candidate B"},
            "geometry": {"type": "Polygon", "coordinates": [[[2, 2], [2, 3], [3, 3], [2, 2]]]},
        },
    ],
}


def test_default_geofabrik_url_is_the_sudeste_extract():
    assert (
        default_geofabrik_url()
        == "https://download.geofabrik.de/south-america/brazil/sudeste-latest.osm.pbf"
    )


def test_default_geofabrik_url_accepts_a_region_override():
    assert default_geofabrik_url("europe/germany") == (
        "https://download.geofabrik.de/europe/germany/sudeste-latest.osm.pbf"
    )


def test_download_source_pbf_calls_the_injected_download(tmp_path: Path):
    calls = []

    def fake_download(url: str, dest: Path) -> None:
        calls.append((url, dest))
        dest.write_bytes(b"fake-pbf-bytes")

    dest = tmp_path / "raw" / "sudeste-latest.osm.pbf"
    result = download_source_pbf("https://example.com/sudeste.pbf", dest, download=fake_download)

    assert result == dest
    assert dest.exists()
    assert dest.read_bytes() == b"fake-pbf-bytes"
    assert calls == [("https://example.com/sudeste.pbf", dest)]


def test_download_source_pbf_creates_parent_directory(tmp_path: Path):
    dest = tmp_path / "does" / "not" / "exist" / "yet.pbf"

    def fake_download(url: str, dest: Path) -> None:
        dest.write_bytes(b"x")

    download_source_pbf("https://example.com/x.pbf", dest, download=fake_download)

    assert dest.parent.is_dir()
    assert dest.exists()


def test_extract_candidate_polygon_matches_by_id(tmp_path: Path):
    path = tmp_path / "study-areas.geojson"
    path.write_text(json.dumps(STUDY_AREAS), encoding="utf-8")

    result = extract_candidate_polygon(path, "a")

    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 1
    assert result["features"][0]["properties"]["id"] == "a"


def test_extract_candidate_polygon_matches_case_insensitively(tmp_path: Path):
    path = tmp_path / "study-areas.geojson"
    path.write_text(json.dumps(STUDY_AREAS), encoding="utf-8")

    result = extract_candidate_polygon(path, "b")

    assert result["features"][0]["properties"]["id"] == "B"

    result_upper = extract_candidate_polygon(path, "A")
    assert result_upper["features"][0]["properties"]["id"] == "a"


def test_extract_candidate_polygon_all_returns_envelope_of_every_candidate(tmp_path: Path):
    path = tmp_path / "study-areas.geojson"
    path.write_text(json.dumps(STUDY_AREAS), encoding="utf-8")

    result = extract_candidate_polygon(path, "all")

    ring = result["features"][0]["geometry"]["coordinates"][0]
    xs = [pt[0] for pt in ring]
    ys = [pt[1] for pt in ring]
    all_pts = [pt for f in STUDY_AREAS["features"] for pt in f["geometry"]["coordinates"][0]]
    assert min(xs) == min(p[0] for p in all_pts)
    assert max(xs) == max(p[0] for p in all_pts)
    assert min(ys) == min(p[1] for p in all_pts)
    assert max(ys) == max(p[1] for p in all_pts)
    assert ring[0] == ring[-1]


def test_extract_candidate_polygon_raises_for_unknown_id_listing_available(tmp_path: Path):
    path = tmp_path / "study-areas.geojson"
    path.write_text(json.dumps(STUDY_AREAS), encoding="utf-8")

    with pytest.raises(OsmFetchError) as excinfo:
        extract_candidate_polygon(path, "nope")

    message = str(excinfo.value)
    assert "nope" in message
    assert "'a'" in message
    assert "'B'" in message


def test_extract_osm_raises_file_not_found_for_missing_pbf(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        extract_osm(
            pbf_path=tmp_path / "missing.osm.pbf",
            polygon_geojson=STUDY_AREAS,
            output_path=tmp_path / "out.osm.pbf",
            run=lambda cmd, **kwargs: subprocess.CompletedProcess(cmd, 0),
        )


def test_extract_osm_success_computes_sha256_and_builds_expected_command(tmp_path: Path):
    pbf_path = tmp_path / "source.osm.pbf"
    pbf_path.write_bytes(b"source-bytes")
    output_path = tmp_path / "out" / "clip.osm.pbf"

    captured_cmd = {}

    def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        captured_cmd["cmd"] = cmd
        captured_cmd["kwargs"] = kwargs
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"clipped-bytes")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    result = extract_osm(
        pbf_path=pbf_path,
        polygon_geojson=STUDY_AREAS,
        output_path=output_path,
        run=fake_run,
    )

    import hashlib

    assert result.sha256 == hashlib.sha256(b"clipped-bytes").hexdigest()
    assert result.output_path == str(output_path)

    cmd = captured_cmd["cmd"]
    assert cmd[0] == "osmium"
    assert cmd[1] == "extract"
    assert cmd[2] == "--polygon"
    # cmd[3] is the temp polygon file path
    assert cmd[4] == str(pbf_path)
    assert cmd[5] == "--output"
    assert cmd[6] == str(output_path)
    assert cmd[7] == "--overwrite"
    assert captured_cmd["kwargs"] == {"capture_output": True, "text": True}

    # the temp polygon file should have been cleaned up afterwards
    assert not Path(cmd[3]).exists()


def test_extract_osm_raises_on_nonzero_returncode_with_stderr(tmp_path: Path):
    pbf_path = tmp_path / "source.osm.pbf"
    pbf_path.write_bytes(b"source-bytes")
    output_path = tmp_path / "out.osm.pbf"

    def failing_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="osmium: bad polygon")

    with pytest.raises(OsmExtractError) as excinfo:
        extract_osm(
            pbf_path=pbf_path,
            polygon_geojson=STUDY_AREAS,
            output_path=output_path,
            run=failing_run,
        )

    assert "osmium: bad polygon" in str(excinfo.value)
